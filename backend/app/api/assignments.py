from datetime import datetime, timezone
from typing import Literal
from sqlalchemy.exc import IntegrityError
from pydantic import Field
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models import *
from ..schemas.common import Input, TextInput
from ..core.database import get_db, now
from ..core.security import principal, require, role
from ..services.access import *
from ..services.notifications import grade_alert
from ..services import attempts as att

router = APIRouter(prefix='/api', tags=['assignments'])

class PolicyInput(Input):
    max_attempts: int = Field(default=1, ge=1, le=20)
    allow_resubmission: bool = False
    allow_late: bool = False
    require_feedback: bool = False
    require_approval: bool = False
    grading_policy: Literal['first','best','latest','selected'] = 'latest'

class AssignmentInput(Input):
    title: str = Field(min_length=2, max_length=150)
    instructions: str = Field(min_length=5, max_length=10000)
    due_at: datetime | None = None
    policy: PolicyInput = Field(default_factory=PolicyInput)

def utc(value):
    return value.astimezone(timezone.utc).replace(tzinfo=None) if value and value.tzinfo else value

def set_policy(db, assignment_id, data):
    p = db.query(AssignmentPolicy).filter_by(assignment_id=assignment_id).first() or AssignmentPolicy(assignment_id=assignment_id)
    for k,v in data.items(): setattr(p,k,v)
    db.add(p)

class GradeInput(Input):
    score: float = Field(ge=0, le=100)
    feedback: str = Field(min_length=1, max_length=5000)

@router.get('/courses/{course_id}/assignments')
def assignments(course_id: int, u: User = Depends(principal), db: Session = Depends(get_db)):
    course_access(db, u, course_id)
    result = []
    for a in db.query(Assignment).filter_by(course_id=course_id):
        sub = db.query(Submission).filter_by(assignment_id=a.id, student_id=u.id).first()
        state, sub, _ = att.eligibility(db,a,u.id)
        selected = att.official(db,sub) if sub else None
        result.append(record(a) | state | {'submitted': bool(sub), 'grade': selected['grade'] if selected else None,
                     'official_attempt': selected['number'] if selected else None})
    return result

@router.post('/courses/{course_id}/assignments', status_code=201)
def create(course_id: int, data: AssignmentInput, u: User = Depends(principal), db: Session = Depends(get_db)):
    course_access(db, u, course_id, manage=True)
    values = data.model_dump()
    p = values.pop('policy'); values['due_at'] = utc(values['due_at'])
    a = Assignment(course_id=course_id, **values)
    db.add(a); db.flush(); set_policy(db,a.id,p)
    return record(save(db, u, a, 'assignment.create')) | {'policy': p}

@router.patch('/assignments/{assignment_id}')
def update(assignment_id: int, data: AssignmentInput, u: User = Depends(principal), db: Session = Depends(get_db)):
    a = get(db, Assignment, assignment_id)
    course_access(db, u, a.course_id, manage=True)
    values = data.model_dump(); p = values.pop('policy')
    for k, v in values.items(): setattr(a, k, utc(v) if k == 'due_at' else v)
    set_policy(db,a.id,p)
    return record(save(db, u, a, 'assignment.update'))

@router.post('/assignments/{assignment_id}/submit', status_code=201)
def submit(assignment_id: int, data: TextInput, u: User = Depends(principal), db: Session = Depends(get_db)):
    require(db, u, 'student')
    a = get(db, Assignment, assignment_id)
    course_access(db, u, a.course_id)
    try:
        s, attempt = att.add_attempt(db,a,u,data.body)
        save(db,u,attempt,'assignment.attempt_submit')
    except IntegrityError:
        db.rollback()
        raise HTTPException(409,'An attempt was already submitted; refresh before retrying')
    return record(s) | {'attempt_id':attempt.id,'attempt_number':attempt.number}

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
