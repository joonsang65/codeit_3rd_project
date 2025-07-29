# backend/app/main.py
# 실행 : uvicorn app.main:app --reload

import asyncio, logging, os, sys
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pydantic import BaseModel

load_dotenv()

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath('./backend'))

from database.connection import create_db_and_tables

from .routers import image, text, session_router, user_router, advertisement_router, authentication_router, TI
from schemas import session_schema, user_schema, advertisement_schema
from .services.image_main import generator

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] [%(name)s] - %(message)s')

# 수명 주기 관리
@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("FastAPI 서범 시작")
    try:
        create_db_and_tables()
        logging.info("데이터베이스 테이블 생성 완료")
    except Exception as e:
        logging.error(f"데이터베이스 생성 실패: {e}")

    yield 

    logging.info("FastAPI 서버 종료 중...")
    try:
        generator.cleanup()
        logging.info("이미지 생성기 정리 완료")
    except Exception as e:
        logging.error(f"이미지 생성기 정리 중 오류 발생: {e}")

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(lifespan=lifespan)

# CORS (Cross-Origin Resource Sharing) Middleware
# 허용된 오리진 목록을 설정
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://34.135.93.123:3000",
    "http://34.135.93.123:3001",
    "http://34.135.93.123:3002"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 디렉토리 경로 설정 및 정적 파일 서빙
STATIC_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))
os.makedirs(STATIC_ROOT_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_ROOT_DIR), name="static")

# *************************************** 라우터 설정 ***************************************
app.include_router(image.router)
app.include_router(text.router) 
app.include_router(TI.router)

# 데이터베이스 라우터
app.include_router(user_router.router)
app.include_router(advertisement_router.router)
app.include_router(session_router.router)
app.include_router(authentication_router.router)

# *************************************** Pydantic 모델 재구성 ***************************************
try:
    all_pydantic_models = {}
    schema_modules_to_scan = [
        session_schema,
        user_schema,
        advertisement_schema
    ]
    for module in schema_modules_to_scan:
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and issubclass(obj, BaseModel) and obj is not BaseModel:
                all_pydantic_models[name] = obj

    for model_name, pydantic_model_class in all_pydantic_models.items():
        if hasattr(pydantic_model_class, "model_rebuild"):
            try:
                pydantic_model_class.model_rebuild(_types_namespace=all_pydantic_models)
                logging.info(f"Pydantic model rebuild successful: {model_name}")
            except Exception as rebuild_e:
                logging.error(f"Pydantic model rebuild failed: {model_name}, Error: {rebuild_e}")
                raise 
    logging.info("All Pydantic models rebuilt successfully.")
except Exception as e:
    logging.critical(f"Fatal error during Pydantic model rebuilding: {e}")
    raise

# 루트 엔드포인트 
@app.get("/")
async def root():
    """서버가 실행 중임을 확인하는 간단한 메시지를 반환합니다."""
    return {"message": "FastAPI에 환영합니다. FastAPI 서버가 실행 중입니다."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)