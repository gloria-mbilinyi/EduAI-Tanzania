from ..models import Notification, ParentStudentLink, User

def grade_alert(db, student_id, score, title):
    student = db.get(User, student_id)
    recipients = [student_id] + [x.parent_id for x in db.query(ParentStudentLink).filter_by(student_id=student_id, status='approved')]
    for ident in recipients:
        sw=db.get(User,ident).language=='sw'
        db.add(Notification(user_id=ident, title='Matokeo mapya ya masomo' if sw else 'New academic result', body=f'{student.name}: {title}, {score:.0f}%. ' + (('Ufuatiliaji wa mwalimu unapendekezwa.' if score<50 else 'Endelea kufanya mazoezi.') if sw else ('Teacher follow-up recommended.' if score < 50 else 'Keep practising.'))))
