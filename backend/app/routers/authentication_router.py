# backend/routers/auth_router.py

import os
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session 
from jose import jwt, JWTError 

from database.connection import get_session 
from crud import user_crud 
from schemas import user_schema as schemas 
from database.models import User as DBUser 
from utils.security import verify_password 

# JWT 설정 
load_dotenv()
SECRET_KEY = os.getenv("JWT_SECRET_KEY") 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 # 60분 이후 토큰 만료

router = APIRouter(prefix="/auth", tags=["Authentication"])

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15) # 15분으로 기본값 설정
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@router.post("/login", response_model=schemas.Token) # 토큰과 토큰 유형을 반환함
async def login_for_access_token(
    user_login: schemas.UserLogin, # JSON 형식의 이메일과 비밀번호를 포함한 요청 본문
    db: Annotated[Session, Depends(get_session)]
):
    user = user_crud.get_user_by_email(db, email=user_login.email)
    
    # 사용자와 비밀번호 검증
    if not user or not verify_password(user_login.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 잘못 입력되었습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 임장 토큰 만료 시간 설정
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, 
        expires_delta=access_token_expires
    )

    # 토큰과 사용자 정보를 반환
    return {"access_token": access_token, "token_type": "bearer", "user": schemas.UserRead.model_validate(user)}