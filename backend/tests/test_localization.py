from app.models import User,Notification

def test_language_preference_errors_reports_and_notifications(env):
    c,db,users,h=env
    headers=h('amina')|{'Accept-Language':'sw'}
    assert c.patch('/api/me/language',headers=headers,json={'language':'sw'}).json()['language']=='sw'
    assert c.get('/api/me',headers=h('amina')).json()['language']=='sw'
    error=c.post('/api/courses',headers=headers,json={'title':'New class','subject':'Math','form':'Form 2','description':''})
    assert error.status_code==403 and error.json()['detail']=='Jukumu halina ruhusa'
    invalid=c.patch('/api/me/language',headers=headers,json={'language':'xx'})
    assert 'Kagua' in invalid.json()['detail'][0]['msg']
    sid=users['amina'].id
    assert 'Tathmini' in c.get(f'/api/students/{sid}/performance',headers=headers).json()['summary']
    assert 'Namba ya mwanafunzi' in c.get(f'/api/students/{sid}/report.csv',headers=headers).text
    assert c.post('/api/submissions/1/grade',headers=h('neema'),json={'score':48,'feedback':'Review the steps'}).status_code==200
    assert db.query(Notification).filter_by(user_id=sid,title='Matokeo mapya ya masomo').count()==1
