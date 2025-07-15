# backend/app/routers/image.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Header
from fastapi.responses import StreamingResponse
import io
from PIL import Image
from app.services import image_main
from app.cache import get_session_cache, update_session_cache
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/preprocess")
async def preprocess_image(
    file: UploadFile = File(...),
    session_id: str = Header(..., alias="session-id"),
):
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        logger.info(f"세션 {session_id}: 이미지 전처리 시작")

        resized_img, back_rm_canv = image_main.step1(img=image)

        update_session_cache(session_id, "resized_img", resized_img)
        update_session_cache(session_id, "back_rm_canv", back_rm_canv)
        logger.info(f"세션 {session_id}: 캐시에 이미지 저장")

        buffer = io.BytesIO()
        resized_img.save(buffer, format="PNG")
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="image/png")

    except Exception as e:
        logger.error(f"세션 {session_id}: 이미지 전처리 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-background")
async def generate_background(
    mode: str = Form(...),
    session_id: str = Header(..., alias="session-id"),
):
    try:
        cache = get_session_cache(session_id)
        if not cache or "resized_img" not in cache or "back_rm_canv" not in cache:
            logger.error(f"세션 {session_id}: 캐시에 필요한 이미지 없음")
            raise HTTPException(status_code=400, detail="세션에 해당하는 이미지가 없습니다. /preprocess 먼저 호출해주세요.")

        resized_img = cache["resized_img"]
        back_rm_canv = cache["back_rm_canv"]
        logger.info(f"세션 {session_id}: 배경 생성 시작, 모드: {mode}")

        result = image_main.step2(mode=mode, resized_img=resized_img, back_rm_canv=back_rm_canv)

        if isinstance(result, list) and result:
            update_session_cache(session_id, "generated_background", result[0])
        elif isinstance(result, Image.Image):
            update_session_cache(session_id, "generated_background", result)
        else:
            logger.error(f"세션 {session_id}: 유효하지 않은 이미지 생성 결과")
            raise HTTPException(status_code=500, detail="이미지 생성 결과가 유효하지 않습니다.")

        logger.info(f"세션 {session_id}: 배경 이미지 생성 완료")
        return {"message": "배경 이미지 생성 완료"}

    except Exception as e:
        logger.error(f"세션 {session_id}: 배경 생성 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/generated-background")
async def get_generated_background(session_id: str = Header(..., alias="session-id")):
    try:
        cache = get_session_cache(session_id)
        if not cache or "generated_background" not in cache:
            logger.error(f"세션 {session_id}: 배경 이미지 없음")
            raise HTTPException(status_code=404, detail="배경 이미지가 없습니다.")

        image = cache["generated_background"]
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)
        logger.info(f"세션 {session_id}: 배경 이미지 반환")
        return StreamingResponse(img_bytes, media_type="image/png")

    except Exception as e:
        logger.error(f"세션 {session_id}: 배경 이미지 조회 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))