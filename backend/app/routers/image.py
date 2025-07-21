# backend/app/routers/image.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Header, Depends, status
from fastapi.responses import StreamingResponse
import io, logging, os
from PIL import Image
from typing import Annotated, Union
from sqlmodel import Session

from app.services import image_main
from app.cache import get_session_cache, update_session_cache
from ...database.connection import get_session
from ...utils.sha_save_image import save_image_to_disk
from ...crud import advertisement_crud, session_crud
from ...schemas.advertisement_schema import AdvertisementCreate

logger = logging.getLogger(__name__)

router = APIRouter()

BACKEND_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STATIC_ROOT_DIR_IMAGE_ROUTER = os.path.join(BACKEND_ROOT_DIR, "static")
GENERATED_IMAGES_SUBDIR_NAME = "generated_images"

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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/generate-background", response_model=dict)
async def generate_background(
    db: Annotated[Session, Depends(get_session)],
    mode: str = Form(...),
    session_id: str = Header(..., alias="session-id"),
    title: str = Form(..., min_length=1, max_length=100),
    description: str = Form(..., min_length=1, max_length=500)
):
    try:
        cache = get_session_cache(session_id)
        if not cache or "canvas" not in cache or "back_rm_canv" not in cache or "mask" not in cache:
            logger.error(f"세션 {session_id}: 캐시에 필요한 이미지 없음")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="세션에 해당하는 이미지가 없습니다. /preprocess 먼저 호출해주세요.")

        image_main.generator.category = cache["category"]

        logger.info(f"세션 {session_id}: 배경 생성 시작, 모드: {mode}")
        
        result = image_main.step2(mode=mode, canvas=cache["canvas"], mask=cache["mask"])

        generated_image: Image.Image = None
        if isinstance(result, list) and result:
            generated_image = result[0]
        elif isinstance(result, Image.Image):
            generated_image = result
        else:
            logger.error(f"세션 {session_id}: 유효하지 않은 이미지 생성 결과")
            raise HTTPException(status_code=500, detail="이미지 생성 결과가 유효하지 않습니다.")

        update_session_cache(session_id, "generated_background", generated_image)
        logger.info(f"세션 {session_id}: 배경 이미지 생성 완료 및 캐시 저장")

        # 1. 생성한 광고 이미지 저장
        # 경로 설정 
        image_save_disk_directory = os.path.join(STATIC_ROOT_DIR_IMAGE_ROUTER, GENERATED_IMAGES_SUBDIR_NAME)
        os.makedirs(image_save_disk_directory, exist_ok=True)

        full_disk_path = save_image_to_disk(generated_image, image_save_disk_directory)
        logger.info(f"세션 {session_id}: 배경 이미지 디스크에 저장 완료: {full_disk_path}")

        # generated_images/image.png 
        relative_path_from_static_root = os.path.relpath(full_disk_path, STATIC_ROOT_DIR_IMAGE_ROUTER)
        # /static/generated_images/image.png
        image_url_path = f"/static/{relative_path_from_static_root.replace(os.sep, '/')}"
        logger.info(f"세션 {session_id}: 배경 이미지 URL 경로: {image_url_path}")

        # 2. user_id 가지고 오기
        user_id = None
        db_session_entry = session_crud.get_session_by_id(db, session_id)
        if db_session_entry:
            user_id = db_session_entry.user_id
            logger.info(f"세션 {session_id}: 사용자 아이디 {user_id} 확인")
        else:
            logger.warning(f"세션 {session_id}: 데이터베이스에 세션 정보가 없습니다")
        
        if user_id is None:
            logger.error(f"세션 {session_id}: 사용자 아이디가 없습니다. 광고를 생성할 수 없습니다.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="사용자 아이디가 없습니다. 광고를 생성할 수 없습니다.")


        # 3. 광고 객체 생성
        advertisement = advertisement_crud.create_advertisement(
            db=db,
            user_id=user_id,
            title=title,
            description=description
        )

        logger.info(f"세션 {session_id}: 광고 객체 생성 완료: {advertisement}")

        # 4. 광고 이미지 
        created_image_preservation = advertisement_crud.create_image_preservation_request(
            db,
            advertisement_id=advertisement.id,
            image_url=image_url_path,
        )
        logger.info(f"세션 {session_id}: 광고 이미지 보존 요청 완료: {created_image_preservation.id}")

        # 5. 세션 캐시에 광고 아이디 저장
        update_session_cache(session_id, "advertisement_id", advertisement.id)

        return {"message": "배경 이미지 생성 완료 및 광고 저장 완료", "advertisement_id": advertisement.id, "image_url": image_url_path}

    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"세션 {session_id}: 배경 생성 실패 및 광고 저장 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"배경 생성 실패 및 광고 저장 실패: {str(e)}")

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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))