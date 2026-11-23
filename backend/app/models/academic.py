from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey, UniqueConstraint, CheckConstraint, DateTime
from ..core.database import Base, Entity

class Course(Entity, Base):
    __tablename__ = 'courses'
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=False, index=True)
    title = Column(String(120), nullable=False)
    subject = Column(String(60), nullable=False)
    form = Column(String(20), nullable=False, default='Form 2')
    description = Column(Text, nullable=False, default='')

class TeacherCourseAssignment(Entity, Base):
    __tablename__ = 'teacher_course_assignments'
    teacher_id = Column(Integer, ForeignKey('teachers.user_id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    __table_args__ = (UniqueConstraint('teacher_id', 'course_id'),)

class Enrollment(Entity, Base):
    __tablename__ = 'enrollments'
    student_id = Column(Integer, ForeignKey('students.user_id'), nullable=False)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    __table_args__ = (UniqueConstraint('student_id', 'course_id'),)

class Lesson(Entity, Base):
    __tablename__ = 'lessons'
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    title = Column(String(150), nullable=False)
    outline = Column(Text, nullable=False, default='')

class LearningMaterial(Entity, Base):
    __tablename__ = 'learning_materials'
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    title = Column(String(150), nullable=False)
    kind = Column(String(20), nullable=False, default='notes')
    content = Column(Text, nullable=False, default='')
    url = Column(String(1000), nullable=False, default='')
    storage_key = Column(String(100), nullable=True)

class Assignment(Entity, Base):
    __tablename__ = 'assignments'
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    title = Column(String(150), nullable=False)
    instructions = Column(Text, nullable=False)
    due_at = Column(DateTime, nullable=True)

class Quiz(Entity, Base):
    __tablename__ = 'quizzes'
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    title = Column(String(150), nullable=False)
    status = Column(String(20), nullable=False, default='draft')

class Question(Entity, Base):
    __tablename__ = 'questions'
    quiz_id = Column(Integer, ForeignKey('quizzes.id'), nullable=False)
    prompt = Column(Text, nullable=False)
    options = Column(Text, nullable=False)
    correct_index = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=False)

class Submission(Entity, Base):
    __tablename__ = 'submissions'
    student_id = Column(Integer, ForeignKey('students.user_id'), nullable=False, index=True)
    assignment_id = Column(Integer, ForeignKey('assignments.id'), nullable=True)
    quiz_id = Column(Integer, ForeignKey('quizzes.id'), nullable=True)
    content = Column(Text, nullable=False)
    __table_args__ = (UniqueConstraint('student_id', 'assignment_id'), UniqueConstraint('student_id', 'quiz_id'),
        CheckConstraint('(assignment_id IS NULL) != (quiz_id IS NULL)', name='one_assessment'))

class Grade(Entity, Base):
    __tablename__ = 'grades'
    submission_id = Column(Integer, ForeignKey('submissions.id'), nullable=False, unique=True)
    score = Column(Float, nullable=False)
    feedback = Column(Text, nullable=False, default='')
    grader_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    __table_args__ = (CheckConstraint('score >= 0 AND score <= 100'),)

class LearningActivity(Entity, Base):
    __tablename__ = 'learning_activities'
    student_id = Column(Integer, ForeignKey('students.user_id'), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    action = Column(String(60), nullable=False)
