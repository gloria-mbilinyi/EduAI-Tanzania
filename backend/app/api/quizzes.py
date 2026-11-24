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
from ..ai.math_solver import equivalent, parse, UnsupportedMath

router = APIRouter(prefix='/api', tags=['quizzes'])

class QuestionInput(Input):
    prompt: str = Field(min_length=5, max_length=2000)
    options: list[str] = Field(default_factory=list, max_length=6)
    correct_index: int = Field(default=0,ge=0)
    explanation: str = Field(min_length=2, max_length=2000)
    kind: Literal['mcq','true_false','numerical','short_answer']='mcq'
    answer: str = Field(default='',max_length=2000)
    language: Literal['en','sw']='en'
    @model_validator(mode='after')
    def valid(self):
        if self.kind in {'mcq','true_false'}:
            if len(self.options)<2 or self.correct_index >= len(self.options) or any(not x.strip() or len(x) > 500 for x in self.options): raise ValueError('Invalid options or answer key')
            if self.kind=='true_false' and len(self.options)!=2:raise ValueError('True/false requires two options')
        elif not self.answer.strip():raise ValueError('A reviewed answer or rubric is required')
        if self.kind=='numerical':
            try:
                if parse(self.answer).free_symbols:raise ValueError('A numerical answer must be constant')
            except UnsupportedMath:raise ValueError('Invalid numerical answer')
        return self

class QuizInput(Input):
    title: str = Field(min_length=2, max_length=150)
    status: Literal['draft', 'published'] = 'draft'
    questions: list[QuestionInput] = Field(min_length=1, max_length=30)
    reviewed: bool = False

    @model_validator(mode='after')
    def publication_review(self):
        if self.status=='published' and not self.reviewed:raise ValueError('Teacher must confirm review before publication')
        return self

class Answers(Input):
    answers: dict[int, int | str]

def settings(db,question):
    cfg=db.query(QuestionSettings).filter_by(question_id=question.id).first()
    return {'kind':cfg.kind,'answer':cfg.answer,'language':cfg.language} if cfg else {'kind':'mcq','answer':'','language':'en'}

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
        cfg={k:v.pop(k) for k in ('kind','answer','language')}
        v['options'] = json.dumps(v['options'])
        row=Question(quiz_id=q.id, **v);db.add(row);db.flush()
        db.add(QuestionSettings(question_id=row.id,**cfg))
    if data.status=='published':db.add(QuizReview(quiz_id=q.id,teacher_id=u.id))
    return record(save(db, u, q, 'quiz.teacher_review_and_save'))

@router.get('/quizzes/{quiz_id}')
def detail(quiz_id: int, u: User = Depends(principal), db: Session = Depends(get_db)):
    q = get(db, Quiz, quiz_id)
    course_access(db, u, q.course_id)
    teacher = role(db, u) == 'teacher'
    if not teacher and q.status != 'published': raise HTTPException(404, 'Quiz not found')
    questions=[]
    for x in db.query(Question).filter_by(quiz_id=q.id):
        cfg=settings(db,x)
        if not teacher:cfg.pop('answer')
        questions.append(record(x, [] if teacher else ['correct_index', 'explanation']) | cfg | {'options':json.loads(x.options)})
    return record(q) | {'questions': questions}

@router.post('/quizzes/{quiz_id}/attempt', status_code=201)
def attempt(quiz_id: int, data: Answers, u: User = Depends(principal), db: Session = Depends(get_db)):
    require(db, u, 'student')
    q = get(db, Quiz, quiz_id)
    course_access(db, u, q.course_id)
    if q.status != 'published': raise HTTPException(404, 'Quiz not found')
    if db.query(Submission).filter_by(student_id=u.id, quiz_id=q.id).first(): raise HTTPException(409, 'Quiz already attempted')
    questions = db.query(Question).filter_by(quiz_id=q.id).all()
    if set(data.answers) != {x.id for x in questions}:raise HTTPException(422,'Answer every question')
    parts=[]
    for x in questions:
        cfg=settings(db,x);answer=data.answers[x.id];correct=None
        if cfg['kind'] in {'mcq','true_false'}:
            if type(answer)!=int or not 0<=answer<len(json.loads(x.options)):raise HTTPException(422,'Choose a valid option')
            correct=answer==x.correct_index
        elif not isinstance(answer,str) or not 1<=len(answer)<=2000:raise HTTPException(422,'Write a valid answer')
        elif cfg['kind']=='numerical':correct=bool(equivalent(answer,cfg['answer']))
        parts.append({'question_id':x.id,'prompt':x.prompt,'explanation':x.explanation,'kind':cfg['kind'],'correct':correct})
    s = Submission(student_id=u.id, quiz_id=q.id, content=json.dumps(data.answers))
    db.add(s)
    db.flush()
    pending=any(p['correct'] is None for p in parts)
    score=None if pending else round(100*sum(p['correct'] for p in parts)/len(parts),1)
    db.add(QuizResponse(submission_id=s.id,parts=json.dumps(parts)))
    if not pending:db.add(Grade(submission_id=s.id,score=score,feedback='Objective assessment graded automatically'))
    db.add(LearningActivity(student_id=u.id, course_id=q.course_id, action='quiz_attempted'))
    if not pending:grade_alert(db, u.id, score, q.title)
    save(db, u, s, 'quiz.auto_grade')
    return {'submission_id':s.id,'score':score,'status':'pending_teacher_grading' if pending else 'graded','feedback':parts}

class Publish(Input):
    reviewed: Literal[True]

@router.post('/quizzes/{quiz_id}/publish')
def publish(quiz_id:int,data:Publish,u:User=Depends(principal),db:Session=Depends(get_db)):
    q=get(db,Quiz,quiz_id);course_access(db,u,q.course_id,manage=True)
    if q.status!='draft':raise HTTPException(409,'Quiz is already published')
    q.status='published';db.add(QuizReview(quiz_id=q.id,teacher_id=u.id))
    return record(save(db,u,q,'quiz.review_and_publish'))

@router.get('/quizzes/{quiz_id}/submissions')
def submissions(quiz_id:int,u:User=Depends(principal),db:Session=Depends(get_db)):
    q=get(db,Quiz,quiz_id);course_access(db,u,q.course_id,manage=True)
    result=[]
    for s in db.query(Submission).filter_by(quiz_id=q.id):
        response=db.query(QuizResponse).filter_by(submission_id=s.id).first()
        grade=db.query(Grade).filter_by(submission_id=s.id).first()
        result.append(record(s)|{'student_name':db.get(User,s.student_id).name,'answers':json.loads(s.content),
            'parts':json.loads(response.parts) if response else [],'grade':record(grade) if grade else None})
    return result

class ManualMarks(Input):
    marks:dict[int,float]
    feedback:str=Field(min_length=3,max_length=3000)

@router.post('/quiz-submissions/{submission_id}/grade')
def manual_grade(submission_id:int,data:ManualMarks,u:User=Depends(principal),db:Session=Depends(get_db)):
    s=get(db,Submission,submission_id)
    if not s.quiz_id:raise HTTPException(404,'Quiz submission not found')
    q=get(db,Quiz,s.quiz_id);course_access(db,u,q.course_id,manage=True)
    response=db.query(QuizResponse).filter_by(submission_id=s.id).first()
    if not response or db.query(Grade).filter_by(submission_id=s.id).first():raise HTTPException(409,'Objective or completed grades cannot be overwritten')
    parts=json.loads(response.parts);manual={p['question_id'] for p in parts if p['kind']=='short_answer'}
    if set(data.marks)!=manual or any(not 0<=m<=100 for m in data.marks.values()):raise HTTPException(422,'Grade every short answer from 0 to 100')
    score=round(sum(data.marks[p['question_id']] if p['kind']=='short_answer' else 100*bool(p['correct']) for p in parts)/len(parts),1)
    response.manual_marks=json.dumps(data.marks)
    g=Grade(submission_id=s.id,score=score,feedback=data.feedback,grader_id=u.id);db.add(g)
    grade_alert(db,s.student_id,score,q.title)
    return record(save(db,u,g,'quiz.teacher_short_answer_grade'))
