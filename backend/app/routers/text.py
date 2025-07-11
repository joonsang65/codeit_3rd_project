# backend/app/routers/text.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.text_modules.text_models import OpenAIClient
from app.services.text_modules.text_prompts import PROMPT_CONFIGS

router = APIRouter()

# 요청 데이터 모델 정의
class TextGenRequest(BaseModel):
    ad_type: str       # instagram / blog / poster
    model_type: str    # mini / nano
    user_prompt: str   # 사용자 설명

@router.post("/generate")
async def generate_text(req: TextGenRequest):
    try:
        # 검증: 지원하지 않는 ad_type/model_type 거르기
        if req.ad_type not in PROMPT_CONFIGS:
            raise HTTPException(status_code=400, detail="지원하지 않는 광고 유형입니다.")
        if req.model_type not in ["mini", "nano"]:
            raise HTTPException(status_code=400, detail="지원하지 않는 모델 유형입니다.")
        
        system_prompt, few_shot_examples = PROMPT_CONFIGS[req.ad_type]
        
        # OpenAI 텍스트 생성
        client = OpenAIClient()
        result = await client.run_generation(
            req.model_type,
            req.user_prompt,
            system_prompt,
            few_shot_examples
        )
        
        return {"result": result}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
