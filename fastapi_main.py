# /ad_project/fastapi_main.py
import accelerate, base64, io, os, sys, time
from dotenv import load_dotenv
from huggingface_hub import notebook_login

# FastAPI 및 관련 모듈.
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Annotated, Any, Dict
from openai import OpenAI

# OmniGen2 경로 설정.
omnigen2_path = os.path.join(os.path.dirname(__file__), "OmniGen2")
if omnigen2_path not in sys.path:
    sys.path.append(omnigen2_path)

# Schema 경로.
from utils.schema import AdvertisementGenerationRequest, ImagePreservationRequest, AdCopyGenerationRequest

# 이미지 생성 경로.
from rag_pipeline.config.config import INSTAGRAM, POSTER, MODEL_PATH
from rag_pipeline.utils.timing_utils import timing_decorator
# 번역 모듈.
from rag_pipeline.translation.prompt_translator import translate_korean_to_english
from rag_pipeline.translation.description_translator import translate_english_to_korean
# 키워드 추출 모듈.
from rag_pipeline.keyword_extraction.extractor import extract_keywords
# 프롬프트 생성 모듈.
from rag_pipeline.prompting.initial_prompt_generator import generate_initial_prompt
from rag_pipeline.prompting.prompt_refiner import refine_prompt_with_content
from rag_pipeline.prompting.negative_prompt_generator import generate_negative_prompt
# 웹 도구 모듈.
from rag_pipeline.web_tools.search import perform_web_search
from rag_pipeline.web_tools.content_processor import fetch_and_process_content
# 모델 모듈.
from rag_pipeline.core.models import initialize_pipelines
# 이미지 생성 및 시각적 이해 모듈.
from rag_pipeline.image_generation.generator import generate_image
from rag_pipeline.image_generation.visual_analyzer import analyze_image
# 광고 문구 생성 모듈.
from rag_pipeline.advertisement.copy_generator import generate_ad_copy

# 이미지 보전 경로.
from model_dev.main import main as model_dev_main

# 광고 문구 텍스트 생성 경로.
from model_textGen.main import main as text_gen_main

# ********************************* FastAPI 애플리케이션 설정 *********************************
# FastAPI 애플리케이션의 생명주기를 관리하기 위한 컨텍스트 매니저.
@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI 애플리케이션의 생명주기 관리."""
    print("FastAPI 애플리케이션 시작.")
    yield # 애플리케이션이 실행되는 동안.
    print("FastAPI 애플리케이션 종료.")

# FastAPI 애플리케이션 인스턴스 생성.
app = FastAPI(lifespan = lifespan)

# ********************************* 환경 변수 및 API 키 설정 *********************************
# 환경 변수 불러오기.
load_dotenv() # .env 파일에서 환경 변수 로드.
HF_TOKEN = os.getenv("HF_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

notebook_login() # Hugging Face 로그인.
llm = OpenAI(api_key = OPENAI_API_KEY)

# 모델 파이프라인 초기화.
accelerator = accelerate.Accelerator()
diffusion_pipeline, chat_pipeline = initialize_pipelines(model_path = MODEL_PATH, hf_token = HF_TOKEN, accelerator = accelerator)

# ********************************* 엔드포인트 정의 *********************************
@app.get("/", description = "루트 엔드포인트. FastAPI 애플리케이션이 작동 중임을 확인합니다.", response_description = "환영 메시지.")
async def read_root():
    """루트 엔드포인트."""
    return {"message": "환영합니다. FastAPI 애플리케이션이 작동 중입니다."}

@app.get("/health", description = "헬스 체크 엔드포인트. 애플리케이션의 상태를 확인합니다.", response_description = "애플리케이션 상태.")
async def health_check():
    """헬스 체크 엔드포인트."""
    return {"status": "정상 작동 중."}

# ********************************* 텍스트-이미지 생성 *********************************
@timing_decorator
@app.post("/generate/text-to-image", description = "텍스트 프롬프트를 기반으로 이미지를 생성합니다.", response_description = "생성된 이미지 Image.Image 객체.")
async def generate_text_to_image(request: AdvertisementGenerationRequest) -> Dict[str, Any]:
    """텍스트 프롬프트를 기반으로 이미지를 생성합니다."""
    korean_prompt = request.korean_prompt
    image_size = request.image_size
    num_images = request.num_images
    
    if not korean_prompt:
        raise HTTPException(status_code = 400, detail = "한국어 프롬프트가 비어 있습니다.")
    
    # 한국어 프롬프트를 영어로 번역.
    translated_prompt = translate_korean_to_english(llm, korean_prompt)
    if not translated_prompt:
        raise HTTPException(status_code = 500, detail = "번역 중 오류가 발생했습니다.")
    
    # 초기 프롬프트 생성.
    initial_prompt = generate_initial_prompt(llm, translated_prompt)
    if not initial_prompt:
        raise HTTPException(status_code = 500, detail = "초기 프롬프트 생성 중 오류가 발생했습니다.")
    
    # 키워드 추출.
    keywords = extract_keywords(llm, initial_prompt)
    if not keywords:
        raise HTTPException(status_code = 404, detail = "키워드를 추출할 수 없습니다.")

    # 웹 검색 및 콘텐츠 추출.
    search_results = perform_web_search(keywords, num_results = 5)
    if not search_results:
        raise HTTPException(status_code = 404, detail = "검색 결과를 찾을 수 없습니다.")
    
    # 콘텐츠 처리 및 정보 추출.
    content = fetch_and_process_content(llm, search_results, keywords)
    if not content:
        raise HTTPException(status_code = 404, detail = "콘텐츠를 추출할 수 없습니다.")
    
    # 프롬프트 개선.
    refined_prompt = refine_prompt_with_content(llm, initial_prompt, content)
    if not refined_prompt:
        raise HTTPException(status_code = 500, detail = "프롬프트 개선 중 오류가 발생했습니다.")

    # 부정 프롬프트 생성.
    negative_prompt = generate_negative_prompt(llm, refined_prompt)
    if not negative_prompt:
        raise HTTPException(status_code = 500, detail = "부정 프롬프트 생성 중 오류가 발생했습니다.")
    
    # 이미지 생성.
    image_size_tuple = INSTAGRAM if image_size == "INSTAGRAM" else POSTER
    generated_image_list = generate_image(diffusion_pipeline, refined_prompt, negative_prompt, accelerator, image_size_tuple[0], image_size_tuple[1], num_images)
    if not generated_image_list:
        raise HTTPException(status_code = 500, detail = "이미지 생성 중 오류가 발생했습니다.")

    # 이미지 분석.
    english_image_description = analyze_image(chat_pipeline, generated_image_list, accelerator)
    if not english_image_description:
        raise HTTPException(status_code = 500, detail = "이미지 분석 중 오류가 발생했습니다.")
    
    # 이미지 설명을 한국어로 번역.
    korean_image_description = translate_english_to_korean(llm, english_image_description)
    if not korean_image_description:
        raise HTTPException(status_code = 500, detail = "이미지 설명 번역 중 오류가 발생했습니다.")
    
    # 광고 문구 생성.
    ad_copy = generate_ad_copy(llm, korean_prompt, korean_image_description)
    if not ad_copy:
        raise HTTPException(status_code = 500, detail = "광고 문구 생성 중 오류가 발생했습니다.")

    # 생성된 이미지를 바이트 스트림으로 변환.
    generated_images_base64 = []
    for image in generated_image_list:
        # Pillow 이미지를 바이트 스트림으로 변환.
        image_stream = io.BytesIO()
        # 이미지를 PNG 형식으로 저장.
        # Pillow 라이브러리를 사용하여 이미지를 바이트 스트림으로 변환.
        image.save(image_stream, format = "PNG")
        # 스트림의 위치를 처음으로 되돌림.
        image_stream.seek(0)
        # 바이트 스트림을 base64로 인코딩.
        generated_images_base64.append(base64.b64encode(image_stream.read()).decode("utf-8"))
    
    print(f"생성된 이미지 수: {len(generated_images_base64)}.")
    # JSON 응답으로 반환할 데이터 구성.
    return {
        "advertisement_image": generated_images_base64,
        "advertisment_copy": ad_copy,
        "image_description": korean_image_description
    }

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
