import pytest
from app.ai.math_solver import solve,equivalent

@pytest.mark.parametrize('question,result',[
 ('3x + 9 = 18','x = 3'),('x^2 - 5x + 6 = 0','x = 2; x = 3'),
 ('Differentiate x^3 + 2x','3*x^2 + 2'),('Integrate 2x','x^2 + C'),
 ('1/2 + 1/3','5/6'),('factor x^2 - 4','(x - 2)*(x + 2)'),
 ('substitute x^2 + 1 at x = 3','10'),('sin(pi/2)','1'),
 ('x + y = 5; x - y = 1','x = 3, y = 2'),('simplify 2x + 3x','5*x')])
def test_verified_math(question,result):
    answer=solve(question)
    assert answer['verified'] and answer['result']==result

@pytest.mark.parametrize('expression',["__import__('os').system('whoami') + 1",'x.__class__ + 1','[x for x in [1]]','2^999999','2^(2^8)','1/0','sin(sin(x))','(' * 90+'1'+')'*90,'x^8*x^8 = 2','1e999 + 2'])
def test_rejects_unsafe_and_excessive_math(expression):
    assert not solve(expression).get('verified',False)

def test_bilingual_steps_and_numeric_equivalence():
    result=solve('3x + 9 = 18','sw')
    assert 'Toa 9' in result['answer'] and 'Gawa kwa 3' in result['answer']
    assert equivalent('1/2','0.5') and not equivalent('x','x')
    assert not equivalent('__import__(1)','1')
    assert solve('I need to solve calculus') is None
