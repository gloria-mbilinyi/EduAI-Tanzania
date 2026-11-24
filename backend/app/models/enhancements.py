"""Additive extension: legacy submissions and grades remain unchanged."""
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, ForeignKey, DateTime, UniqueConstraint, CheckConstraint
from ..core.database import Base, Entity

class AssignmentPolicy(Entity, Base):
    __tablename__ = 'assignment_policies'
    assignment_id = Column(Integer, ForeignKey('assignments.id'), nullable=False, unique=True)
    max_attempts = Column(Integer, nullable=False, default=1)
    allow_resubmission = Column(Boolean, nullable=False, default=False)
    allow_late = Column(Boolean, nullable=False, default=False)
    require_feedback = Column(Boolean, nullable=False, default=False)
    require_approval = Column(Boolean, nullable=False, default=False)
    grading_policy = Column(String(20), nullable=False, default='latest')
    __table_args__ = (CheckConstraint('max_attempts BETWEEN 1 AND 20'), CheckConstraint("grading_policy IN ('first','best','latest','selected')"))

class SubmissionAttempt(Entity, Base):
    __tablename__ = 'submission_attempts'
    submission_id = Column(Integer, ForeignKey('submissions.id'), nullable=False, index=True)
    number = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    __table_args__ = (UniqueConstraint('submission_id', 'number'), CheckConstraint('number > 0'))

class AttemptGrade(Entity, Base):
    """Attempts 2+ use this table; attempt 1 retains its original Grade ID."""
    __tablename__ = 'attempt_grades'
    attempt_id = Column(Integer, ForeignKey('submission_attempts.id'), nullable=False, unique=True)
    score = Column(Float, nullable=False)
    feedback = Column(Text, nullable=False)
    grader_id = Column(Integer, ForeignKey('teachers.user_id'), nullable=False)
    __table_args__ = (CheckConstraint('score >= 0 AND score <= 100'),)

class GradeHistory(Entity, Base):
    __tablename__ = 'grade_history'
    attempt_id = Column(Integer, ForeignKey('submission_attempts.id'), nullable=False)
    score = Column(Float, nullable=False)
    feedback = Column(Text, nullable=False)
    grader_id = Column(Integer, ForeignKey('users.id'), nullable=True)

class ResubmissionApproval(Entity, Base):
    __tablename__ = 'resubmission_approvals'
    assignment_id = Column(Integer, ForeignKey('assignments.id'), nullable=False)
    student_id = Column(Integer, ForeignKey('students.user_id'), nullable=False)
    attempt_number = Column(Integer, nullable=False)
    status = Column(String(20), nullable=False, default='pending')
    reason = Column(Text, nullable=False)
    teacher_id = Column(Integer, ForeignKey('teachers.user_id'), nullable=True)
    comment = Column(Text, nullable=False, default='')
    reopen_until = Column(DateTime, nullable=True)

class FinalGradeSelection(Entity, Base):
    __tablename__ = 'final_grade_selections'
    submission_id = Column(Integer, ForeignKey('submissions.id'), nullable=False, unique=True)
    attempt_id = Column(Integer, ForeignKey('submission_attempts.id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('teachers.user_id'), nullable=False)

class RecommendationRevision(Entity, Base):
    __tablename__ = 'recommendation_revisions'
    recommendation_id = Column(Integer, ForeignKey('ai_recommendations.id'), nullable=False)
    version = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    reasons = Column(Text, nullable=False)
    __table_args__ = (UniqueConstraint('recommendation_id', 'version'),)
