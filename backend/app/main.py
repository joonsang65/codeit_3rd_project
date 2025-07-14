# backend/app/main.py
# 실행 명령: uvicorn app.main:app --reload
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import image, text

# .env 파일에서 환경 변수 로드
load_dotenv()  # .env 1회 로드
# 그 이후부턴 os.getenv("OPENAI_API_KEY")만 쓰면 됨

app = FastAPI()

# CORS 허용 (React와 통신 위해 필요)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 추후 특정 도메인만 허용해도 됨
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(image.router, prefix="/image", tags=["Image"])
app.include_router(text.router, prefix="/text", tags=["Text"])
