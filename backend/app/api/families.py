from pydantic import Field
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import principal, role, require
from ..models import *
from ..schemas.common import Input
from ..services.access import *

router = APIRouter(prefix='/api', tags=['families and communication'])

@router.get('/parent/links')
def links(u: User = Depends(principal), db: Session = Depends(get_db)):
    require(db, u, 'parent')
    return [record(x) | {'student_name': db.get(User, x.student_id).name if x.status == 'approved' else 'Awaiting school verification'} for x in db.query(ParentStudentLink).filter_by(parent_id=u.id)]

class LinkInput(Input):
    student_id: int = Field(gt=0)

@router.post('/parent/links', status_code=201)
def request_link(data: LinkInput, u: User = Depends(principal), db: Session = Depends(get_db)):
    require(db, u, 'parent')
    s = db.get(User, data.student_id)
    if not s or not db.get(Student, data.student_id) or s.school_id != u.school_id: raise HTTPException(404, 'Student unavailable for linking')
    if db.query(ParentStudentLink).filter_by(parent_id=u.id, student_id=s.id).first(): raise HTTPException(409, 'Link request already exists')
    return record(save(db, u, ParentStudentLink(parent_id=u.id, student_id=s.id), 'parent.link_requested'))

@router.get('/notifications')
def notifications(u: User = Depends(principal), db: Session = Depends(get_db)):
    return [record(n) for n in db.query(Notification).filter_by(user_id=u.id).order_by(Notification.id.desc()).limit(100)]

@router.post('/notifications/{notification_id}/read')
def read(notification_id: int, u: User = Depends(principal), db: Session = Depends(get_db)):
    n = get(db, Notification, notification_id)
    if n.user_id != u.id: raise HTTPException(404, 'Notification not found')
    n.read = True
    return record(save(db, u, n, 'notification.read'))

def family_pair(db, sender, recipient, student_id):
    same_school(sender, recipient)
    s = get(db, User, student_id)
    same_school(sender, s)
    parent, teacher = (sender, recipient) if role(db, sender) == 'parent' else (recipient, sender)
    if role(db, parent) != 'parent' or role(db, teacher) != 'teacher' or not linked(db, parent.id, student_id): raise HTTPException(403, 'Approved parent-teacher relationship required')
    if not any(assigned(db, teacher.id, e.course_id) for e in db.query(Enrollment).filter_by(student_id=student_id)): raise HTTPException(403, 'Teacher is not assigned to this student')

class MessageInput(Input):
    recipient_id: int = Field(gt=0)
    student_id: int = Field(gt=0)
    body: str = Field(min_length=1, max_length=5000)

@router.post('/messages', status_code=201)
def send(data: MessageInput, u: User = Depends(principal), db: Session = Depends(get_db)):
    recipient = get(db, User, data.recipient_id)
    family_pair(db, u, recipient, data.student_id)
    sw=recipient.language=='sw'
    db.add(Notification(user_id=recipient.id, title='Ujumbe mpya wa shule' if sw else 'New school message', body=(f'Ujumbe kutoka {u.name}.' if sw else f'Message from {u.name}.')))
    return record(save(db, u, Message(sender_id=u.id, **data.model_dump()), 'message.sent'))

@router.get('/messages')
def messages(u: User = Depends(principal), db: Session = Depends(get_db)):
    require(db, u, 'parent', 'teacher')
    return [record(m) | {'sender_name': db.get(User, m.sender_id).name, 'recipient_name': db.get(User, m.recipient_id).name} for m in db.query(Message).filter(or_(Message.sender_id == u.id, Message.recipient_id == u.id)).order_by(Message.id.desc()).limit(100)]

@router.get('/message-contacts/{student_id}')
def contacts(student_id: int, u: User = Depends(principal), db: Session = Depends(get_db)):
    student_access(db, u, student_id)
    require(db, u, 'parent', 'teacher')
    ids = set()
    if role(db, u) == 'parent':
        for e in db.query(Enrollment).filter_by(student_id=student_id):
            ids.update(a.teacher_id for a in db.query(TeacherCourseAssignment).filter_by(course_id=e.course_id))
    else:
        ids.update(x.parent_id for x in db.query(ParentStudentLink).filter_by(student_id=student_id, status='approved'))
    return [{'id': p.id, 'name': p.name} for i in ids if (p := db.get(User, i)) and p.active]
