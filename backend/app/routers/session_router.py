# backend/routers/session_router.py
import logging
from typing import Annotated, Optional, Dict, Any
from fastapi import APIRouter, Header, Depends, HTTPException, status
from fastapi.responses import JSONResponse 
from sqlmodel import Session

from ...database.connection import get_session 
from ...crud import session_crud, user_crud # 데이터베이스 CRUD 함수
from ...schemas import session_schema as schemas # Pydantic 세션 스키마
from ...database.models import Session as DBSession # SQLModel 데이터베이스 객체
from ..cache import clear_session_cache

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.post("/init", response_model=schemas.SessionResponse, status_code=status.HTTP_201_CREATED)
async def init_session(
    session_id: Annotated[str, Header(alias="session-id", description="React 앱에서 사용하는 고유 식별자입니다.")],
    db: Annotated[Session, Depends(get_session)],
    user_id: Annotated[Optional[int], Header(alias="user-id", description="로그인한 사용자의 선택적 아이디입니다.", default=None)] = None
) -> DBSession:
    """새로운 세션을 초기화하거나 기존 세션을 업데이트합니다."""
    try:
        # 세션 아이디 유효성 검사
        existing_session = session_crud.get_session_by_id(db, session_id)

        if existing_session:
            # 세션이 이미 존재하는 경우
            if user_id is not None and existing_session.user_id != user_id:
                # user_id가 제공되었고, 기존 세션의 user_id와 다를 경우
                existing_session.user_id = user_id
                updated_session = session_crud.update_session_timestamp(db, existing_session) 
                clear_session_cache(session_id)
                logger.info(f"세션 {session_id} 업데이트: user_id 변경됨")
                return updated_session 
            else:
                updated_session = session_crud.update_session_timestamp(db, existing_session)
                clear_session_cache(session_id)
                logger.info(f"세션 {session_id} 업데이트: timestamp 갱신됨")
                return updated_session 
        else:
            # 새로운 세션 생성
            new_session = session_crud.create_new_session(db, session_id=session_id, user_id=user_id)
            clear_session_cache(session_id)
            logger.info(f"새로운 세션 {session_id} 생성됨")
            return new_session
            
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"세션 초기화/업데이트 실패: {str(e)}")


@router.get("/{session_id}", response_model=schemas.SessionResponse)
async def get_session_data(
    session_id: str,
    db: Annotated[Session, Depends(get_session)]
) -> DBSession:
    """세션 아이디로 세션 데이터를 조회합니다."""
    try:
        session_entry = session_crud.get_session_by_id(db, session_id)
        if not session_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="세션 데이터가 없습니다"
            )
        return session_entry
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"세션 데이터 조회 실패: {str(e)}")

@router.patch("/{session_id}/data", response_model=schemas.SessionResponse)
async def update_session_data_endpoint(
    session_id: str,
    data: Dict[str, Any],
    db: Annotated[Session, Depends(get_session)]
) -> DBSession:
    """세션 아이디로 세션 데이터를 업데이트합니다."""
    try:
        session_entry = session_crud.get_session_by_id(db, session_id)
        if not session_entry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="세션이 존재하지 않습니다."
            )
        updated_session = session_crud.update_session_data(db, session_entry, data)
        return updated_session
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"세션 데이터 업데이트 실패: {str(e)}")