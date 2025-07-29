# backend/app/routers/text.py
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from typing import Annotated 
from sqlmodel import Session
import logging

from app.services.text_modules.text_models import OpenAIClient
from app.services.text_modules.text_prompts import PROMPT_CONFIGS

from database.connection import get_session
from crud import advertisement_crud, session_crud
from schemas.advertisement_schema import AdvertisementCopyCreate 

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/text", tags=["Text Generation"])

# Combined Request Data Model
class TextGenRequest(BaseModel):
    ad_type: str        # instagram / blog / poster
    model_type: str     # mini / nano
    user_prompt: str    # 사용자 설명
    session_id: str     # 세션 아이디

@router.post("/generate")
async def generate_text(req: TextGenRequest, db: Annotated[Session, Depends(get_session)]):
    """사용자 프롬프트와 광고 유형에 따라 광고 문구를 생성하고, 생성된 문구를 데이터베이스에 저장합니다."""
    try:
        if req.ad_type not in PROMPT_CONFIGS:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"지원하지 않는 광고 유형입니다: {req.ad_type}")
        if req.model_type not in ["mini", "nano"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"지원하지 않는 모델 유형입니다: {req.model_type}")
        
        db_session_entry = session_crud.get_session_by_id(db, req.session_id)
        if not db_session_entry or not db_session_entry.session_data:
            logger.error(f"세션 {req.session_id}: 데이터베이스에 세션 데이터 없음")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="세션 데이터를 찾을 수 없습니다. 이미지 전처리 또는 이전 단계가 먼저 호출되어야 합니다.")

        session_data = db_session_entry.session_data

        advertisement_id = session_data.get("advertisement_id")
        if not advertisement_id:
            logger.error(f"세션 {req.session_id}: 세션 데이터에 광고 아이디가 없습니다.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="세션에 광고 아이디가 없습니다. 이미지 배경 생성 단계가 먼저 완료되어야 합니다.")

        session_data["user_prompt"] = req.user_prompt
        # 세션 데이터 업데이트
        session_crud.update_session_data(db, db_session_entry, session_data) 
        logger.info(f"세션 {req.session_id}: 사용자 프롬프트 세션에 저장됨.")

        system_prompt, few_shot_examples = PROMPT_CONFIGS[req.ad_type]

        client = OpenAIClient()
        result = await client.run_generation(
            req.model_type,
            req.user_prompt,
            system_prompt,
            few_shot_examples
        )

        session_data["generated_text"] = result
        # 세션 데이터 업데이트
        session_crud.update_session_data(db, db_session_entry, session_data)
        logger.info(f"세션 {req.session_id}: 광고 문구 생성 완료 및 세션에 저장: {result}")

        extracted_copy_text = ""
        if result and isinstance(result, list) and len(result) > 0 and isinstance(result[0], tuple) and len(result[0]) > 1:
            extracted_copy_text = result[0][1] # 첫 요소의 두 번째 값을 추출
        else:
            logger.warning(f"세션 {req.session_id}: 생성된 문구 결과가 예상 형식과 다릅니다. {result}")

        print(f"PRINTING EXTRACTED COPY TEXT: {extracted_copy_text}")
        # AdvertisementCopyCreate 스키마 객체 생성
        advertisement_copy_data = AdvertisementCopyCreate(
            copy_text=extracted_copy_text,
            ad_type=req.ad_type,
            user_prompt_for_generation=req.user_prompt
        )

        # 데이터베이스에 광고 문구 저장
        advertisement_copy = advertisement_crud.create_advertisement_copy(
            db=db,
            advertisement_id=advertisement_id,
            copy_text=advertisement_copy_data.copy_text,
            ad_type=advertisement_copy_data.ad_type,
            user_prompt_for_generation=advertisement_copy_data.user_prompt_for_generation
        )

        logger.info(f"세션 {req.session_id}: 광고 문구 데이터베이스에 저장 완료: {advertisement_copy.id}")

        return {"result": result}
    
    except HTTPException:
        logger.error(f"세션 {req.session_id}: HTTP 오류 발생") # req.detail is not available here, log actual exception detail if possible
        raise
    except Exception as e:
        db.rollback() 
        logger.error(f"세션 {req.session_id}: 예외 발생: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"오류 발생: {str(e)}")