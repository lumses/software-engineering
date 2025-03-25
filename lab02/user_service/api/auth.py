from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional
from models.auth import AuthResponse
from jose import JWTError, jwt
from datetime import datetime, timedelta

from .user import users_db
from .dependencies import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, pwd_context


auth_router = APIRouter()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


@auth_router.post(
    '/token',
    summary='Authenticate',
    response_model=AuthResponse,
    responses={
        401: {'description': 'Invalid creds'}
    }
)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    password_check = False
    user = users_db.get(form_data.username)
    if user:
        if pwd_context.verify(form_data.password, user.password):
            password_check = True

    if password_check:
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
        return {"access_token": access_token, "token_type": "bearer"}
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )