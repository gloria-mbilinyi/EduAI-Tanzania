import pytest
from conftest import PASSWORD
from app.models import LearningActivity

@pytest.mark.parametrize('handle',['amina','neema','parent','admin'])
def test_all_four_roles_login_and_load_protected_identity(env,handle):
    c,_,users,_=env
    r=c.post('/api/auth/login',json={'email':users[handle].email,'password':PASSWORD})
    assert r.status_code==200
    me=c.get('/api/me',headers={'Authorization':'Bearer '+r.json()['access_token']})
    assert me.status_code==200 and me.json()['id']==users[handle].id

def test_reading_materials_is_read_only_and_study_is_explicit(env):
    c,db,users,h=env
    before=db.query(LearningActivity).count()
    items=c.get('/api/courses/1/materials',headers=h('amina')).json()
    c.get('/api/courses/1/materials',headers=h('amina'))
    assert db.query(LearningActivity).count()==before
    ident=items[0]['id']
    assert c.post(f'/api/materials/{ident}/study',headers=h('amina')).status_code==201
    assert db.query(LearningActivity).count()==before+1
    assert c.post(f'/api/materials/{ident}/study',headers=h('isolated')).status_code==404
    assert c.post(f'/api/materials/{ident}/study',headers=h('neema')).status_code==403
