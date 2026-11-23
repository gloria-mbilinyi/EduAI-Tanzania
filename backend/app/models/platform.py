from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, UniqueConstraint, CheckConstraint
from ..core.database import Base, Entity

class Recommendation(Entity, Base):
    __tablename__ = 'ai_recommendations'
    student_id = Column(Integer, ForeignKey('students.user_id'), nullable=False, index=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    status = Column(String(25), nullable=False, default='pending_review')
    content = Column(Text, nullable=False)
    reasons = Column(Text, nullable=False)
    version = Column(Integer, nullable=False, default=1)

class RecommendationApproval(Entity, Base):
    __tablename__ = 'recommendation_approvals'
    recommendation_id = Column(Integer, ForeignKey('ai_recommendations.id'), nullable=False)
    teacher_id = Column(Integer, ForeignKey('teachers.user_id'), nullable=False)
    decision = Column(String(20), nullable=False)
    comment = Column(Text, nullable=False)
    version = Column(Integer, nullable=False)

class TutorMessage(Entity, Base):
    __tablename__ = 'tutor_messages'
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    subject = Column(String(60), nullable=False)
    language = Column(String(2), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    source = Column(String(200), nullable=False)

class Notification(Entity, Base):
    __tablename__ = 'notifications'
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    title = Column(String(150), nullable=False)
    body = Column(Text, nullable=False)
    read = Column(Boolean, nullable=False, default=False)

class Message(Entity, Base):
    __tablename__ = 'messages'
    sender_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    recipient_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    student_id = Column(Integer, ForeignKey('students.user_id'), nullable=False)
    body = Column(Text, nullable=False)

class SubscriptionPlan(Entity, Base):
    __tablename__ = 'subscription_plans'
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=True)
    name = Column(String(80), nullable=False)
    price_tzs = Column(Integer, nullable=False)
    days = Column(Integer, nullable=False, default=30)
    premium = Column(Boolean, nullable=False, default=True)
    active = Column(Boolean, nullable=False, default=True)
    __table_args__ = (CheckConstraint('price_tzs > 0 AND days > 0'),)

class Subscription(Entity, Base):
    __tablename__ = 'subscriptions'
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    plan_id = Column(Integer, ForeignKey('subscription_plans.id'), nullable=False)
    status = Column(String(30), nullable=False, default='pending_payment')
    expires_at = Column(DateTime, nullable=True)
    premium = Column(Boolean, nullable=False)

class Payment(Entity, Base):
    __tablename__ = 'payments'
    subscription_id = Column(Integer, ForeignKey('subscriptions.id'), nullable=False, unique=True)
    amount_tzs = Column(Integer, nullable=False)
    currency = Column(String(3), nullable=False, default='TZS')
    provider_reference = Column(String(80), nullable=False, unique=True)
    status = Column(String(30), nullable=False, default='pending')
    verified_at = Column(DateTime, nullable=True)

class ProviderTransaction(Entity, Base):
    __tablename__ = 'provider_transactions'
    reference = Column(String(80), nullable=False, unique=True)
    amount_tzs = Column(Integer, nullable=False)
    currency = Column(String(3), nullable=False)
    outcome = Column(String(20), nullable=False)

class AuditLog(Entity, Base):
    __tablename__ = 'audit_logs'
    actor_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    action = Column(String(100), nullable=False)
    entity = Column(String(100), nullable=False)
    detail = Column(String(500), nullable=False, default='')
