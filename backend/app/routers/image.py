# backend/app/routers/image.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Header, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Literal
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
    category: str = Header(...)
):
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        logger.info(f"세션 {session_id}: 이미지 전처리 시작")
        image_main.generator.cfg['paths']['product_image'] = image

        canvas, back_rm_canv, mask = image_main.step1()

        update_session_cache(session_id, "category", category)
        update_session_cache(session_id, "canvas", canvas)
        update_session_cache(session_id, "back_rm_canv", back_rm_canv)
        update_session_cache(session_id, "mask", mask)
        logger.info(f"세션 {session_id}: 캐시에 이미지 저장")

        buffer = io.BytesIO()
        back_rm_canv.save(buffer, format="PNG")
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="image/png")

    except Exception as e:
        logger.error(f"세션 {session_id}: 이미지 전처리 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# generate-background용 모델 정의
class ProductBox(BaseModel):
    x: float
    y: float
    width: float
    height: float

class BackgroundRequest(BaseModel):
    mode: Literal["inpaint"]
    prompt: str
    product_box: ProductBox

@router.post("/generate-background")
async def generate_background(
    request: BackgroundRequest = Body(...),
    session_id: str = Header(..., alias="session-id"),
):
    try:
        cache = get_session_cache(session_id)
        if not cache or "canvas" not in cache or "back_rm_canv" not in cache:
            logger.error(f"세션 {session_id}: 캐시에 필요한 이미지 없음")
            raise HTTPException(status_code=400, detail="세션에 해당하는 이미지가 없습니다. /preprocess 먼저 호출해주세요.")
        
        image_main.generator.category = cache["category"]
        image_main.generator.prompt = request.prompt
        image_main.generator.cfg['product_box'] = {
            "x": request.product_box.x,
            "y": request.product_box.y,
            "width": request.product_box.width,
            "height": request.product_box.height,
        }

        logger.info(f"세션 {session_id}: 배경 생성 시작, 모드: {request.mode}")
        logger.info(f"세션 {session_id}: 프롬프트: {request.prompt}")
        logger.info(f"세션 {session_id}: 제품 박스: {request.product_box}")


        result = image_main.step2(
            mode=request.mode,
            canvas=cache["canvas"],
            mask=cache["mask"]
        )

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