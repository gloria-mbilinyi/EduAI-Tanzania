import hashlib
import hmac
import secrets
from datetime import timedelta
import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from .config import JWT_SECRET
from .database import get_db, now
from ..models import User, Role

bearer = HTTPBearer(auto_error=False)
def hash_password(password: str):
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 600000).hex()
    return f'pbkdf2_sha256$600000${salt}${digest}'

def verify_password(password: str, stored: str):
    try:
        _, iterations, salt, expected = stored.split('$')
        actual = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), int(iterations)).hex()
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False

def token(user: User):
    return jwt.encode({'sub': str(user.id), 'exp': now() + timedelta(hours=2), 'iat': now()}, JWT_SECRET, algorithm='HS256')

def principal(credential: HTTPAuthorizationCredentials | None = Depends(bearer), db: Session = Depends(get_db)):
    try:
        if not credential: raise ValueError()
        payload = jwt.decode(credential.credentials, JWT_SECRET, algorithms=['HS256'], options={'require': ['exp', 'sub', 'iat']})
        user = db.get(User, int(payload['sub']))
        if not user or not user.active: raise ValueError()
        return user
    except (jwt.PyJWTError, ValueError, TypeError):
        raise HTTPException(401, 'Authentication required', headers={'WWW-Authenticate': 'Bearer'})

def role(db, user):
    return db.get(Role, user.role_id).name

def require(db, user, *allowed):
    if role(db, user) not in allowed: raise HTTPException(403, 'Role not permitted')

def public_user(db, user):
    return {key: getattr(user, key) for key in ['id', 'email', 'name', 'school_id', 'language', 'active']} | {'role': role(db, user)}
