from app.models import Grade

def test_reviewed_publication_and_numeric_symbolic_grading(env):
    c,_,_,h=env
    body={'title':'Equivalent fractions','status':'published','questions':[{'prompt':'Calculate 1/2 + 1/4','kind':'numerical','answer':'3/4','explanation':'Use a common denominator.'}]}
    assert c.post('/api/courses/1/quizzes',headers=h('neema'),json=body).status_code==422
    body['reviewed']=True
    q=c.post('/api/courses/1/quizzes',headers=h('neema'),json=body).json()
    detail=c.get(f'/api/quizzes/{q["id"]}',headers=h('amina')).json()
    assert all('answer' not in x and 'correct_index' not in x for x in detail['questions'])
    qid=detail['questions'][0]['id']
    r=c.post(f'/api/quizzes/{q["id"]}/attempt',headers=h('amina'),json={'answers':{str(qid):'0.75'}})
    assert r.status_code==201 and r.json()['score']==100
    assert c.post(f'/api/quiz-submissions/{r.json()["submission_id"]}/grade',headers=h('neema'),json={'marks':{str(qid):0},'feedback':'Override'}).status_code==409

def test_short_answer_waits_for_assigned_teacher_and_objective_marks_cannot_change(env):
    c,db,_,h=env
    body={'title':'Mixed quiz','questions':[{'prompt':'Is two even?','kind':'true_false','options':['True','False'],'correct_index':0,'explanation':'Two divides by two.'},{'prompt':'Explain your method.','kind':'short_answer','answer':'A clear mathematical argument','explanation':'Teacher assesses reasoning.'}]}
    q=c.post('/api/courses/1/quizzes',headers=h('neema'),json=body).json();path=f'/api/quizzes/{q["id"]}'
    assert c.post(path+'/publish',headers=h('amina'),json={'reviewed':True}).status_code==403
    assert c.post(path+'/publish',headers=h('neema'),json={'reviewed':True}).status_code==200
    questions=c.get(path,headers=h('amina')).json()['questions'];short=questions[1]['id']
    r=c.post(path+'/attempt',headers=h('amina'),json={'answers':{str(questions[0]['id']):0,str(short):'It divides exactly by two.'}}).json()
    sid=r['submission_id'];assert r['score'] is None and db.query(Grade).filter_by(submission_id=sid).first() is None
    mark=f'/api/quiz-submissions/{sid}/grade';data={'marks':{str(short):80},'feedback':'Reasoning is correct'}
    assert c.post(mark,headers=h('hamisi'),json=data).status_code==403
    assert c.post(mark,headers=h('amina'),json=data).status_code==403
    assert c.post(mark,headers=h('neema'),json=data).json()['score']==90

def test_bank_drafts_types_language_limits_and_no_auto_publication(env):
    c,_,_,h=env
    for kind in ['mcq','true_false','short_answer','numerical']:
        r=c.post('/api/teacher-tools/quiz-draft',headers=h('neema'),json={'course_id':1,'topic':'Linear equations','count':3,'kind':kind,'language':'sw','use_local_ai':True})
        assert r.status_code==200,r.text
        assert r.json()['status']=='draft'
        assert all(q['kind']==kind and q['language']=='sw' for q in r.json()['questions'])
    assert c.post('/api/teacher-tools/quiz-draft',headers=h('neema'),json={'course_id':1,'topic':'Linear equations','count':999}).status_code==422

def test_local_quiz_schema_validates_drafts_without_writing_marks(env,monkeypatch):
    from app.ai import ollama
    c,db,_,h=env;before=db.query(Grade).count()
    monkeypatch.setattr(ollama,'generate',lambda *a,**k:{'questions':[{'prompt':'Calculate one half plus one half.','kind':'numerical','answer':'1','explanation':'Two halves make one whole.','language':'en'}]})
    body={'course_id':1,'topic':'Fractions','kind':'numerical','count':1,'use_local_ai':True}
    response=c.post('/api/teacher-tools/quiz-draft',headers=h('neema'),json=body)
    assert response.status_code==200 and response.json()['mode'].startswith('Ollama generated')
    assert db.query(Grade).count()==before
    monkeypatch.setattr(ollama,'generate',lambda *a,**k:{'questions':[{'prompt':'Calculate one half plus one half.','kind':'numerical','answer':'__import__(1)','explanation':'Unsafe key','language':'en'}]})
    fallback=c.post('/api/teacher-tools/quiz-draft',headers=h('neema'),json=body).json()
    assert 'bank fallback' in fallback['warning'] and not fallback['mode'].startswith('Ollama')
