"""Idempotent fictional demonstration data; never run against personal records."""
import getpass
import json
import os
from datetime import timedelta
from .core.database import SessionLocal, now
from .core.security import hash_password
from .models import *
from .migrate import migrate
from .ai.recommendations import generate
from .ai.corpus import CORPUS

def seed(db, password):
    if len(password) < 10: raise ValueError('Choose a demonstration password of at least 10 characters')
    if db.query(User).first(): return False
    roles = {}
    for name in ['admin', 'teacher', 'student', 'parent']:
        r = Role(name=name)
        db.add(r)
        db.flush()
        roles[name] = r.id
    school = School(name='Mwangaza Secondary (Fictional Demo)', region='Dodoma')
    other = School(name='Upendo Secondary (Fictional Demo)', region='Morogoro')
    db.add_all([school, other])
    db.flush()
    accounts = [('admin', 'School Administrator', 'admin', school.id), ('neema', 'Neema Mushi', 'teacher', school.id),
                ('amina', 'Amina Juma', 'student', school.id), ('juma', 'Juma Salum', 'student', school.id),
                ('parent', 'Rehema Juma', 'parent', school.id), ('hamisi', 'Hamisi Ally', 'teacher', school.id),
                ('isolated', 'Other School Student', 'student', other.id)]
    users = {}
    hashed = hash_password(password)
    for handle, name, r, school_id in accounts:
        u = User(email=handle + '@demo.eduai.test', name=name, role_id=roles[r], school_id=school_id, password_hash=hashed)
        db.add(u)
        db.flush()
        users[handle] = u
        if r != 'admin': db.add({'teacher': Teacher, 'student': Student, 'parent': Parent}[r](user_id=u.id))
    db.flush()
    courses = []
    for title, subject, sch in [('Mathematics foundations', 'Mathematics', school.id), ('Discovering living things', 'Biology', school.id), ('Physics in everyday life', 'Physics', school.id), ('Other school mathematics', 'Mathematics', other.id)]:
        c = Course(title=title, subject=subject, school_id=sch, description='Fictional Form 2 teaching demonstration with low-bandwidth notes and practice.')
        db.add(c)
        db.flush()
        courses.append(c)
    for c in courses[:2]: db.add(TeacherCourseAssignment(teacher_id=users['neema'].id, course_id=c.id))
    db.add(TeacherCourseAssignment(teacher_id=users['hamisi'].id, course_id=courses[2].id))
    for student in ['amina', 'juma']:
        for c in courses[:3]: db.add(Enrollment(student_id=users[student].id, course_id=c.id))
    db.add(Enrollment(student_id=users['isolated'].id, course_id=courses[3].id))
    db.add(ParentStudentLink(parent_id=users['parent'].id, student_id=users['amina'].id, status='approved'))
    db.flush()
    for c in courses[:3]:
        entries = [e for e in CORPUS if e['subject'] == c.subject]
        for e in entries:
            db.add(LearningMaterial(course_id=c.id, title=e['topic'], kind='notes', content=e['en'] + '\n\n' + e['sw']))
        a = Assignment(course_id=c.id, title=f'{c.subject} practice journal', instructions='Explain a concept in your own words, give one example, and write a question to discuss with your teacher.', due_at=now()+timedelta(days=14))
        db.add(a)
        db.flush()
        for handle, score in [('amina', 45 if c.subject == 'Mathematics' else 76), ('juma', 82)]:
            s = Submission(student_id=users[handle].id, assignment_id=a.id, content='Fictional sample submission for demonstration.')
            db.add(s)
            db.flush()
            db.add(Grade(submission_id=s.id, score=score, feedback='Review the worked examples and explain your steps.', grader_id=users['neema' if c.subject != 'Physics' else 'hamisi'].id))
        q = Quiz(course_id=c.id, title=entries[0]['topic'] + ' checkpoint', status='published')
        db.add(q)
        db.flush()
        for e in entries[:2]: db.add(Question(quiz_id=q.id, prompt=e['question'], options=json.dumps(e['options']), correct_index=e['correct'], explanation=e['en']))
        db.add(LearningActivity(student_id=users['amina'].id, course_id=c.id, action='read_materials'))
    db.flush()
    for c, status in [(courses[0], 'pending_review'), (courses[1], 'published')]:
        content, reasons = generate(db, users['amina'].id, c.id)
        r = Recommendation(student_id=users['amina'].id, course_id=c.id, content=content, reasons=json.dumps(reasons), status=status)
        db.add(r)
        db.flush()
        if status == 'published': db.add(RecommendationApproval(recommendation_id=r.id, teacher_id=users['neema'].id, decision='approved', comment='Fictional teacher approval for demonstration.', version=1))
    plan = SubscriptionPlan(name='Learning Plus Demo', price_tzs=3000, days=30, premium=True)
    db.add(plan)
    db.flush()
    s = Subscription(user_id=users['neema'].id, plan_id=plan.id, premium=True, status='active', expires_at=now()+timedelta(days=30))
    db.add(s)
    db.flush()
    db.add_all([Payment(subscription_id=s.id, amount_tzs=3000, provider_reference='DEMO-SEED-TEACHER', status='verified', verified_at=now()),
                ProviderTransaction(reference='DEMO-SEED-TEACHER', amount_tzs=3000, currency='TZS', outcome='success'),
                Notification(user_id=users['parent'].id, title='Mathematics follow-up', body='Amina scored 45% in the fictional mathematics practice. Please contact the assigned teacher.'),
                AuditLog(actor_id=users['admin'].id, action='demo.seed', entity='fictional_data', detail='Teacher demo subscription has a matching simulated provider transaction.')])
    db.commit()
    return True

if __name__ == '__main__':
    migrate()
    password = os.getenv('EDUAI_DEMO_PASSWORD') or getpass.getpass('Choose a shared fictional demo password (10+ characters): ')
    with SessionLocal() as db: print('Fictional demo created.' if seed(db, password) else 'Database already contains users; seed skipped.')
