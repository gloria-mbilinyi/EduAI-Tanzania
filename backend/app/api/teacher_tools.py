from pydantic import Field
from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import principal
from ..models import User, Lesson
from ..schemas.common import Input
from ..services.access import course_access, save, record
from ..services.billing import premium
from ..ai.corpus import CORPUS
from ..ai.tutor import retrieve
from ..ai.quiz_builder import draft as build_quiz
from .quizzes import QuestionInput

router = APIRouter(prefix='/api/teacher-tools', tags=['teacher draft assistance'])
class Draft(Input):
    course_id: int = Field(gt=0)
    topic: str = Field(min_length=3, max_length=150)

class QuizDraft(Draft):
    subject:str|None=None
    objective:str=Field(default='Understand and apply the selected topic',min_length=5,max_length=500)
    difficulty:Literal['easy','medium','hard']='medium'
    count:int=Field(default=3,ge=1,le=20)
    language:Literal['en','sw']='en'
    kind:Literal['mcq','true_false','numerical','short_answer']='mcq'
    use_local_ai:bool=False

@router.post('/quiz-draft')
def quiz_draft(data: QuizDraft, u: User = Depends(principal), db: Session = Depends(get_db)):
    c = course_access(db, u, data.course_id, manage=True)
    premium(db, u.id)
    try:questions,mode,warning=build_quiz(data,c.subject,QuestionInput)
    except ValueError as exc:raise HTTPException(422,str(exc))
    return {'title':data.topic+' practice','status':'draft','mode':mode,'warning':warning,'objective':data.objective,
            'difficulty':data.difficulty,'requested_count':data.count,'questions':questions}

@router.post('/lesson-draft')
def lesson(data: Draft, u: User = Depends(principal), db: Session = Depends(get_db)):
    c = course_access(db, u, data.course_id, manage=True)
    premium(db, u.id)
    score, entry = retrieve(data.topic, c.subject)
    if not entry or score < 0.15: raise HTTPException(422, 'No suitable teaching passage; refine the topic')
    outline = f'Learning objectives: explain {entry["topic"]}, solve an example, and justify the answer.\n'
    outline += '5 min: ask learners what they know.\n10 min: demonstrate the concept.\n15 min: paired practice using locally available materials.\n10 min: individual exercise and feedback.\n'
    outline += f'Teaching note: {entry["en"]}\nKiswahili support: {entry["sw"]}\nResource: original passage {entry["id"]}.\nAssessment: {entry["question"]}\nAdapt for accessibility and have the teacher verify factual accuracy.'
    return {'title': data.topic, 'outline': outline, 'mode': 'retrieval plus structured template; teacher draft'}

class LessonInput(Draft):
    outline: str = Field(min_length=20, max_length=15000)

@router.post('/lessons', status_code=201)
def save_lesson(data: LessonInput, u: User = Depends(principal), db: Session = Depends(get_db)):
    course_access(db, u, data.course_id, manage=True)
    return record(save(db, u, Lesson(course_id=data.course_id, title=data.topic, outline=data.outline), 'lesson.teacher_reviewed'))

@router.get('/lessons/{course_id}')
def lessons(course_id: int, u: User = Depends(principal), db: Session = Depends(get_db)):
    course_access(db, u, course_id, manage=True)
    return [record(x) for x in db.query(Lesson).filter_by(course_id=course_id)]
