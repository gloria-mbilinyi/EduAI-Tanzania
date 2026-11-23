from datetime import datetime
from pydantic import Field
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import *
from ..schemas.common import Input, TextInput
from ..core.database import get_db, now
from ..core.security import principal, require, role
from ..services.access import *
from ..services.notifications import grade_alert

router = APIRouter(prefix='/api', tags=['assignments'])

class AssignmentInput(Input):
    title: str = Field(min_length=2, max_length=150)
    instructions: str = Field(min_length=5, max_length=10000)
    due_at: datetime | None = None

class GradeInput(Input):
    score: float = Field(ge=0, le=100)
    feedback: str = Field(min_length=1, max_length=5000)

@router.get('/courses/{course_id}/assignments')
def assignments(course_id: int, u: User = Depends(principal), db: Session = Depends(get_db)):
    course_access(db, u, course_id)
    result = []
    for a in db.query(Assignment).filter_by(course_id=course_id):
        sub = db.query(Submission).filter_by(assignment_id=a.id, student_id=u.id).first()
        grade = db.query(Grade).filter_by(submission_id=sub.id).first() if sub else None
        result.append(record(a) | {'submitted': bool(sub), 'grade': record(grade) if grade else None})
    return result

@router.post('/courses/{course_id}/assignments', status_code=201)
def create(course_id: int, data: AssignmentInput, u: User = Depends(principal), db: Session = Depends(get_db)):
    course_access(db, u, course_id, manage=True)
    values = data.model_dump()
    if values['due_at']: values['due_at'] = values['due_at'].replace(tzinfo=None)
    return record(save(db, u, Assignment(course_id=course_id, **values), 'assignment.create'))

@router.patch('/assignments/{assignment_id}')
def update(assignment_id: int, data: AssignmentInput, u: User = Depends(principal), db: Session = Depends(get_db)):
    a = get(db, Assignment, assignment_id)
    course_access(db, u, a.course_id, manage=True)
    for k, v in data.model_dump().items(): setattr(a, k, v.replace(tzinfo=None) if k == 'due_at' and v else v)
    return record(save(db, u, a, 'assignment.update'))

@router.post('/assignments/{assignment_id}/submit', status_code=201)
def submit(assignment_id: int, data: TextInput, u: User = Depends(principal), db: Session = Depends(get_db)):
    require(db, u, 'student')
    a = get(db, Assignment, assignment_id)
    course_access(db, u, a.course_id)
    if a.due_at and a.due_at < now(): raise HTTPException(409, 'Assignment deadline has passed')
    if db.query(Submission).filter_by(student_id=u.id, assignment_id=a.id).first(): raise HTTPException(409, 'Assignment already submitted')
    s = Submission(student_id=u.id, assignment_id=a.id, content=data.body)
    db.add(LearningActivity(student_id=u.id, course_id=a.course_id, action='assignment_submitted'))
    return record(save(db, u, s, 'assignment.submit'))

@router.get('/assignments/{assignment_id}/submissions')
def submissions(assignment_id: int, u: User = Depends(principal), db: Session = Depends(get_db)):
    a = get(db, Assignment, assignment_id)
    course_access(db, u, a.course_id, manage=True)
    return [record(s) | {'student_name': db.get(User, s.student_id).name, 'grade': record(g) if (g := db.query(Grade).filter_by(submission_id=s.id).first()) else None} for s in db.query(Submission).filter_by(assignment_id=a.id)]

@router.post('/submissions/{submission_id}/grade')
def grade(submission_id: int, data: GradeInput, u: User = Depends(principal), db: Session = Depends(get_db)):
    s = get(db, Submission, submission_id)
    if not s.assignment_id: raise HTTPException(409, 'Objective quiz grades cannot be overridden')
    a = get(db, Assignment, s.assignment_id)
    course_access(db, u, a.course_id, manage=True)
    g = db.query(Grade).filter_by(submission_id=s.id).first() or Grade(submission_id=s.id)
    g.score, g.feedback, g.grader_id = data.score, data.feedback, u.id
    grade_alert(db, s.student_id, data.score, a.title)
    return record(save(db, u, g, 'grade.record'))
