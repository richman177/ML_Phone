from phone_app.config import (SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, ALGORITHM)
from jose import jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta, datetime
from fastapi_limiter.depends import RateLimiter
from phone_app.db.database import SessionLocal
from typing import Optional
from phone_app.db.schema import UserProfileSchema
from phone_app.db.models import UserProfile, RefreshToken
from fastapi import Depends, HTTPException, status, APIRouter
from sqlalchemy.orm import Session

auth_router = APIRouter(prefix='/auth')

oauth2_schema = OAuth2PasswordBearer(tokenUrl='/auth/login/')
password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


async def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({'exp': expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, ):
    return create_access_token(data, expires_delta=timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))


def verify_password(plain_password, hash_password):
    return password_context.verify(plain_password, hash_password)


def get_password_hash(password):
    return password_context.hash(password)


@auth_router.post('/register/', tags=['Авторизация'], summary='Регистрация')
async def register(user: UserProfileSchema, db: Session = Depends(get_db)):
    user_db = db.query(UserProfile).filter(UserProfile.username == user.username).first()
    if user_db:
        raise HTTPException(status_code=400, detail='username бар экен')
    new_hash_pass = get_password_hash(user.password)
    new_user = UserProfile(
        first_name=user.first_name,
        username=user.username,
        phone_number=user.phone_number,
        age=user.age,
        hashed_password=new_hash_pass
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {'message': 'User successfully registered'}


@auth_router.post('/login', dependencies=[Depends(RateLimiter(times=5, seconds=180))],
                  tags=['Авторизация'], summary='Авторизация')
async def login(from_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(UserProfile).filter(UserProfile.username == from_data.username).first()
    if not user or not verify_password(from_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Маалымат туура эмес')
    access_token = create_access_token({'sub': user.username})
    refresh_token = create_refresh_token({'sub': user.username})
    token_db = RefreshToken(token=refresh_token, user_id=user.id)
    db.add(token_db)
    db.commit()
    return {'access_token': access_token, 'refresh_token': refresh_token, 'token_type': 'bearer'}


@auth_router.post('/logout', tags=['Авторизация'], summary='выход из системы')
async def logout(refresh_token: str, db: Session = Depends(get_db)):
    stored_token = db.query(RefreshToken).filter(RefreshToken.token == refresh_token).first()
    if not stored_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detatil='Маалымат туура эмес')
    db.delete(stored_token)
    db.commit()
    return {'message': 'Вышли'}


@auth_router.post('/refresh/', tags=['Авторизация'], summary='Рефреш токен')
async def refresh(refresh_token: str, db: Session = Depends(get_db)):
    token_entry = db.query(RefreshToken).filter_by(token=refresh_token).first()
    if not token_entry:
        raise HTTPException(status_code=401, detail='Маалымат туура эмес')
    access_token = create_access_token({'sub': token_entry.user_id})
    return {'access_token': access_token, 'token_type': 'bearer'}
