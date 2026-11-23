from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import *
from ..models import *
from ..schemas.common import Registration, Login, ProfileInput
from ..services.access import get, save, record, audit

router = APIRouter(prefix='/api', tags=['identity'])

@router.get('/schools')
def schools(db: Session = Depends(get_db)):
    return [record(s) for s in db.query(School).filter_by(active=True)]

@router.post('/auth/register', status_code=201)
def register(data: Registration, db: Session = Depends(get_db)):
    school = get(db, School, data.school_id)
    if not school.active: raise HTTPException(422, 'School is inactive')
    if db.query(User).filter_by(email=data.email.lower()).first(): raise HTTPException(409, 'Email already registered')
    r = db.query(Role).filter_by(name=data.role).one()
    u = User(name=data.name, email=data.email.lower(), password_hash=hash_password(data.password), role_id=r.id,
             school_id=data.school_id, language=data.language, active=data.role != 'teacher')
    db.add(u)
    db.flush()
    db.add({'student': Student, 'teacher': Teacher, 'parent': Parent}[data.role](user_id=u.id))
    audit(db, u, 'account.register', f'user:{u.id}')
    db.commit()
    return {'user': public_user(db, u), 'message': 'Teacher accounts require school administrator activation' if not u.active else 'Registration complete'}

@router.post('/auth/login')
def login(data: Login, db: Session = Depends(get_db)):
    u = db.query(User).filter_by(email=data.email.lower()).first()
    # A dummy hash comparison keeps unknown-user failures from skipping all hashing work.
    encoded = u.password_hash if u else 'pbkdf2_sha256$600000$invalid$' + '0' * 64
    valid = verify_password(data.password, encoded)
    if not u or not valid or not u.active: raise HTTPException(401, 'Invalid credentials or account awaiting activation')
    audit(db, u, 'account.login', f'user:{u.id}')
    db.commit()
    return {'access_token': token(u), 'token_type': 'bearer', 'user': public_user(db, u)}

@router.get('/me')
def me(u: User = Depends(principal), db: Session = Depends(get_db)):
    s = db.get(Student, u.id)
    return public_user(db, u) | {'profile': record(s) if s else {}}

@router.patch('/me')
def profile(data: ProfileInput, u: User = Depends(principal), db: Session = Depends(get_db)):
    u.name, u.language = data.name, data.language
    s = db.get(Student, u.id)
    if s: s.interests, s.preference = data.interests, data.preference
    save(db, u, u, 'profile.update')
    return me(u, db)
