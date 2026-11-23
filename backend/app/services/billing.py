from fastapi import HTTPException
from ..models import Subscription, Payment
from ..core.database import now

def entitled(db, user_id):
    for s in db.query(Subscription).filter_by(user_id=user_id, status='active', premium=True):
        if not s.expires_at or s.expires_at <= now(): continue
        if db.query(Payment).filter_by(subscription_id=s.id, status='verified').first(): return True
    return False

def premium(db, user_id):
    if not entitled(db, user_id): raise HTTPException(402, 'Verified active premium subscription required')
