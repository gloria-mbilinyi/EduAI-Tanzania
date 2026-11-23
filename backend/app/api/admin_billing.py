from typing import Literal
from pydantic import Field
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..core.database import get_db, now
from ..models import *
from ..schemas.common import Input
from ..services.access import *
from .admin import admin

router = APIRouter(prefix='/api/admin', tags=['billing administration'])
class PlanInput(Input):
    name: str = Field(min_length=3, max_length=80)
    price_tzs: int = Field(gt=0, le=10000000)
    days: int = Field(gt=0, le=366)
    premium: bool = True
    active: bool = True

@router.get('/plans')
def plans(u: User = Depends(admin), db: Session = Depends(get_db)):
    return [record(p) for p in db.query(SubscriptionPlan).filter(or_(SubscriptionPlan.school_id == None, SubscriptionPlan.school_id == u.school_id))]

@router.post('/plans', status_code=201)
def create_plan(data: PlanInput, u: User = Depends(admin), db: Session = Depends(get_db)):
    return record(save(db, u, SubscriptionPlan(school_id=u.school_id, **data.model_dump()), 'admin.plan_created'))

@router.patch('/plans/{plan_id}')
def edit_plan(plan_id: int, data: PlanInput, u: User = Depends(admin), db: Session = Depends(get_db)):
    p = get(db, SubscriptionPlan, plan_id)
    if p.school_id != u.school_id: raise HTTPException(403, 'Shared plans are managed out of band')
    for k, v in data.model_dump().items(): setattr(p, k, v)
    return record(save(db, u, p, 'admin.plan_updated'))

@router.get('/subscriptions')
def subscriptions(u: User = Depends(admin), db: Session = Depends(get_db)):
    result = []
    for s in db.query(Subscription).join(User, User.id == Subscription.user_id).filter(User.school_id == u.school_id):
        if s.status == 'active' and s.expires_at and s.expires_at <= now(): s.status = 'expired'
        p = db.query(Payment).filter_by(subscription_id=s.id).first()
        result.append(record(s) | {'user_name': db.get(User, s.user_id).name, 'payment': record(p) if p else None})
    db.commit()
    return result

class SubscriptionAction(Input):
    status: Literal['active', 'suspended', 'cancelled']

@router.patch('/subscriptions/{subscription_id}')
def status(subscription_id: int, data: SubscriptionAction, u: User = Depends(admin), db: Session = Depends(get_db)):
    s = get(db, Subscription, subscription_id)
    same_school(u, get(db, User, s.user_id))
    if s.status == 'cancelled': raise HTTPException(409, 'Cancelled subscriptions require new checkout')
    if data.status == 'active':
        verified = db.query(Payment).filter_by(subscription_id=s.id, status='verified').first()
        if not verified or not s.expires_at or s.expires_at <= now(): raise HTTPException(409, 'Verified unexpired payment is required')
    s.status = data.status
    return record(save(db, u, s, 'admin.subscription_' + data.status))
