import pytest
from app.ai.tutor import answer,retrieve

@pytest.mark.parametrize('subject,question,source',[('Mathematics','I need to solve calculus','M04'),('Biology','Explain respiration','B03'),('Physics','electric circuit','P02'),('Chemistry','atomic structure','C02'),('Geography','map reading','G02'),('History','trade','H02'),('English','reading comprehension','E02'),('Kiswahili','nyakati za vitenzi','S02')])
def test_topic_matching(subject,question,source):
    result=answer(question,subject,'en')
    assert source in result['source']
    assert 'M01' not in result['source']

def test_context_language_math_history_and_privacy(env):
    c,db,_,h=env
    ask=lambda q,lang='en':c.post('/api/tutor/ask',headers=h('amina'),json={'question':q,'subject':'Mathematics','language':lang})
    assert ask('3x + 9 = 18').json()['result']=='x = 3'
    assert ask('Explain calculus','sw').json()['language']=='sw'
    assert 'M04' in ask('Explain that again').json()['source']
    assert ask('Explain calculus in English','sw').json()['language']=='en'
    assert len(c.get('/api/tutor/history',headers=h('amina')).json())==4
    assert c.get('/api/tutor/history',headers=h('juma')).json()==[]
    assert retrieve('quantum entanglement','Mathematics')[0]<0.15
