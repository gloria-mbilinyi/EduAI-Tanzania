import pytest
from app.services.performance import risk_assessment
from conftest import PASSWORD

@pytest.mark.parametrize('average,activities,expected',[(None,0,'insufficient_data'),(49.9,4,'high'),(50,4,'moderate'),(65,0,'moderate'),(65,2,'low')])
def test_explainable_risk_boundaries(average,activities,expected):
    result=risk_assessment(average,activities,3 if average is not None else 0)
    assert result['level']==expected and result['reasons']
    assert 'not a trained' in result['mode']

def test_parent_self_registration_creates_restricted_account(env):
    c,_,_,_=env
    r=c.post('/api/auth/register',json={'name':'Fictional Parent','email':'newparent@demo.eduai.test','password':PASSWORD,'school_id':1,'role':'parent','language':'sw'})
    assert r.status_code==201
    login=c.post('/api/auth/login',json={'email':'newparent@demo.eduai.test','password':PASSWORD})
    headers={'Authorization':'Bearer '+login.json()['access_token']}
    assert c.get('/api/parent/links',headers=headers).json()==[]
    assert c.get('/api/students/3/performance',headers=headers).status_code==403
