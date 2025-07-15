# backend/app/routers/text.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.text_modules.text_models import OpenAIClient
from app.services.text_modules.text_prompts import PROMPT_CONFIGS
from app.cache import get_session_cache, update_session_cache

router = APIRouter()

# 요청 데이터 모델 정의
class TextGenRequest(BaseModel):
    ad_type: str       # instagram / blog / poster
    model_type: str    # mini / nano
    user_prompt: str   # 사용자 설명
    session_id: str    # 세션 ID

@router.post("/generate")
async def generate_text(req: TextGenRequest):
    try:
        # 검증: 지원하지 않는 ad_type/model_type 거르기
        if req.ad_type not in PROMPT_CONFIGS:
            raise HTTPException(status_code=400, detail=f"지원하지 않는 광고 유형입니다: {req.ad_type}")
        if req.model_type not in ["mini", "nano"]:
            raise HTTPException(status_code=400, detail=f"지원하지 않는 모델 유형입니다: {req.model_type}")

        # 캐시된 데이터 확인 (디버깅용)
        cache = get_session_cache(req.session_id)
        print(f"Session cache for {req.session_id}: {cache.keys()}")

        # 사용자 프롬프트 저장
        update_session_cache(req.session_id, "user_prompt", req.user_prompt)

        system_prompt, few_shot_examples = PROMPT_CONFIGS[req.ad_type]

        # OpenAI 텍스트 생성
        client = OpenAIClient()
        result = await client.run_generation(
            req.model_type,
            req.user_prompt,
            system_prompt,
            few_shot_examples
        )

        # 생성된 텍스트 저장
        update_session_cache(req.session_id, "generated_text", result)

        return {"result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))