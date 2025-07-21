# backend/app/main.py
# 실행 : uvicorn app.main:app --reload

import os
import sys
from dotenv import load_dotenv
load_dotenv()
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.abspath('./backend'))
import signal
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import image, text, cache, TI
from app.cache import clear_session_cache, get_all_session_ids
from app.services.image_main import generator

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(image.router, prefix="/image")
app.include_router(text.router, prefix="/text")
app.include_router(cache.router, prefix="/cache")
app.include_router(TI.router, prefix="/text-image")

@app.on_event("startup")
async def startup_event():
    print("FastAPI 서버 시작")
    print(f"현재 세션: {get_all_session_ids()}")

@app.on_event("shutdown")
async def shutdown_event():
    print("FastAPI 서버 종료")
    for session_id in get_all_session_ids():
        clear_session_cache(session_id)
    print("세션 캐시 정리 완료")
    generator.cleanup()

@app.get("/")
async def root():
    return {"message": "FastAPI server running"}

def handle_shutdown(loop):
    tasks = [task for task in asyncio.all_tasks(loop) if task is not asyncio.current_task()]
    for task in tasks:
        task.cancel()
    loop.stop()
    loop.run_until_complete(loop.shutdown_asyncgens())
    loop.close()

def setup_signal_handlers():
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, handle_shutdown, loop)

if __name__ == "__main__":
    import uvicorn
    setup_signal_handlers()
    uvicorn.run(app, host="0.0.0.0", port=8000)