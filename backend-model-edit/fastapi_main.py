# /ad_project/fastapi_main.py
import accelerate, base64, io, os, sys, time
from dotenv import load_dotenv

# FastAPI 및 관련 모듈.
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Annotated, Any, Dict
from openai import OpenAI

# Schema 경로.
from utils.schema import ImagePreservationRequest, AdCopyGenerationRequest
# 이미지 보전 경로.
from model_dev.main import main as model_dev_main
# 광고 문구 텍스트 생성 경로.
from model_textGen.main import main as text_gen_main

# ********************************* FastAPI 애플리케이션 설정 *********************************
# FastAPI 애플리케이션의 생명주기를 관리하기 위한 컨텍스트 매니저.
@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 애플리케이션의 생명주기 관리."""
    # 환경 변수 불러오기.
    load_dotenv() # .env 파일에서 환경 변수 로드.
    HF_TOKEN = os.getenv("HF_TOKEN")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    llm = OpenAI(api_key = OPENAI_API_KEY)
    print("FastAPI 애플리케이션 시작.")

    yield # 애플리케이션이 실행되는 동안.
    print("FastAPI 애플리케이션 종료.")

# FastAPI 애플리케이션 인스턴스 생성.
app = FastAPI(lifespan = lifespan)

# ********************************* 엔드포인트 정의 *********************************
@app.get("/", description = "루트 엔드포인트. FastAPI 애플리케이션이 작동 중임을 확인합니다.", response_description = "환영 메시지.")
async def read_root():
    """루트 엔드포인트."""
    return {"message": "환영합니다. FastAPI 애플리케이션이 작동 중입니다."}

@app.get("/health", description = "헬스 체크 엔드포인트. 애플리케이션의 상태를 확인합니다.", response_description = "애플리케이션 상태.")
async def health_check():
    """헬스 체크 엔드포인트."""
    return {"status": "정상 작동 중."}

# ********************************* 이미지 보전 *********************************
@app.post("/generate/image-preservation", description = "이미지 보전을 위한 엔드포인트.", response_description = "이미지 보전 결과.")
async def generate_image_preservation(request: ImagePreservationRequest) -> Dict[str, Any]:
    """이미지 보전을 위한 엔드포인트."""
    mode = request.mode
    product_type = request.product_type
    canvas_size = request.canvas_size
    desired_size = request.desired_size
    if mode not in ["inpaint", "text2img"]:
        raise HTTPException(status_code = 400, detail = "유효하지 않은 모드입니다. 'inpaint' 또는 'text2img' 중 하나를 선택하세요.")
    
    # 이미지 보전 모듈 호출.
    try:
        result = model_dev_main(mode = mode, product_type = product_type, canvas_size = canvas_size, desired_size = desired_size)

        # 생성된 이미지를 바이트 스트림으로 변환.
        generated_images_base64 = []
        for image in result:
            # Pillow 이미지를 바이트 스트림으로 변환.
            image_stream = io.BytesIO()
            # 이미지를 PNG 형식으로 저장.
            # Pillow 라이브러리를 사용하여 이미지를 바이트 스트림으로 변환.
            image.save(image_stream, format = "PNG")
            # 스트림의 위치를 처음으로 되돌림.
            image_stream.seek(0)
            # 바이트 스트림을 base64로 인코딩.
            generated_images_base64.append(base64.b64encode(image_stream.read()).decode("utf-8"))

    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"이미지 보전 중 오류가 발생했습니다: {str(e)}")
    
    return {"message": "이미지 보전이 완료되었습니다.", "result": generated_images_base64}

# ********************************* 광고 문구 텍스트 생성 *********************************
@app.post("/generate/ad-copy", description = "광고 문구 텍스트 생성을 위한 엔드포인트.", response_description = "생성된 광고 문구.")
async def generate_ad_copy_text(request: AdCopyGenerationRequest) -> Dict[str, Any]:
    """광고 문구 텍스트 생성을 위한 엔드포인트."""
    ad_type = request.ad_type
    user_prompt = request.user_prompt
    
    if not user_prompt:
        raise HTTPException(status_code = 400, detail = "사용자 입력 프롬프트가 비어 있습니다.")
    
    # 광고 문구 생성 모듈 호출.
    try:
        responses = await text_gen_main(ad_type = ad_type, user_prompt = user_prompt)
        return {"ad_copy": responses}
    
    except Exception as e:
        raise HTTPException(status_code = 500, detail = f"광고 문구 생성 중 오류가 발생했습니다: {str(e)}.")
