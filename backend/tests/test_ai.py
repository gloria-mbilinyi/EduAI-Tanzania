from app.models import RecommendationApproval, Recommendation, TutorMessage, AuditLog

def test_pending_hidden_then_teacher_approval_publishes(env):
    c,db,users,h=env
    pending=c.post('/api/recommendations/generate',headers=h('amina'),json={'student_id':users['amina'].id,'course_id':1})
    assert pending.status_code==201
    ident=pending.json()['id']
    assert 'content' not in pending.json()
    assert ident not in [r['id'] for r in c.get('/api/recommendations',headers=h('amina')).json()]
    assert c.post(f'/api/recommendations/{ident}/review',headers=h('amina'),json={'decision':'approved','comment':'Self approval'}).status_code==403
    assert c.post(f'/api/recommendations/{ident}/review',headers=h('hamisi'),json={'decision':'approved','comment':'Wrong teacher'}).status_code==403
    assert c.post(f'/api/recommendations/{ident}/review',headers=h('neema'),json={'decision':'approved','comment':'Verified the evidence and activities.'}).status_code==200
    published=c.get('/api/recommendations',headers=h('amina')).json()
    item=next(x for x in published if x['id']==ident)
    assert '45' in ' '.join(item['reasons']) and 'Science' in item['content']
    assert c.post(f'/api/recommendations/{ident}/view',headers=h('juma')).status_code==404
    assert c.post(f'/api/recommendations/{ident}/view',headers=h('amina')).json()['status']=='viewed'
    assert db.query(RecommendationApproval).filter_by(recommendation_id=ident,decision='approved').count()==1

def test_rejection_regeneration_keeps_review_history(env):
    c,db,_,h=env
    assert c.post('/api/recommendations/1/review',headers=h('neema'),json={'decision':'rejected','comment':'Revise foundation exercises.'}).status_code==200
    assert c.post('/api/recommendations/1/review',headers=h('neema'),json={'decision':'approved','comment':'Cannot skip regeneration.'}).status_code==409
    r=c.post('/api/recommendations/1/regenerate',headers=h('neema'))
    assert r.json()['version']==2 and r.json()['status']=='pending_review'
    assert 1 not in [x['id'] for x in c.get('/api/recommendations',headers=h('amina')).json()]
    c.post('/api/recommendations/1/review',headers=h('neema'),json={'decision':'approved','comment':'Second draft is suitable.'})
    hist=c.get('/api/recommendations/1/history',headers=h('neema')).json()
    assert [x['decision'] for x in hist]==['rejected','approved']
    assert [x['version'] for x in hist]==[1,2]
    assert c.get('/api/recommendations/1/history',headers=h('amina')).status_code==403
    assert c.post('/api/recommendations/1/archive',headers=h('neema')).json()['status']=='archived'
    assert db.query(AuditLog).filter_by(action='recommendation.regenerated').count()==1

def test_recommendation_cross_student_and_school_denied(env):
    c,_,users,h=env
    for handle in ['juma','isolated']:
        assert c.post('/api/recommendations/generate',headers=h(handle),json={'student_id':users['amina'].id,'course_id':1}).status_code in (403,404)
    assert c.post('/api/recommendations/1/view',headers=h('amina')).status_code==404

def test_bilingual_retrieval_sources_history_and_no_match(env):
    c,db,_,h=env
    for lang,word in [('en','subtract'),('sw','toa')]:
        r=c.post('/api/tutor/ask',headers=h('amina'),json={'question':'Solve a linear equation mlinganyo','subject':'Mathematics','language':lang})
        assert r.status_code==200 and word in r.json()['answer'].lower()
        assert 'M01' in r.json()['source'] and 'not generative' in r.json()['mode']
    assert len(c.get('/api/tutor/history',headers=h('amina')).json())==2
    assert c.get('/api/tutor/history',headers=h('juma')).json()==[]
    no=c.post('/api/tutor/ask',headers=h('amina'),json={'question':'quantum entanglement','subject':'Mathematics','language':'en'}).json()
    assert no['source']=='No matching passage'
    assert c.post('/api/tutor/ask',headers=h('amina'),json={'question':'hi','subject':'Mathematics','language':'fr'}).status_code==422

def test_teacher_tools_are_entitled_drafts_and_persist_reviewed_lesson(env):
    c,db,_,h=env
    body={'course_id':1,'topic':'Linear equations'}
    q=c.post('/api/teacher-tools/quiz-draft',headers=h('neema'),json=body)
    assert q.status_code==200 and q.json()['status']=='draft'
    assert 'not generative' in q.json()['mode']
    assert c.post('/api/teacher-tools/quiz-draft',headers=h('amina'),json=body).status_code==403
    assert c.post('/api/teacher-tools/lesson-draft',headers=h('neema'),json={'course_id':3,'topic':'Force'}).status_code==403
    r=c.post('/api/teacher-tools/lesson-draft',headers=h('neema'),json=body)
    assert r.status_code==200 and 'Kiswahili' in r.json()['outline']
    assert c.post('/api/teacher-tools/lessons',headers=h('neema'),json={**body,'outline':r.json()['outline']}).status_code==201
    assert len(c.get('/api/teacher-tools/lessons/1',headers=h('neema')).json())==1
