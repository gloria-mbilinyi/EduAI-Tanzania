from datetime import timedelta
from app.core.database import now
from app.models import Grade, Submission, Assignment

def assignment(c,h,**policy):
    r=c.post('/api/courses/1/assignments',headers=h('neema'),json={'title':'Three attempts','instructions':'Show your working clearly.','policy':{'max_attempts':3,'allow_resubmission':True,**policy}})
    assert r.status_code==201, r.text
    return r.json()['id']

def submit(c,h,aid,who='amina'):
    return c.post(f'/api/assignments/{aid}/submit',headers=h(who),json={'body':'My worked solution'})

def test_three_attempts_limits_history_and_no_student_grading(env):
    c,db,_,h=env; aid=assignment(c,h)
    submissions=[submit(c,h,aid) for _ in range(3)]
    assert all(r.status_code==201 for r in submissions)
    assert [r.json()['attempt_number'] for r in submissions]==[1,2,3]
    assert len({r.json()['id'] for r in submissions})==1
    assert submit(c,h,aid).status_code==409
    row=next(a for a in c.get('/api/courses/1/assignments',headers=h('amina')).json() if a['id']==aid)
    assert len(row['attempts'])==3 and row['remaining_attempts']==0
    assert c.post(f'/api/submissions/{submissions[0].json()["id"]}/grade',headers=h('amina'),json={'score':100,'feedback':'Fake marks'}).status_code==403
    assert submit(c,h,aid,'isolated').status_code==404
    assert submit(c,h,aid,'neema').status_code==403

def test_default_limits_feedback_and_late_policy(env):
    c,db,_,h=env; aid=assignment(c,h,require_feedback=True)
    assert submit(c,h,aid).status_code==201
    assert submit(c,h,aid).status_code==409
    late=assignment(c,h,allow_late=True)
    db.get(Assignment,late).due_at=now()-timedelta(days=1);db.commit()
    assert submit(c,h,late).status_code==201

def test_grading_history_approval_reopen_and_selection(env):
    c,db,users,h=env;aid=assignment(c,h,require_approval=True,require_feedback=True,grading_policy='selected')
    first=submit(c,h,aid).json(); at1=first['attempt_id']
    def grade(at,score):return c.post(f'/api/attempts/{at}/grade',headers=h('neema'),json={'score':score,'feedback':f'Feedback for {score}'})
    assert grade(at1,45).status_code==200
    assert submit(c,h,aid).status_code==409
    request=c.post(f'/api/assignments/{aid}/resubmission-requests',headers=h('amina'),json={'reason':'I revised my working'}).json()
    path=f'/api/resubmission-requests/{request["id"]}/review'
    assert c.post(path,headers=h('hamisi'),json={'decision':'approved','comment':'Try again'}).status_code==403
    assert c.post(path,headers=h('neema'),json={'decision':'approved','comment':'Try again'}).status_code==200
    second=submit(c,h,aid).json();assert grade(second['attempt_id'],80).status_code==200
    assert grade(second['attempt_id'],81).status_code==200
    assert db.query(Grade).filter_by(submission_id=first['id']).one().score==45
    assert c.post(f'/api/attempts/{second["attempt_id"]}/select-final',headers=h('neema')).status_code==200
    hist=c.get(f'/api/assignments/{aid}/history',headers=h('amina')).json()
    assert hist['official']['grade']['score']==81 and len(hist['feedback_history'])==3
    assert c.get(f'/api/assignments/{aid}/history?student_id={users["amina"].id}',headers=h('juma')).status_code==403
    assert c.get(f'/api/assignments/{aid}/history?student_id={users["amina"].id}',headers=h('parent')).status_code==200
    db.get(Assignment,aid).due_at=now()-timedelta(days=1);db.commit()
    assert c.post(f'/api/assignments/{aid}/reopen',headers=h('neema'),json={'student_id':users['amina'].id,'reason':'One more try','reopen_until':(now()+timedelta(days=1)).isoformat()}).status_code==201
    third=submit(c,h,aid);assert third.status_code==201
    assert grade(third.json()['attempt_id'],100).status_code==200
    assert submit(c,h,aid).status_code==409
