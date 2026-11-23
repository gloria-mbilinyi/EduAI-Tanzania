from ..models import Notification, ParentStudentLink, User

def grade_alert(db, student_id, score, title):
    student = db.get(User, student_id)
    recipients = [student_id] + [x.parent_id for x in db.query(ParentStudentLink).filter_by(student_id=student_id, status='approved')]
    for ident in recipients:
        db.add(Notification(user_id=ident, title='New academic result', body=f'{student.name}: {title}, {score:.0f}%. ' + ('Teacher follow-up recommended.' if score < 50 else 'Keep practising.')))
