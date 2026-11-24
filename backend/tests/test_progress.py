import pytest
from app.models import AssignmentPolicy, Recommendation
from app.ai.recommendations import generate

@pytest.mark.parametrize('policy,expected',[('first',45),('best',100),('latest',100),('selected',None)])
def test_official_policy_counts_assignment_once(env,policy,expected):
    c,db,users,h=env
    db.add(AssignmentPolicy(assignment_id=1,max_attempts=3,allow_resubmission=True,grading_policy=policy));db.commit()
    for score in [80,100]:
        s=c.post('/api/assignments/1/submit',headers=h('amina'),json={'body':'An improved answer'}).json()
        assert c.post(f'/api/attempts/{s["attempt_id"]}/grade',headers=h('neema'),json={'score':score,'feedback':'Improved calculation steps'}).status_code==200
    course=next(x for x in c.get(f'/api/students/{users["amina"].id}/performance',headers=h('amina')).json()['courses'] if x['course_id']==1)
    assert course['average']==expected
    if expected is not None:
        assert len(course['results'])==1 and course['results'][0]['improvement']==55

def test_pathways_follow_progress_and_keep_immutable_versions(env):
    c,db,users,h=env;sid=users['amina'].id
    db.add(AssignmentPolicy(assignment_id=1,max_attempts=3,allow_resubmission=True,grading_policy='best'));db.commit()
    assert 'foundation' in generate(db,sid,1)[0]
    old=db.get(Recommendation,1).content
    for score,word in [(80,'intermediate'),(100,'advanced')]:
        s=c.post('/api/assignments/1/submit',headers=h('amina'),json={'body':'Revised solution'}).json()
        c.post(f'/api/attempts/{s["attempt_id"]}/grade',headers=h('neema'),json={'score':score,'feedback':'Show all calculation steps'})
        content,reasons=generate(db,sid,1)
        assert word in content and any(str(score) in r for r in reasons)
        assert db.get(Recommendation,1).status=='pending_review'
    c.post('/api/recommendations/1/review',headers=h('neema'),json={'decision':'rejected','comment':'Update the evidence'})
    c.post('/api/recommendations/1/regenerate',headers=h('neema'))
    versions=c.get('/api/recommendations/1/versions',headers=h('neema')).json()
    assert [v['version'] for v in versions]==[1,2] and versions[0]['content']==old
    assert 'advanced' in versions[1]['content']
    assert c.get('/api/recommendations/1/versions',headers=h('amina')).status_code==403
