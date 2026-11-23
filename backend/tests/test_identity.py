import pytest
import jwt
from datetime import timedelta
from app.models import User, Student
from app.core.security import verify_password
from app.core.database import now
from app.core.config import JWT_SECRET
from conftest import PASSWORD

def registration(**extra):
    return {'email':'new@demo.eduai.test','name':'New Demo','password':PASSWORD,'school_id':1,'role':'student',**extra}

def test_login_and_password_hash(env):
    c,db,users,h=env
    r=c.post('/api/auth/login',json={'email':users['amina'].email,'password':PASSWORD})
    assert r.status_code==200
    assert 'password_hash' not in r.text
    assert verify_password(PASSWORD,users['amina'].password_hash)
    assert users['amina'].password_hash!=PASSWORD
    assert c.get('/api/me',headers={'Authorization':'Bearer '+r.json()['access_token']}).json()['id']==users['amina'].id

def test_invalid_authentication(env):
    c,_,_,_=env
    assert c.get('/api/me').status_code==401
    assert c.get('/api/me',headers={'Authorization':'Bearer invalid'}).status_code==401
    assert c.post('/api/auth/login',json={'email':'unknown@test.test','password':PASSWORD}).status_code==401

def test_expired_jwt(env):
    c,_,users,_=env
    expired=jwt.encode({'sub':str(users['amina'].id),'iat':now()-timedelta(days=2),'exp':now()-timedelta(days=1)},JWT_SECRET,algorithm='HS256')
    assert c.get('/api/me',headers={'Authorization':'Bearer '+expired}).status_code==401

def test_registration_school_profile_and_duplicates(env):
    c,db,_,_=env
    r=c.post('/api/auth/register',json=registration())
    assert r.status_code==201
    assert db.get(Student,r.json()['user']['id'])
    assert c.post('/api/auth/register',json=registration()).status_code==409
    assert c.post('/api/auth/register',json=registration(email='missing@demo.test',school_id=999)).status_code==404

@pytest.mark.parametrize('extra',[{'role':'admin'},{'school_id':0},{'password':'short'},{'email':'bad'},{'unexpected':True}])
def test_registration_validation(env,extra):
    c,*_=env
    assert c.post('/api/auth/register',json=registration(**extra)).status_code==422

def test_teacher_requires_activation(env):
    c,_,_,h=env
    r=c.post('/api/auth/register',json=registration(role='teacher'))
    ident=r.json()['user']['id']
    assert not r.json()['user']['active']
    assert c.post('/api/auth/login',json={'email':'new@demo.eduai.test','password':PASSWORD}).status_code==401
    assert c.patch(f'/api/admin/users/{ident}',headers=h('admin'),json={'active':True}).status_code==200
    assert c.post('/api/auth/login',json={'email':'new@demo.eduai.test','password':PASSWORD}).status_code==200

def test_profile_language_and_no_role_escalation(env):
    c,_,_,h=env
    data={'name':'Amina Updated','language':'sw','interests':'Engineering','preference':'practice'}
    assert c.patch('/api/me',headers=h('amina'),json=data).json()['profile']['interests']=='Engineering'
    assert c.get('/api/me',headers=h('amina')).json()['language']=='sw'
    assert c.patch('/api/me',headers=h('amina'),json={**data,'role':'admin'}).status_code==422
    assert c.get('/api/admin/users',headers=h('amina')).status_code==403

def test_disabled_user_existing_token_denied(env):
    c,_,users,h=env
    old=h('amina')
    c.patch(f'/api/admin/users/{users["amina"].id}',headers=h('admin'),json={'active':False})
    assert c.get('/api/me',headers=old).status_code==401
