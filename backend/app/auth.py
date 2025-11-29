from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db

# Password hashing context
# Note: bcrypt 5.0+ requires explicit truncation for long passwords
pwd_context = CryptContext(
    schemes=['bcrypt'],
    deprecated='auto',
    bcrypt__rounds=12,
    bcrypt__truncate_error=False,
)

# HTTP Bearer security scheme
security = HTTPBearer()

# Token type constants
TOKEN_TYPE_ACCESS = 'access'
TOKEN_TYPE_REFRESH = 'refresh'

# Token expiration settings
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour
REFRESH_TOKEN_EXPIRE_DAYS = 7  # 7 days


def hash_password(password: str) -> str:
    '''Hash a password using bcrypt'''
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    '''Verify a password against its hash'''
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    '''Create a JWT access token'''
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode = {
        'sub': str(user_id),
        'type': TOKEN_TYPE_ACCESS,
        'exp': expire,
    }
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def create_refresh_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    '''Create a JWT refresh token'''
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    to_encode = {
        'sub': str(user_id),
        'type': TOKEN_TYPE_REFRESH,
        'exp': expire,
    }
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    '''Decode a JWT token'''
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        return payload
    except JWTError:
        return None


def verify_access_token(token: str) -> Optional[str]:
    '''Verify an access token and return the user_id if valid'''
    payload = decode_token(token)
    if payload is None:
        return None
    if payload.get('type') != TOKEN_TYPE_ACCESS:
        return None
    return payload.get('sub')


def verify_refresh_token(token: str) -> Optional[str]:
    '''Verify a refresh token and return the user_id if valid'''
    payload = decode_token(token)
    if payload is None:
        return None
    if payload.get('type') != TOKEN_TYPE_REFRESH:
        return None
    return payload.get('sub')


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UUID:
    '''
    Dependency to get the current authenticated user's ID from the JWT token.
    Raises HTTPException if token is invalid or expired.
    '''
    token = credentials.credentials
    user_id = verify_access_token(token)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid or expired token',
            headers={'WWW-Authenticate': 'Bearer'},
        )

    try:
        return UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid token payload',
            headers={'WWW-Authenticate': 'Bearer'},
        )


def get_current_user(
    user_id: UUID = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    '''
    Dependency to get the current authenticated user from the database.
    Raises HTTPException if user is not found.
    '''
    from app.models import User  # Import here to avoid circular imports

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='User not found',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return user
