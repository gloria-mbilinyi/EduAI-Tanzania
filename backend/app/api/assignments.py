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
    return [record(s) | {'student_name': db.get(User, s.student_id).name,
            'attempts': att.history(db,s), 'official': att.official(db,s),
            'grade': record(g) if (g := db.query(Grade).filter_by(submission_id=s.id).first()) else None}
            for s in db.query(Submission).filter_by(assignment_id=a.id)]

def record_grade(db,u,s,attempt,data):
    a = get(db,Assignment,s.assignment_id)
    course_access(db,u,a.course_id,manage=True)
    g = att.grade_for(db,attempt)
    if not g:
        g = Grade(submission_id=s.id) if attempt.number==1 else AttemptGrade(attempt_id=attempt.id)
    # Every accepted revision is retained. Legacy initial marks are snapshotted by migration/ensure_first.
    g.score,g.feedback,g.grader_id=data.score,data.feedback,u.id
    db.add(g)
    db.add(GradeHistory(attempt_id=attempt.id,score=data.score,feedback=data.feedback,grader_id=u.id))
    grade_alert(db,s.student_id,data.score,a.title)
    return record(save(db,u,g,'grade.attempt_record'))

@router.post('/submissions/{submission_id}/grade')
def grade(submission_id: int, data: GradeInput, u: User = Depends(principal), db: Session = Depends(get_db)):
    s = get(db, Submission, submission_id)
    if not s.assignment_id: raise HTTPException(409, 'Objective quiz grades cannot be overridden')
    a = get(db, Assignment, s.assignment_id)
    course_access(db, u, a.course_id, manage=True)
    return record_grade(db,u,s,att.ensure_first(db,s),data)

@router.post('/attempts/{attempt_id}/grade')
def grade_attempt(attempt_id:int,data:GradeInput,u:User=Depends(principal),db:Session=Depends(get_db)):
    attempt=get(db,SubmissionAttempt,attempt_id); s=get(db,Submission,attempt.submission_id)
    return record_grade(db,u,s,attempt,data)

@router.get('/assignments/{assignment_id}/history')
def attempt_history(assignment_id:int,student_id:int|None=None,u:User=Depends(principal),db:Session=Depends(get_db)):
    a=get(db,Assignment,assignment_id); sid=student_id or u.id
    student_access(db,u,sid); course_access(db,u,a.course_id,manage=role(db,u)=='teacher')
    if not enrolled(db,sid,a.course_id): raise HTTPException(404,'Student not enrolled')
    state,s,_=att.eligibility(db,a,sid)
    return state | {'official':att.official(db,s) if s else None,
        'feedback_history':[record(g) for row in state['attempts'] if row['id'] for g in db.query(GradeHistory).filter_by(attempt_id=row['id'])]}

@router.post('/attempts/{attempt_id}/select-final')
def select_final(attempt_id:int,u:User=Depends(principal),db:Session=Depends(get_db)):
    attempt=get(db,SubmissionAttempt,attempt_id);s=get(db,Submission,attempt.submission_id);a=get(db,Assignment,s.assignment_id)
    course_access(db,u,a.course_id,manage=True)
    if att.policy(db,a.id)['grading_policy']!='selected' or not att.grade_for(db,attempt):
        raise HTTPException(409,'Choose a graded attempt under the teacher-selected policy')
    selection=db.query(FinalGradeSelection).filter_by(submission_id=s.id).first() or FinalGradeSelection(submission_id=s.id)
    selection.attempt_id,selection.teacher_id=attempt.id,u.id
    return record(save(db,u,selection,'grade.select_final'))

class RequestInput(Input):
    reason:str=Field(min_length=3,max_length=2000)

@router.post('/assignments/{assignment_id}/resubmission-requests',status_code=201)
def request_resubmission(assignment_id:int,data:RequestInput,u:User=Depends(principal),db:Session=Depends(get_db)):
    require(db,u,'student');a=get(db,Assignment,assignment_id);course_access(db,u,a.course_id)
    state,s,_=att.eligibility(db,a,u.id)
    if not s: raise HTTPException(409,'Submit the first attempt before requesting resubmission')
    if db.query(ResubmissionApproval).filter_by(assignment_id=a.id,student_id=u.id,attempt_number=state['next_attempt'],status='pending').first():
        raise HTTPException(409,'A request is already pending')
    return record(save(db,u,ResubmissionApproval(assignment_id=a.id,student_id=u.id,attempt_number=state['next_attempt'],reason=data.reason),'assignment.resubmission_request'))

@router.get('/assignments/{assignment_id}/resubmission-requests')
def requests(assignment_id:int,u:User=Depends(principal),db:Session=Depends(get_db)):
    a=get(db,Assignment,assignment_id); course_access(db,u,a.course_id,manage=role(db,u)!='student')
    q=db.query(ResubmissionApproval).filter_by(assignment_id=a.id)
    if role(db,u)=='student': q=q.filter_by(student_id=u.id)
    return [record(r)|{'student_name':db.get(User,r.student_id).name} for r in q]

class ApprovalInput(Input):
    decision:Literal['approved','rejected']
    comment:str=Field(min_length=3,max_length=2000)
    reopen_until:datetime|None=None

@router.post('/resubmission-requests/{request_id}/review')
def review_request(request_id:int,data:ApprovalInput,u:User=Depends(principal),db:Session=Depends(get_db)):
    r=get(db,ResubmissionApproval,request_id);a=get(db,Assignment,r.assignment_id);course_access(db,u,a.course_id,manage=True)
    if r.status!='pending':raise HTTPException(409,'Request is no longer pending')
    if data.reopen_until and utc(data.reopen_until)<=now():raise HTTPException(422,'Reopen date must be in the future')
    state,_,_=att.eligibility(db,a,r.student_id)
    if state['next_attempt']!=r.attempt_number:raise HTTPException(409,'Attempt history changed; request again')
    r.status,r.comment,r.teacher_id,r.reopen_until=data.decision,data.comment,u.id,utc(data.reopen_until)
    return record(save(db,u,r,'assignment.resubmission_'+data.decision))

class ReopenInput(RequestInput):
    student_id:int=Field(gt=0)
    reopen_until:datetime

@router.post('/assignments/{assignment_id}/reopen',status_code=201)
def reopen(assignment_id:int,data:ReopenInput,u:User=Depends(principal),db:Session=Depends(get_db)):
    a=get(db,Assignment,assignment_id);course_access(db,u,a.course_id,manage=True)
    if not enrolled(db,data.student_id,a.course_id):raise HTTPException(404,'Student not enrolled')
    if utc(data.reopen_until)<=now():raise HTTPException(422,'Reopen date must be in the future')
    state,_,_=att.eligibility(db,a,data.student_id)
    return record(save(db,u,ResubmissionApproval(assignment_id=a.id,student_id=data.student_id,
        attempt_number=state['next_attempt'],status='approved',reason=data.reason,comment='Teacher reopened',
        teacher_id=u.id,reopen_until=utc(data.reopen_until)),'assignment.reopen'))
