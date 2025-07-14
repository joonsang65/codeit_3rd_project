# backend/app/routers/image.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Header
from fastapi.responses import FileResponse, StreamingResponse
import os
import uuid
import shutil
from app.services import image_main
from PIL import Image
import io

router = APIRouter()

# 사용자별 이미지 캐시 (session_id 기반)
"""
image_session_cache = {
    "session123": {
        "resized_img": PIL.Image,
        "back_rm_canv": PIL.Image,
    },
    ...
}
"""
image_session_cache: dict[str, dict[str, Image.Image]] = {}


# 세션 초기화 엔드포인트
@router.post("/init-session")
def reset_session(session_id: str = Header(..., alias="session-id")):
    if session_id in image_session_cache:
        del image_session_cache[session_id]
        return {"message": "세션 초기화 완료"}
    return {"message": "세션이 존재하지 않습니다."}


# 이미지 전처리 및 배경 제거
@router.post("/preprocess")
async def preprocess_image(
    file: UploadFile = File(...),
    session_id: str = Header(..., alias="session-id"),
):
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")

        resized_img, back_rm_canv = image_main.step1(img=image)

        # 세션별 저장
        image_session_cache[session_id] = {
            "resized_img": resized_img,
            "back_rm_canv": back_rm_canv,
        }

        return {"message": "전처리 완료"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 배경 이미지 생성 (세션 기반 저장만)
@router.post("/generate-background")
async def generate_background(
    mode: str = Form(...),
    session_id: str = Header(..., alias="session-id"),
):
    try:
        if session_id not in image_session_cache:
            raise HTTPException(status_code=400, detail="세션에 해당하는 이미지가 없습니다. /preprocess 먼저 호출해주세요.")

        resized_img = image_session_cache[session_id]["resized_img"]
        back_rm_canv = image_session_cache[session_id]["back_rm_canv"]

        # Step 2 실행 (배경 생성)
        result = image_main.step2(
            mode=mode,
            resized_img=resized_img,
            back_rm_canv=back_rm_canv
        )

        # 생성 결과가 리스트(PIL.Image)일 수 있으므로 적절히 저장
        if isinstance(result, list) and result:
            image_session_cache[session_id]["generated_background"] = result[0]  # 하나만 저장
        elif isinstance(result, Image.Image):
            image_session_cache[session_id]["generated_background"] = result
        else:
            raise HTTPException(status_code=500, detail="이미지 생성 결과가 유효하지 않습니다.")

        return {"message": "배경 이미지 생성 완료"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
from fastapi.responses import StreamingResponse

@router.get("/generated-background")
async def get_generated_background(session_id: str = Header(..., alias="session-id")):
    if session_id not in image_session_cache or "generated_background" not in image_session_cache[session_id]:
        raise HTTPException(status_code=404, detail="배경 이미지가 없습니다.")
    
    image = image_session_cache[session_id]["generated_background"]

    img_bytes = io.BytesIO()
    image.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return StreamingResponse(img_bytes, media_type="image/png")