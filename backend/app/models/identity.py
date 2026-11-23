from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from ..core.database import Base, Entity

class Role(Entity, Base):
    __tablename__ = 'roles'
    name = Column(String(20), nullable=False, unique=True)

class School(Entity, Base):
    __tablename__ = 'schools'
    name = Column(String(150), nullable=False)
    region = Column(String(80), nullable=False)
    active = Column(Boolean, nullable=False, default=True)

class User(Entity, Base):
    __tablename__ = 'users'
    email = Column(String(254), nullable=False, unique=True, index=True)
    name = Column(String(100), nullable=False)
    password_hash = Column(String(300), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=False, index=True)
    active = Column(Boolean, nullable=False, default=True)
    language = Column(String(2), nullable=False, default='en')

class Student(Base):
    __tablename__ = 'students'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    form = Column(String(20), nullable=False, default='Form 2')
    interests = Column(String(200), nullable=False, default='Science')
    preference = Column(String(20), nullable=False, default='reading')

class Teacher(Base):
    __tablename__ = 'teachers'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    specialization = Column(String(100), nullable=False, default='General studies')

class Parent(Base):
    __tablename__ = 'parents'
    user_id = Column(Integer, ForeignKey('users.id'), primary_key=True)

class ParentStudentLink(Entity, Base):
    __tablename__ = 'parent_student_links'
    parent_id = Column(Integer, ForeignKey('parents.user_id'), nullable=False)
    student_id = Column(Integer, ForeignKey('students.user_id'), nullable=False)
    status = Column(String(20), nullable=False, default='pending')
    __table_args__ = (UniqueConstraint('parent_id', 'student_id'),)
