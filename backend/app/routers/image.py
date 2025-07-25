# backend/app/routers/image.py
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Header, Depends, status, Body
from fastapi.responses import StreamingResponse
import io, logging, os
from PIL import Image
from typing import Annotated, Union, Literal
from sqlmodel import Session
from pydantic import BaseModel

from app.services import image_main
from database.connection import get_session
from utils.sha_save_image import save_image_to_disk
from crud import advertisement_crud, session_crud

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/image", tags=["Image Processing"])

BACKEND_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
STATIC_ROOT_DIR_IMAGE_ROUTER = os.path.join(BACKEND_ROOT_DIR, "static")
GENERATED_IMAGES_SUBDIR_NAME = "generated_images"
TEMP_SESSION_IMAGES_SUBDIR_NAME = "temp_session_images"

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

@router.post("/preprocess")
async def preprocess_image(
    db: Annotated[Session, Depends(get_session)],
    file: UploadFile = File(...),
    session_id: str = Header(..., alias="session-id"),
    category: str = Header(...)
):
    """새로운 세션을 초기화하거나 기존 세션을 업데이트합니다."""
    try:
        image_bytes = await file.read()
        image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        logger.info(f"세션 {session_id}: 이미지 전처리 시작")
        image_main.generator.cfg['paths']['product_image'] = image

        back_rm = image_main.step1() 

        db_session_entry = session_crud.get_session_by_id(db, session_id)
        if not db_session_entry:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="세션을 찾을 수 없습니다.")

        session_data = db_session_entry.session_data if db_session_entry.session_data is not None else {} 

        # static/temp_session_images/{session_id} 디렉토리 생성
        session_temp_dir = os.path.join(STATIC_ROOT_DIR_IMAGE_ROUTER, TEMP_SESSION_IMAGES_SUBDIR_NAME, session_id)
        os.makedirs(session_temp_dir, exist_ok=True)

        # back_rm 저장
        back_rm_full_path = save_image_to_disk(back_rm, session_temp_dir, prefix="back_rm_")
        session_data["back_rm_url"] = f"/static/{os.path.relpath(back_rm_full_path, STATIC_ROOT_DIR_IMAGE_ROUTER).replace(os.sep, '/')}"

        session_data["category"] = category

        session_crud.update_session_data(db, db_session_entry, session_data)
        updated_session = session_crud.get_session_by_id(db, session_id) # 검증
        logger.info(f"세션 {session_id}: 세션 데이터 업데이트 완료: {updated_session.session_data}")

        # 전처리된 이미지를 캔버스에 적용
        buffer = io.BytesIO()
        back_rm.save(buffer, format="PNG")
        buffer.seek(0)
        logger.info(f"세션 {session_id}: 이미지 전처리 완료 및 세션 데이터 업데이트")
        return StreamingResponse(buffer, media_type="image/png")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"세션 {session_id}: 이미지 전처리 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/generate-background", response_model=dict)
async def generate_background(
    db: Annotated[Session, Depends(get_session)],
    request: BackgroundRequest = Body(...), 
    session_id: str = Header(..., alias="session-id"),
):
    try:
        print("RUNNING GENERATE BACKGROUND!!!")
        db_session_entry = session_crud.get_session_by_id(db, session_id)
        if not db_session_entry or not db_session_entry.session_data:
            logger.error(f"세션 {session_id}: 데이터베이스에 세션 데이터 없음")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="세션 데이터를 찾을 수 없습니다. /preprocess 먼저 호출해주세요.")

        session_data = db_session_entry.session_data
        logger.info(f"세션 {session_id}: Generate-Background 함수 - 세션 데이터: {session_data}")

        # 저장된 URL에서 이미지 불러오기
        back_rm_url = session_data.get("back_rm_url") 

        logger.info(f"세션 {session_id}: Generate-Background 함수 - 추출한 URL: back_rm={back_rm_url}")

        if not back_rm_url:
            logger.error(f"세션 {session_id}: 데이터베이스 세션에 필요한 이미지 또는 마스크 이미지 URL 없음")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="세션에 해당하는 이미지가 없습니다. /preprocess 먼저 호출해주세요.")

        # 이미지 URL에서 파일 경로 추출
        back_rm_path = os.path.join(STATIC_ROOT_DIR_IMAGE_ROUTER, back_rm_url.replace("/static/", "").replace('/', os.sep))
        if not os.path.exists(back_rm_path):
            logger.error(f"세션 {session_id}: 저장된 back_rm 파일이 없습니다: {back_rm_path}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="백그라운드가 제거된 이미지가 파일 시스템에서 발견되지 않습니다.")

        image_main.generator.back_rm = Image.open(back_rm_path).convert("RGBA")
        logger.info(f"세션 {session_id}: back_rm 이미지를 로드하여 generator에 설정 완료.")

        image_main.generator.category = session_data.get("category") 
        image_main.generator.marketing_type = request.prompt
        size_info = (int(request.product_box.width), int(request.product_box.height))
        position = (int(request.product_box.x), int(request.product_box.y))
        
        image_main.generator.cfg['image_config']['resize_info'] = size_info
        image_main.generator.cfg['image_config']['position'] = position
        image_main.generator.cfg['canvas_type'] = request.product_box.canvas_type
        
        logger.info(f"***************캔버스 종류: {image_main.generator.cfg['canvas_type']}")
        logger.info(f"세션 {session_id}: 배경 생성 시작, 모드: {request.mode}")
        logger.info(f"세션 {session_id}: 프롬프트: {request.prompt}")
        logger.info(f"세션 {session_id}: 제품 박스: {request.product_box}")

        canv, _, mask = image_main.step1_5() 
        result = image_main.step2(
            mode=request.mode,
            canvas=canv,
            mask=mask
        )

        generated_image: Image.Image = result[0] if isinstance(result, list) else result

        session_temp_dir = os.path.join(STATIC_ROOT_DIR_IMAGE_ROUTER, TEMP_SESSION_IMAGES_SUBDIR_NAME, session_id)
        os.makedirs(session_temp_dir, exist_ok=True)
        generated_background_temp_path = save_image_to_disk(generated_image, session_temp_dir, prefix="generated_bg_")
        session_data["generated_background_url"] = f"/static/{os.path.relpath(generated_background_temp_path, STATIC_ROOT_DIR_IMAGE_ROUTER).replace(os.sep, '/')}"
        
        logger.info(f"세션 {session_id}: 배경 이미지 생성 완료 및 임시 세션 데이터 업데이트")

        # 1. 생성한 광고 이미지 저장 
        image_save_disk_directory = os.path.join(STATIC_ROOT_DIR_IMAGE_ROUTER, GENERATED_IMAGES_SUBDIR_NAME)
        os.makedirs(image_save_disk_directory, exist_ok=True)
        full_disk_path = save_image_to_disk(generated_image, image_save_disk_directory)
        logger.info(f"세션 {session_id}: 배경 이미지 디스크에 저장 완료: {full_disk_path}")
        relative_path_from_static_root = os.path.relpath(full_disk_path, STATIC_ROOT_DIR_IMAGE_ROUTER)
        image_url_path = f"/static/{relative_path_from_static_root.replace(os.sep, '/')}"
        logger.info(f"세션 {session_id}: 배경 이미지 URL 경로: {image_url_path}")

        # 2. user_id 가지고 오기
        user_id = None
        db_session_entry = session_crud.get_session_by_id(db, session_id)
        if db_session_entry:
            user_id = db_session_entry.user_id
            logger.info(f"세션 {session_id}: 사용자 아이디 {user_id} 확인")
        else:
            logger.warning(f"세션 {session_id}: 데이터베이스에 세션 정보가 없습니다. 광고를 저장할 수 없습니다.")
        
        if user_id is None:
            logger.error(f"세션 {session_id}: 사용자 아이디가 없습니다. 광고를 생성할 수 없습니다.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="사용자 아이디가 없습니다. 광고를 생성할 수 없습니다.")

        # 3. 광고 객체 생성
        advertisement = advertisement_crud.create_advertisement(
            db=db,
            user_id=user_id,
            description=request.prompt,
        )
        logger.info(f"세션 {session_id}: 광고 객체 생성 완료: {advertisement}")

        # 4. 광고 이미지 보존 요청
        created_image_preservation = advertisement_crud.create_image_preservation_request(
            db,
            advertisement_id=advertisement.id,
            preserved_image_path=image_url_path,
        )
        logger.info(f"세션 {session_id}: 광고 이미지 보존 요청 완료: {created_image_preservation.id}")

        # 5. 세션 데이터 업데이트
        session_data["advertisement_id"] = advertisement.id
        session_crud.update_session_data(db, db_session_entry, session_data)

        return {"message": "배경 이미지 생성 완료 및 광고 저장 완료", "advertisement_id": advertisement.id, "image_url": image_url_path}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"세션 {session_id}: 배경 생성 실패 및 광고 저장 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"배경 생성 실패 및 광고 저장 실패: {str(e)}")

@router.get("/generated-background")
async def get_generated_background(db: Annotated[Session, Depends(get_session)], session_id: str = Header(..., alias="session-id")):
    """세션 아이디로 생성된 배경 이미지 데이터를 조회합니다."""
    try:
        db_session_entry = session_crud.get_session_by_id(db, session_id)
        if not db_session_entry or not db_session_entry.session_data:
            logger.error(f"세션 {session_id}: 데이터베이스에 세션 데이터 없음")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="세션 데이터를 찾을 수 없습니다.")
        
        session_data = db_session_entry.session_data
        generated_background_url = session_data.get("generated_background_url")

        if not generated_background_url:
            logger.error(f"세션 {session_id}: 배경 이미지 URL 없음")
            raise HTTPException(status_code=404, detail="배경 이미지가 없습니다.")

        image_path = os.path.join(STATIC_ROOT_DIR_IMAGE_ROUTER, generated_background_url.replace("/static/", "").replace('/', os.sep))
        if not os.path.exists(image_path):
            logger.error(f"세션 {session_id}: 저장된 배경 이미지 파일이 없습니다: {image_path}")
            raise HTTPException(status_code=404, detail="배경 이미지가 파일 시스템에서 발견되지 않습니다.")

        image = Image.open(image_path) # PIL.Image 객체
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        logger.info(f"세션 {session_id}: 배경 이미지 반환")
        return StreamingResponse(img_bytes, media_type="image/png")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"세션 {session_id}: 배경 이미지 조회 실패: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))