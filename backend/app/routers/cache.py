# backend/app/routers/cache.py
from fastapi import APIRouter, HTTPException, Header
from fastapi.responses import JSONResponse
from app.cache import clear_session_cache, get_session_cache
import logging
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/init-session")
def init_session(session_id: str = Header(..., alias="session-id")):
    try:
        validate_session_id(session_id)
        clear_session_cache(session_id)
        logger.info(f"세션 {session_id} 초기화 완료")
        return {"message": f"세션 {session_id} 초기화 완료"}
    except Exception as e:
        logger.error(f"세션 초기화 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/session/{session_id}")
def get_session(session_id: str):
    try:
        validate_session_id(session_id)
        cache = get_session_cache(session_id)
        if not cache:
            logger.warning(f"세션 {session_id}: 데이터 없음")
            raise HTTPException(status_code=404, detail="세션 데이터가 없습니다.")
        logger.info(f"세션 {session_id}: 캐시 키 {list(cache.keys())}")
        return {"session_id": session_id, "cache_keys": list(cache.keys())}
    except Exception as e:
        logger.error(f"세션 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

def validate_session_id(session_id: str):
    try:
        uuid.UUID(session_id)
    except ValueError:
        logger.error(f"유효하지 않은 session_id: {session_id}")
        raise HTTPException(status_code=400, detail="유효하지 않은 session_id입니다.") 