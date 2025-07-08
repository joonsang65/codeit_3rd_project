# main.py
# FastAPI 애플리케이션 실행 방법
# 실행: uvicorn main:app --reload


# React는 기본적으로 localhost:3000에서 실행되고, FastAPI는 localhost:8000에서 실행
# 그러므로 CORS 설정을 반드시 해줘야 브라우저가 API 요청을 허용함
from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
import shutil

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 개발 서버 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 결과 이미지 저장 경로 설정
RESULT_DIR = "app/static/results"
os.makedirs(RESULT_DIR, exist_ok=True)

# 정적 파일 서빙 (이미지 접근용)
app.mount("/results", StaticFiles(directory=RESULT_DIR), name="results")

@app.get("/")
def root():
    return {"message": "FastAPI is running!"}

@app.post("/upload/")
async def upload_image(file: UploadFile = File(...)):
    file_path = os.path.join(RESULT_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename, "url": f"/results/{file.filename}"}
