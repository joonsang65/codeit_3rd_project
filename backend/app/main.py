# backend/app/main.py
# 실행 : uvicorn app.main:app --reload

import asyncio, os, signal, sys
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath('./backend'))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

from app.routers import image, text, cache as cache_router_from_app_routers
from app.routers import advertisement_router, session_router, user_router 
from .cache import clear_session_cache, get_all_session_ids
from services.image_main import generator

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("FastAPI 서버 시작")
    print(f"현재 세션 아이디: {get_all_session_ids()}")
    yield
    print("FastAPI 서버 종료")
    for session_id in get_all_session_ids():
        clear_session_cache(session_id)
    print("세션 캐시 정리 완료")
    generator.cleanup()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

STATIC_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "static"))
os.makedirs(STATIC_ROOT_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_ROOT_DIR), name="static")

app.include_router(image.router, prefix="/image")
app.include_router(text.router, prefix="/text")
app.include_router(cache_router_from_app_routers.router, prefix="/cache")
# 데이터베이스 관련 라우터
app.include_router(user_router.router, prefix="/users")
app.include_router(advertisement_router.router, prefix="/advertisements")
app.include_router(session_router.router, prefix="/sessions")

@app.get("/")
async def root():
    return {"message": "FastAPI server running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)