import io
from datetime import timedelta
from app.models import Assignment, Grade, Notification
from app.core.database import now

def test_course_assignment_permissions_and_scope(env):
    c,_,_,h=env
    assert len(c.get('/api/courses',headers=h('neema')).json())==2
    assert c.get('/api/courses/3/materials',headers=h('neema')).status_code==403
    assert c.get('/api/courses/4/materials',headers=h('amina')).status_code==404
    data={'title':'New chemistry course','subject':'Chemistry','form':'Form 2','description':'Lab concepts'}
    assert c.post('/api/courses',headers=h('amina'),json=data).status_code==403
    r=c.post('/api/courses',headers=h('neema'),json=data)
    assert r.status_code==201
    assert c.patch(f'/api/courses/{r.json()["id"]}',headers=h('neema'),json={**data,'title':'Updated chemistry'}).status_code==200
    assert c.patch('/api/courses/3',headers=h('neema'),json=data).status_code==403

def test_materials_upload_download_and_validation(env,tmp_path,monkeypatch):
    import app.api.courses as mod
    monkeypatch.setattr(mod,'UPLOADS',tmp_path)
    c,_,_,h=env
    r=c.post('/api/courses/1/upload',headers=h('neema'),data={'title':'A study note'},files={'file':('notes.txt',b'Linear equations')})
    assert r.status_code==201
    ident=r.json()['id']
    assert c.get(f'/api/materials/{ident}/download',headers=h('amina')).content==b'Linear equations'
    assert c.get(f'/api/materials/{ident}/download',headers=h('isolated')).status_code==404
    assert c.post('/api/courses/1/upload',headers=h('neema'),data={'title':'Bad file'},files={'file':('evil.html',b'<script>')}).status_code==422
    assert c.post('/api/courses/1/materials',headers=h('neema'),json={'title':'Unsafe link','url':'http://example.com'}).status_code==422
    r=c.post('/api/courses/1/materials',headers=h('neema'),json={'title':'Lesson video','kind':'video','url':'https://example.com/lesson'})
    assert r.status_code==201

def test_assignment_submission_grading_and_alerts(env):
    c,db,users,h=env
    r=c.post('/api/courses/1/assignments',headers=h('neema'),json={'title':'New exercise','instructions':'Show your complete solution.'})
    aid=r.json()['id']
    sub=c.post(f'/api/assignments/{aid}/submit',headers=h('amina'),json={'body':'I subtracted six from both sides.'})
    assert sub.status_code==201
    sid=sub.json()['id']
    assert c.post(f'/api/assignments/{aid}/submit',headers=h('amina'),json={'body':'Again'}).status_code==409
    assert c.get(f'/api/assignments/{aid}/submissions',headers=h('juma')).status_code==403
    assert c.post(f'/api/submissions/{sid}/grade',headers=h('amina'),json={'score':100,'feedback':'Give me marks'}).status_code==403
    assert c.post(f'/api/submissions/{sid}/grade',headers=h('hamisi'),json={'score':70,'feedback':'Good work'}).status_code==403
    assert c.post(f'/api/submissions/{sid}/grade',headers=h('neema'),json={'score':72,'feedback':'Explain the final division.'}).status_code==200
    assert db.query(Grade).filter_by(submission_id=sid).one().score==72
    assert db.query(Notification).filter_by(user_id=users['parent'].id,title='New academic result').count()==1
    report=c.get(f'/api/students/{users["amina"].id}/performance',headers=h('amina')).json()
    assert any(r['score']==72 for x in report['courses'] for r in x['results'])
    assert c.get(f'/api/students/{users["amina"].id}/report.csv',headers=h('parent')).status_code==200

def test_late_assignment_denied(env):
    c,db,_,h=env
    a=Assignment(course_id=1,title='Expired work',instructions='Past deadline',due_at=now()-timedelta(days=1))
    db.add(a);db.commit()
    assert c.post(f'/api/assignments/{a.id}/submit',headers=h('amina'),json={'body':'late'}).status_code==409

def test_objective_quiz_hides_keys_validates_and_grades(env):
    c,_,_,h=env
    data=c.get('/api/quizzes/1',headers=h('amina')).json()
    assert all('correct_index' not in q and 'explanation' not in q for q in data['questions'])
    assert c.post('/api/quizzes/1/attempt',headers=h('amina'),json={'answers':{}}).status_code==422
    teacher=c.get('/api/quizzes/1',headers=h('neema')).json()
    answers={str(q['id']):q['correct_index'] for q in teacher['questions']}
    assert c.post('/api/quizzes/1/attempt',headers=h('amina'),json={'answers':{**answers,'999':0}}).status_code==422
    r=c.post('/api/quizzes/1/attempt',headers=h('amina'),json={'answers':answers})
    assert r.status_code==201 and r.json()['score']==100
    assert c.post('/api/quizzes/1/attempt',headers=h('amina'),json={'answers':answers}).status_code==409

def test_teacher_quiz_draft_and_question_validation(env):
    c,_,_,h=env
    quiz={'title':'Draft assessment','status':'draft','questions':[{'prompt':'Which number is even?','options':['2','3'],'correct_index':0,'explanation':'Two is divisible by two.'}]}
    r=c.post('/api/courses/1/quizzes',headers=h('neema'),json=quiz)
    assert r.status_code==201
    assert c.get(f'/api/quizzes/{r.json()["id"]}',headers=h('amina')).status_code==404
    quiz['questions'][0]['correct_index']=9
    assert c.post('/api/courses/1/quizzes',headers=h('neema'),json=quiz).status_code==422

def test_teacher_performance_excludes_unassigned_subjects(env):
    c,_,users,h=env
    r=c.get(f'/api/students/{users["amina"].id}/performance',headers=h('neema'))
    assert r.status_code==200
    assert {x['subject'] for x in r.json()['courses']}=={'Mathematics','Biology'}
