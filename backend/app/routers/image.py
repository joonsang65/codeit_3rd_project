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

        back_rm = image_main.step1()

        update_session_cache(session_id, "category", category)
        update_session_cache(session_id, "back_rm", back_rm)
        # update_session_cache(session_id, "back_rm_canv", back_rm_canv)
        # update_session_cache(session_id, "mask", mask)
        logger.info(f"세션 {session_id}: 캐시에 이미지 저장")

        buffer = io.BytesIO()
        back_rm.save(buffer, format="PNG")
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="image/png")

    except Exception as e:
        logger.error(f"세션 {session_id}: 이미지 전처리 실패: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# generate-background용 모델 정의
class ProductBox(BaseModel):
    canvas_type: str
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
        if not cache or "back_rm" not in cache:
            logger.error(f"세션 {session_id}: 캐시에 필요한 이미지 없음")
            raise HTTPException(status_code=400, detail="세션에 해당하는 이미지가 없습니다. /preprocess 먼저 호출해주세요.")
        
        image_main.generator.category = cache["category"]
        if request:
            image_main.generator.marketing_type = request.prompt
            size_info = (int(request.product_box.width), int(request.product_box.height))
            position = (int(request.product_box.x), int(request.product_box.y))
        else:
            logger.info("request가 없습니다.")
            size_info = (128, 128)
            position = (300, 220)
        image_main.generator.cfg['image_config']['resize_info'] = size_info
        image_main.generator.cfg['image_config']['position'] = position
        image_main.generator.cfg['canvas_type'] = request.product_box.canvas_type
                
        print(f"***************캔버스 타입: {image_main.generator.cfg['canvas_type']}")
        logger.info(f"세션 {session_id}: 배경 생성 시작, 모드: {request.mode}")
        logger.info(f"세션 {session_id}: 프롬프트: {request.prompt}")
        logger.info(f"세션 {session_id}: 제품 박스: {request.product_box}")

        canv, back_rm_canv, mask = image_main.step1_5()
        result = image_main.step2(
            mode=request.mode,
            canvas=canv,
            mask=mask
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