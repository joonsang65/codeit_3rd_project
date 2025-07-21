# backend/app/routers/text.py
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated
from sqlmodel import Session
import logging

from app.services.text_modules.text_models import OpenAIClient
from app.services.text_modules.text_prompts import PROMPT_CONFIGS
from app.cache import get_session_cache, update_session_cache
from ...database.connection import get_session
from ...crud import advertisement_crud
from ...schemas.advertisement_schema import AdvertisementCopyCreate

logger = logging.getLogger(__name__)

router = APIRouter()

# 요청 데이터 모델 정의
class TextGenRequest(BaseModel):
    ad_type: str       # instagram / blog / poster
    user_prompt: str   # 사용자 설명
    session_id: str    # 세션 ID

@router.post("/generate")
async def generate_text(req: TextGenRequest, db: Annotated[Session, Depends(get_session)]):
    """사용자 프롬프트와 광고 유형에 따라 광고 문구를 생성하고, 생성된 문구를 데이터베이스에 저장합니다."""
    try:
        # 검증: 지원하지 않는 ad_type 고르기
        if req.ad_type not in PROMPT_CONFIGS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"지원하지 않는 광고 유형입니다: {req.ad_type}")
        
        # 캐시된 데이터 확인 (디버깅용)
        cache = get_session_cache(req.session_id)
        print(f"Session cache for {req.session_id}: {cache.keys()}")


        # advertisement_id가 캐시에 있는지 확인
        advertisement_id = cache.get("advertisement_id")
        if not advertisement_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="세션 캐시에 광고 아이디가 없습니다.")

        # 사용자 프롬프트 저장
        update_session_cache(req.session_id, "user_prompt", req.user_prompt)
        system_prompt, few_shot_examples = PROMPT_CONFIGS[req.ad_type]

        # OpenAI 텍스트 생성
        client = OpenAIClient()
        result = await client.run_generation(
            req.user_prompt,
            system_prompt,
            few_shot_examples
        )

        # 생성된 텍스트 저장
        update_session_cache(req.session_id, "generated_text", result)

        # AdvertisementCopyCreate 스키마 객체 생성
        advertisement_copy_data = AdvertisementCopyCreate(
            ad_copy_text=result,
            ad_type=req.ad_type,
            user_prompt_for_generation=req.user_prompt
        )

        # 광고 문구 데이터베이스에 저장
        advertisement_copy = advertisement_crud.create_advertisement_copy(
            db=db,
            advertisement_id=advertisement_id,
            copy_text=advertisement_copy_data.copy_text,
            ad_type=advertisement_copy_data.ad_type,
            user_prompt_for_generation=advertisement_copy_data.user_prompt_for_generation
        )

        logger.info(f"세션 {req.session_id}: 광고 문구 생성 완료: {advertisement_copy.id}")

        return {"result": result}
    
    except HTTPException:
        db.rollback()
        logger.error(f"세션 {req.session_id}: HTTP 오류 발생: {req.detail}")
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"세션 {req.session_id}: 예외 발생: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"오류 발생: {str(e)}")