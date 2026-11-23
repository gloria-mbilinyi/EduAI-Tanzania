import json
from typing import Literal
from pydantic import Field, model_validator
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import *
from ..schemas.common import Input
from ..core.database import get_db
from ..core.security import principal, require, role
from ..services.access import *
from ..services.notifications import grade_alert

router = APIRouter(prefix='/api', tags=['quizzes'])

class QuestionInput(Input):
    prompt: str = Field(min_length=5, max_length=2000)
    options: list[str] = Field(min_length=2, max_length=6)
    correct_index: int = Field(ge=0)
    explanation: str = Field(min_length=2, max_length=2000)
    @model_validator(mode='after')
    def valid(self):
        if self.correct_index >= len(self.options) or any(not x.strip() or len(x) > 500 for x in self.options): raise ValueError('Invalid options or answer key')
        return self

class QuizInput(Input):
    title: str = Field(min_length=2, max_length=150)
    status: Literal['draft', 'published'] = 'draft'
    questions: list[QuestionInput] = Field(min_length=1, max_length=30)

class Answers(Input):
    answers: dict[int, int]

@router.get('/courses/{course_id}/quizzes')
def quizzes(course_id: int, u: User = Depends(principal), db: Session = Depends(get_db)):
    course_access(db, u, course_id)
    q = db.query(Quiz).filter_by(course_id=course_id)
    if role(db, u) != 'teacher': q = q.filter_by(status='published')
    return [record(x) | {'attempted': bool(db.query(Submission).filter_by(student_id=u.id, quiz_id=x.id).first())} for x in q]

@router.post('/courses/{course_id}/quizzes', status_code=201)
def create(course_id: int, data: QuizInput, u: User = Depends(principal), db: Session = Depends(get_db)):
    course_access(db, u, course_id, manage=True)
    q = Quiz(course_id=course_id, title=data.title, status=data.status)
    db.add(q)
    db.flush()
    for question in data.questions:
        v = question.model_dump()
        v['options'] = json.dumps(v['options'])
        db.add(Question(quiz_id=q.id, **v))
    return record(save(db, u, q, 'quiz.teacher_review_and_save'))

@router.get('/quizzes/{quiz_id}')
def detail(quiz_id: int, u: User = Depends(principal), db: Session = Depends(get_db)):
    q = get(db, Quiz, quiz_id)
    course_access(db, u, q.course_id)
    teacher = role(db, u) == 'teacher'
    if not teacher and q.status != 'published': raise HTTPException(404, 'Quiz not found')
    questions = [record(x, [] if teacher else ['correct_index', 'explanation']) | {'options': json.loads(x.options)} for x in db.query(Question).filter_by(quiz_id=q.id)]
    return record(q) | {'questions': questions}

@router.post('/quizzes/{quiz_id}/attempt', status_code=201)
def attempt(quiz_id: int, data: Answers, u: User = Depends(principal), db: Session = Depends(get_db)):
    require(db, u, 'student')
    q = get(db, Quiz, quiz_id)
    course_access(db, u, q.course_id)
    if q.status != 'published': raise HTTPException(404, 'Quiz not found')
    if db.query(Submission).filter_by(student_id=u.id, quiz_id=q.id).first(): raise HTTPException(409, 'Quiz already attempted')
    questions = db.query(Question).filter_by(quiz_id=q.id).all()
    if set(data.answers) != {x.id for x in questions} or any(data.answers[x.id] < 0 or data.answers[x.id] >= len(json.loads(x.options)) for x in questions):
        raise HTTPException(422, 'Answer every question using a valid option')
    s = Submission(student_id=u.id, quiz_id=q.id, content=json.dumps(data.answers))
    db.add(s)
    db.flush()
    score = round(100 * sum(data.answers[x.id] == x.correct_index for x in questions) / len(questions), 1)
    g = Grade(submission_id=s.id, score=score, feedback='Objective assessment graded automatically')
    db.add(g)
    db.add(LearningActivity(student_id=u.id, course_id=q.course_id, action='quiz_attempted'))
    grade_alert(db, u.id, score, q.title)
    save(db, u, s, 'quiz.auto_grade')
    return {'score': score, 'feedback': [{'prompt': x.prompt, 'explanation': x.explanation, 'correct': data.answers[x.id] == x.correct_index} for x in questions]}
