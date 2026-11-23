from typing import Literal
from pydantic import Field
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ..core.database import get_db, now
from ..core.security import principal, require, role, public_user
from ..models import *
from ..schemas.common import Input, Registration
from ..services.access import *
from ..services.performance import performance
from .auth import register

router = APIRouter(prefix='/api/admin', tags=['school administration'])

def admin(u: User = Depends(principal), db: Session = Depends(get_db)):
    require(db, u, 'admin')
    return u

@router.get('/school')
def school(u: User = Depends(admin), db: Session = Depends(get_db)):
    return record(get(db, School, u.school_id))

class SchoolInput(Input):
    name: str = Field(min_length=3, max_length=150)
    region: str = Field(min_length=2, max_length=80)

@router.patch('/school')
def update_school(data: SchoolInput, u: User = Depends(admin), db: Session = Depends(get_db)):
    s = get(db, School, u.school_id)
    s.name, s.region = data.name, data.region
    return record(save(db, u, s, 'school.update'))

@router.get('/users')
def users(u: User = Depends(admin), db: Session = Depends(get_db)):
    return [public_user(db, x) for x in db.query(User).filter_by(school_id=u.school_id)]

@router.post('/users', status_code=201)
def create_user(data: Registration, u: User = Depends(admin), db: Session = Depends(get_db)):
    if data.school_id != u.school_id: raise HTTPException(403, 'School scope denied')
    result = register(data, db)
    audit(db, u, 'admin.account_created', f'user:{result["user"]["id"]}')
    db.commit()
    return result

class Activation(Input):
    active: bool

@router.patch('/users/{user_id}')
def activate(user_id: int, data: Activation, u: User = Depends(admin), db: Session = Depends(get_db)):
    target = get(db, User, user_id)
    same_school(u, target)
    if role(db, target) == 'admin': raise HTTPException(403, 'Administrator identities require out-of-band provisioning')
    target.active = data.active
    save(db, u, target, 'admin.account_activation')
    return public_user(db, target)

class AssignmentInput(Input):
    teacher_id: int = Field(gt=0)
    course_id: int = Field(gt=0)

@router.post('/teacher-assignments', status_code=201)
def assign(data: AssignmentInput, u: User = Depends(admin), db: Session = Depends(get_db)):
    t, c = get(db, User, data.teacher_id), get(db, Course, data.course_id)
    same_school(u, t)
    same_school(u, c)
    if not db.get(Teacher, t.id) or not t.active: raise HTTPException(422, 'Active teacher required')
    if assigned(db, t.id, c.id): raise HTTPException(409, 'Teacher already assigned')
    return record(save(db, u, TeacherCourseAssignment(**data.model_dump()), 'admin.teacher_assigned'))

@router.get('/teacher-assignments')
def assignments(u: User = Depends(admin), db: Session = Depends(get_db)):
    return [record(a) for a in db.query(TeacherCourseAssignment).join(Course, Course.id == TeacherCourseAssignment.course_id).filter(Course.school_id == u.school_id)]

@router.delete('/teacher-assignments/{assignment_id}', status_code=204)
def unassign(assignment_id: int, u: User = Depends(admin), db: Session = Depends(get_db)):
    a = get(db, TeacherCourseAssignment, assignment_id)
    same_school(u, get(db, Course, a.course_id))
    audit(db, u, 'admin.teacher_unassigned', f'assignment:{a.id}')
    db.delete(a)
    db.commit()

class EnrollmentInput(Input):
    student_id: int = Field(gt=0)
    course_id: int = Field(gt=0)

@router.post('/enrollments', status_code=201)
def enroll(data: EnrollmentInput, u: User = Depends(admin), db: Session = Depends(get_db)):
    s, c = get(db, User, data.student_id), get(db, Course, data.course_id)
    same_school(u, s)
    same_school(u, c)
    if not db.get(Student, s.id): raise HTTPException(422, 'Student required')
    if enrolled(db, s.id, c.id): raise HTTPException(409, 'Already enrolled')
    return record(save(db, u, Enrollment(**data.model_dump()), 'admin.student_enrolled'))

@router.get('/parent-links')
def links(u: User = Depends(admin), db: Session = Depends(get_db)):
    return [record(x) | {'parent_name': db.get(User, x.parent_id).name, 'student_name': db.get(User, x.student_id).name} for x in db.query(ParentStudentLink).join(User, User.id == ParentStudentLink.parent_id).filter(User.school_id == u.school_id)]

class LinkDecision(Input):
    status: Literal['approved', 'rejected']

@router.patch('/parent-links/{link_id}')
def decide_link(link_id: int, data: LinkDecision, u: User = Depends(admin), db: Session = Depends(get_db)):
    link = get(db, ParentStudentLink, link_id)
    same_school(u, get(db, User, link.parent_id))
    same_school(u, get(db, User, link.student_id))
    link.status = data.status
    return record(save(db, u, link, 'admin.parent_link_' + data.status))

@router.get('/reports')
def reports(u: User = Depends(admin), db: Session = Depends(get_db)):
    students = db.query(User).join(Student, Student.user_id == User.id).filter(User.school_id == u.school_id).all()
    data = [performance(db, s.id) | {'name': s.name} for s in students]
    values = [x['average'] for x in data if x['average'] is not None]
    ids = [x.id for x in db.query(User).filter_by(school_id=u.school_id)]
    return {'school': record(get(db, School, u.school_id)), 'users': len(ids), 'students': data,
            'school_average': round(sum(values)/len(values), 1) if values else None,
            'learning_activities': db.query(LearningActivity).filter(LearningActivity.student_id.in_(ids)).count(),
            'login_events': db.query(AuditLog).filter(AuditLog.actor_id.in_(ids), AuditLog.action == 'account.login').count(),
            'method': 'Unweighted mean of student means with at least one grade; demo sample, not a school ranking'}

@router.get('/audit')
def audit_log(u: User = Depends(admin), db: Session = Depends(get_db)):
    return [record(a) for a in db.query(AuditLog).join(User, User.id == AuditLog.actor_id).filter(User.school_id == u.school_id).order_by(AuditLog.id.desc()).limit(200)]
