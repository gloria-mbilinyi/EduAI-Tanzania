from datetime import timedelta
import pytest
from app.core.database import now
from app.models import Subscription, Payment, ProviderTransaction
from app.services.billing import entitled

def checkout(c,h,scenario='success',handle='amina'):
    r=c.post('/api/billing/checkout',headers=h(handle),json={'plan_id':1,'demo_scenario':scenario})
    assert r.status_code==201
    return r.json()

def test_payment_verification_entitlement_receipt_and_idempotency(env):
    c,db,users,h=env
    assert not c.get('/api/billing',headers=h('amina')).json()['premium']
    p=checkout(c,h)
    assert not entitled(db,users['amina'].id)
    assert c.post(f'/api/payments/{p["id"]}/verify',headers=h('amina'),json={'success':True}).status_code==422
    r=c.post(f'/api/payments/{p["id"]}/verify',headers=h('amina'),json={})
    assert r.json()['status']=='verified' and entitled(db,users['amina'].id)
    expires=db.get(Subscription,p['subscription_id']).expires_at
    assert c.post(f'/api/payments/{p["id"]}/verify',headers=h('amina'),json={}).status_code==200
    assert db.get(Subscription,p['subscription_id']).expires_at==expires
    receipt=c.get(f'/api/payments/{p["id"]}/receipt',headers=h('amina'))
    assert receipt.status_code==200 and 'No real money' in receipt.text
    assert c.get(f'/api/payments/{p["id"]}/receipt',headers=h('juma')).status_code==403

@pytest.mark.parametrize('scenario',['failed','rejected'])
def test_unsuccessful_payments_never_entitle(env,scenario):
    c,db,users,h=env
    p=checkout(c,h,scenario)
    r=c.post(f'/api/payments/{p["id"]}/verify',headers=h('amina'),json={})
    assert r.json()['status']==scenario
    assert not entitled(db,users['amina'].id)
    assert c.get(f'/api/payments/{p["id"]}/receipt',headers=h('amina')).status_code==409

def test_amount_tampering_and_unrelated_verifier_denied(env):
    c,db,users,h=env
    p=checkout(c,h)
    assert c.post(f'/api/payments/{p["id"]}/verify',headers=h('juma'),json={}).status_code==403
    assert c.post(f'/api/payments/{p["id"]}/verify',headers=h('isolated'),json={}).status_code==404
    ledger=db.query(ProviderTransaction).filter_by(reference=p['provider_reference']).one()
    ledger.amount_tzs=1;db.commit()
    assert c.post(f'/api/payments/{p["id"]}/verify',headers=h('admin'),json={}).json()['status']=='rejected'
    assert not entitled(db,users['amina'].id)

def test_expiry_suspension_and_no_manual_activation_bypass(env):
    c,db,users,h=env
    p=checkout(c,h)
    sid=p['subscription_id']
    assert c.patch(f'/api/admin/subscriptions/{sid}',headers=h('admin'),json={'status':'active'}).status_code==409
    c.post(f'/api/payments/{p["id"]}/verify',headers=h('admin'),json={})
    c.patch(f'/api/admin/subscriptions/{sid}',headers=h('admin'),json={'status':'suspended'})
    assert not entitled(db,users['amina'].id)
    assert c.patch(f'/api/admin/subscriptions/{sid}',headers=h('admin'),json={'status':'active'}).status_code==200
    s=db.get(Subscription,sid);s.expires_at=now()-timedelta(days=1);db.commit()
    assert not c.get('/api/billing',headers=h('amina')).json()['premium']
    assert db.get(Subscription,sid).status=='expired'
    assert c.patch(f'/api/admin/subscriptions/{sid}',headers=h('admin'),json={'status':'active'}).status_code==409

def test_premium_tools_denied_after_expiry_or_unverified_payment(env):
    c,db,users,h=env
    s=db.query(Subscription).filter_by(user_id=users['neema'].id).one()
    s.expires_at=now()-timedelta(seconds=1);db.commit()
    body={'course_id':1,'topic':'Algebra'}
    assert c.post('/api/teacher-tools/quiz-draft',headers=h('neema'),json=body).status_code==402
    s.expires_at=now()+timedelta(days=5)
    db.query(Payment).filter_by(subscription_id=s.id).one().status='pending';db.commit()
    assert c.post('/api/teacher-tools/lesson-draft',headers=h('neema'),json=body).status_code==402

def test_demo_provider_can_be_disabled(env,monkeypatch):
    import app.api.billing as mod
    monkeypatch.setattr(mod,'DEMO_PAYMENTS',False)
    c,_,_,h=env
    assert c.post('/api/billing/checkout',headers=h('amina'),json={'plan_id':1}).status_code==503
