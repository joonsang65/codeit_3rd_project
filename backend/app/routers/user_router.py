# backend/routers/user_router.py
from typing import Optional, List, Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session 

from database.connection import get_session # 데이터베이스 연결 함수
from crud import user_crud # 사용자 CRUD 함수
from schemas import user_schema as schemas # Pydantic 사용자 스키마
from database.models import User as DBUser # SQLModel 사용자 클래
from utils.security import get_password_hash # 비밀번호 암호화 함수 

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    user: schemas.UserCreate,
    db: Annotated[Session, Depends(get_session)]
) -> DBUser:
    """새로운 사용자를 생성합니다."""
    # 사용자 이미 존재 여부 확인
    existing_user = user_crud.get_user_by_email(db, email=user.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="이메일 이미 사용 중입니다"
        )

    # 비밀번호 암호화 유틸리티 함수 사용
    hashed_password = get_password_hash(user.password)

    # 사용자 객체 데이터베이스 생성.
    db_user = user_crud.create_user(
        db,
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    return db_user

@router.get("/{user_id}", response_model=schemas.UserRead)
async def read_user(
    user_id: int,
    db: Annotated[Session, Depends(get_session)]
) -> DBUser:
    """사용자 아이디로 사용자 정보를 조회합니다."""
    db_user = user_crud.get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자 존재하지 않습니다"
        )
    return db_user

@router.put("/{user_id}", response_model=schemas.UserRead)
async def update_user_data(
    user_id: int,
    user_update: schemas.UserUpdate,
    db: Annotated[Session, Depends(get_session)]
) -> DBUser:
    """사용자 정보를 업데이트합니다."""
    db_user = user_crud.get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자 존재하지 않습니다"
        )
    # 비밀번호 암호화 함수 사용
    hashed_password = None
    if user_update.password:
        hashed_password = get_password_hash(user_update.password) 
        
    updated_user = user_crud.update_user(
        db, 
        user_entry=db_user,
        new_username=user_update.username,
        new_email=user_update.email,
        new_hashed_password=hashed_password
    )
    return updated_user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_data(
    user_id: int,
    db: Annotated[Session, Depends(get_session)]
) -> Response:
    """사용자 정보를 삭제합니다."""
    success = user_crud.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="사용자 존재하지 않습니다"
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)