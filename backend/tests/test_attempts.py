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
    assert c.post(f'/submissions/{submissions[0].json()["id"]}/grade',headers=h('amina'),json={}).status_code!=200
    assert submit(c,h,aid,'isolated').status_code==404
    assert submit(c,h,aid,'neema').status_code==403

def test_default_limits_feedback_and_late_policy(env):
    c,db,_,h=env; aid=assignment(c,h,require_feedback=True)
    assert submit(c,h,aid).status_code==201
    assert submit(c,h,aid).status_code==409
    late=assignment(c,h,allow_late=True)
    db.get(Assignment,late).due_at=now()-timedelta(days=1);db.commit()
    assert submit(c,h,late).status_code==201
