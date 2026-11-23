import secrets
from datetime import timedelta
from typing import Literal
from pydantic import Field
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from ..core.database import get_db, now
from ..core.security import principal, require, role
from ..core.config import DEMO_PAYMENTS
from ..models import *
from ..schemas.common import Input
from ..services.access import *
from ..services.billing import entitled

router = APIRouter(prefix='/api', tags=['subscriptions'])

class Checkout(Input):
    plan_id: int = Field(gt=0)
    demo_scenario: Literal['success', 'failed', 'rejected'] = 'success'

@router.get('/plans')
def plans(db: Session = Depends(get_db)):
    return [record(p) for p in db.query(SubscriptionPlan).filter_by(active=True)]

@router.get('/billing')
def history(u: User = Depends(principal), db: Session = Depends(get_db)):
    result = []
    for s in db.query(Subscription).filter_by(user_id=u.id):
        if s.status == 'active' and s.expires_at and s.expires_at <= now(): s.status = 'expired'
        p = db.query(Payment).filter_by(subscription_id=s.id).first()
        result.append(record(s) | {'payment': record(p) if p else None, 'plan': db.get(SubscriptionPlan, s.plan_id).name})
    db.commit()
    return {'premium': entitled(db, u.id), 'subscriptions': result, 'provider': 'academic simulation; no real money'}

@router.post('/billing/checkout', status_code=201)
def checkout(data: Checkout, u: User = Depends(principal), db: Session = Depends(get_db)):
    if not DEMO_PAYMENTS: raise HTTPException(503, 'Demo provider disabled')
    plan = get(db, SubscriptionPlan, data.plan_id)
    if not plan.active: raise HTTPException(409, 'Plan unavailable')
    if plan.school_id is not None and plan.school_id != u.school_id: raise HTTPException(404, 'Plan unavailable')
    s = Subscription(user_id=u.id, plan_id=plan.id, premium=plan.premium)
    db.add(s)
    db.flush()
    reference = 'DEMO-' + secrets.token_hex(10)
    p = Payment(subscription_id=s.id, amount_tzs=plan.price_tzs, provider_reference=reference)
    db.add(ProviderTransaction(reference=reference, amount_tzs=plan.price_tzs, currency='TZS', outcome=data.demo_scenario))
    save(db, u, p, 'payment.demo_initiated')
    return record(p)

class Verify(Input):
    pass

@router.post('/payments/{payment_id}/verify')
def verify(payment_id: int, data: Verify, u: User = Depends(principal), db: Session = Depends(get_db)):
    if not DEMO_PAYMENTS: raise HTTPException(503, 'Demo provider disabled')
    p = get(db, Payment, payment_id)
    s = get(db, Subscription, p.subscription_id)
    owner = get(db, User, s.user_id)
    same_school(u, owner)
    if u.id != owner.id and role(db, u) != 'admin': raise HTTPException(403, 'Payment access denied')
    if p.status != 'pending': return record(p)
    if s.status != 'pending_payment': raise HTTPException(409, 'Subscription no longer pending')
    provider = db.query(ProviderTransaction).filter_by(reference=p.provider_reference).first()
    valid = provider and provider.outcome == 'success' and provider.amount_tzs == p.amount_tzs and provider.currency == p.currency
    if valid:
        p.status, p.verified_at = 'verified', now()
        s.status, s.expires_at = 'active', now() + timedelta(days=get(db, SubscriptionPlan, s.plan_id).days)
    else:
        p.status = 'failed' if provider and provider.outcome == 'failed' else 'rejected'
        s.status = 'payment_' + p.status
    db.add(s)
    save(db, u, p, 'payment.verify',)
    return record(p)

@router.get('/payments/{payment_id}/receipt', response_class=PlainTextResponse)
def receipt(payment_id: int, u: User = Depends(principal), db: Session = Depends(get_db)):
    p = get(db, Payment, payment_id)
    s = get(db, Subscription, p.subscription_id)
    if s.user_id != u.id: raise HTTPException(403, 'Receipt access denied')
    if p.status != 'verified': raise HTTPException(409, 'Payment has not been verified')
    return f'EduAI Tanzania DEMONSTRATION RECEIPT\nNo real money transferred\nReference: {p.provider_reference}\nAmount: TZS {p.amount_tzs}\nVerified: {p.verified_at.isoformat()} UTC\nExpires: {s.expires_at.isoformat()} UTC\n'
