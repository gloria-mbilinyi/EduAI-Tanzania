from fastapi import HTTPException
from ..models import *
from ..core.security import role, require

def get(db, model, ident):
    item = db.get(model, ident)
    if not item: raise HTTPException(404, 'Record not found')
    return item

def same_school(user, other):
    if user.school_id != other.school_id: raise HTTPException(404, 'Record not found')

def assigned(db, teacher_id, course_id):
    return db.query(TeacherCourseAssignment).filter_by(teacher_id=teacher_id, course_id=course_id).first() is not None

def enrolled(db, student_id, course_id):
    return db.query(Enrollment).filter_by(student_id=student_id, course_id=course_id).first() is not None

def linked(db, parent_id, student_id):
    return db.query(ParentStudentLink).filter_by(parent_id=parent_id, student_id=student_id, status='approved').first() is not None

def course_access(db, user, course_id, manage=False):
    course = get(db, Course, course_id)
    same_school(user, course)
    r = role(db, user)
    if r == 'teacher' and assigned(db, user.id, course_id): return course
    if not manage and r == 'student' and enrolled(db, user.id, course_id): return course
    if not manage and r == 'parent':
        ids = [x.student_id for x in db.query(ParentStudentLink).filter_by(parent_id=user.id, status='approved')]
        if any(enrolled(db, s, course_id) for s in ids): return course
    if r == 'admin' and not manage: return course
    raise HTTPException(403, 'Course access denied')

def student_access(db, user, student_id):
    student = get(db, User, student_id)
    same_school(user, student)
    if not db.get(Student, student_id): raise HTTPException(404, 'Student not found')
    r = role(db, user)
    if r == 'admin' or (r == 'student' and user.id == student_id) or (r == 'parent' and linked(db, user.id, student_id)):
        return student
    if r == 'teacher':
        if any(assigned(db, user.id, e.course_id) for e in db.query(Enrollment).filter_by(student_id=student_id)): return student
    raise HTTPException(403, 'Student access denied')

def audit(db, user, action, entity, detail=''):
    db.add(AuditLog(actor_id=user.id, action=action, entity=str(entity), detail=detail[:500]))

def save(db, user, item, action):
    db.add(item)
    db.flush()
    audit(db, user, action, f'{item.__tablename__}:{getattr(item, "id", "")}')
    db.commit()
    return item

def record(item, exclude=()):
    return {c.name: getattr(item, c.name) for c in item.__table__.columns if c.name not in exclude}
