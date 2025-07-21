# backend/routers/advertisement_router.py
from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session
from typing import Annotated, List, Optional, Union

from ...database.connection import get_session
from ...database.models import (
    Advertisement as DBAdvertisement,
    AdvertisementImageGeneration as DBImageGeneration,
    AdvertisementImagePreservation as DBImagePreservation,
    AdvertisementCopy as DBAdvertisementCopy
) 
from ...crud import advertisement_crud as crud 
from ...schemas import advertisement_schema as schemas 

router = APIRouter(prefix="/advertisements", tags=["Advertisements"])

# ******************************************* Advertisement CRUD ******************************************

@router.post("/", response_model=schemas.AdvertisementRead, status_code=status.HTTP_201_CREATED)
def create_advertisement(
    ad_create: schemas.AdvertisementCreate,
    user_id: int,
    db: Annotated[Session, Depends(get_session)]
) -> Union[DBAdvertisement, HTTPException]:
    """새로운 광고를 생성합니다."""
    try:
        new_ad = crud.create_advertisement(
            db=db,
            user_id=user_id,
            title=ad_create.title,
            description=ad_create.description
        )
        return new_ad
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"광고 생성 실패: {e}")

@router.get("/", response_model=List[schemas.AdvertisementRead])
def read_advertisements(db: Annotated[Session, Depends(get_session)]) -> List[DBAdvertisement]:
    """모든 광고 목록을 조회합니다."""
    try:
        ads = crud.get_all_advertisements(db) 
        return ads
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"광고 조회 실패: {e}")

@router.get("/{ad_id}", response_model=schemas.AdvertisementRead)
def read_advertisement(ad_id: int, db: Annotated[Session, Depends(get_session)]) -> Union[DBAdvertisement, HTTPException]:
    """특정 광고를 ID로 조회합니다."""
    try:
        ad = crud.get_advertisement_by_id(db, ad_id)
        if not ad:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="광고를 찾을 수 없습니다.")
        return ad
    except HTTPException:
        raise 
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"광고 조회 실패: {e}")

@router.patch("/{ad_id}", response_model=schemas.AdvertisementRead)
def update_advertisement(
    ad_id: int,
    ad_update: schemas.AdvertisementUpdate,
    db: Annotated[Session, Depends(get_session)]
) -> Union[DBAdvertisement, HTTPException]:
    """특정 광고를 부분적으로 업데이트합니다."""
    try:
        db_ad = crud.get_advertisement_by_id(db, ad_id)
        if not db_ad:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="광고를 찾을 수 없습니다.")

        updated_ad = crud.update_advertisement(
            db,
            ad_entry=db_ad,
            new_title=ad_update.title,
            new_description=ad_update.description
        )
        return updated_ad
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"광고 업데이트 실패: {e}")

@router.delete("/{ad_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_advertisement(ad_id: int, db: Annotated[Session, Depends(get_session)]) -> Union[Response, HTTPException]:
    """특정 광고를 삭제합니다."""
    try:
        success = crud.delete_advertisement(db, ad_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="광고를 찾을 수 없습니다.")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"광고 삭제 실패: {e}")

# ******************************************* AdvertisementImageGeneration CRUD ******************************************

@router.post("/{ad_id}/image-generations", response_model=schemas.AdvertisementImageGenerationRead, status_code=status.HTTP_201_CREATED)
def create_ad_image_generation(
    ad_id: int,
    image_gen_create: schemas.AdvertisementImageGenerationCreate,
    db: Annotated[Session, Depends(get_session)]
) -> DBImageGeneration:
    """광고에 대한 이미지 생성 요청 기록을 생성합니다."""
    try:
        db_ad = crud.get_advertisement_by_id(db, ad_id)
        if not db_ad:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="광고를 찾을 수 없습니다.")

        new_image_gen = crud.create_image_generation_request(
            db,
            advertisement_id=ad_id,
            image_path=image_gen_create.image_path
        )
        return new_image_gen
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"광고 이미지 생성 요청 기록 생성 실패: {e}")

@router.get("/{ad_id}/image-generations", response_model=List[schemas.AdvertisementImageGenerationRead])
def read_ad_image_generations(ad_id: int, db: Annotated[Session, Depends(get_session)]) -> Union[List[DBImageGeneration], HTTPException]:
    """특정 광고에 연결된 모든 이미지 생성 요청 기록을 조회합니다."""
    try:
        db_ad = crud.get_advertisement_by_id(db, ad_id)
        if not db_ad:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="광고를 찾을 수 없습니다.")
        return db_ad.images
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"광고 {ad_id}에 대한 이미지 생성 요청 기록 조회 실패: {e}")

@router.get("/image-generations/{image_gen_id}", response_model=schemas.AdvertisementImageGenerationRead)
def read_single_ad_image_generation(image_gen_id: int, db: Annotated[Session, Depends(get_session)]) -> Union[DBImageGeneration, HTTPException]:
    """단일 이미지 생성 요청 기록을 아이디로 조회합니다."""
    try:
        image_gen = crud.get_image_generation_by_id(db, image_gen_id)
        if not image_gen:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="이미지 생성 요청을 찾을 수 없습니다.")
        return image_gen
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"이미지 생성 요청 {image_gen_id} 조회 실패: {e}")

@router.patch("/image-generations/{image_gen_id}", response_model=schemas.AdvertisementImageGenerationRead)
def update_ad_image_generation(
    image_gen_id: int,
    image_gen_update: schemas.AdvertisementImageGenerationUpdate,
    db: Annotated[Session, Depends(get_session)]
) -> Union[DBImageGeneration, HTTPException]:
    """특정 이미지 생성 요청 기록을 업데이트합니다."""
    try:
        db_image_gen = crud.get_image_generation_by_id(db, image_gen_id)
        if not db_image_gen:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="이미지 생성 요청을 찾을 수 없습니다.")

        updated_image_gen = crud.update_image_generation_request(
            db,
            image_gen_entry=db_image_gen,
            new_image_path=image_gen_update.image_path,
        )
        return updated_image_gen
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"이미지 생성 요청 업데이트 실패: {e}")

@router.delete("/image-generations/{image_gen_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ad_image_generation(image_gen_id: int, db: Annotated[Session, Depends(get_session)]) -> Union[Response, HTTPException]:
    """특정 이미지 생성 요청 기록을 삭제합니다."""
    try:
        success = crud.delete_image_generation_request(db, image_gen_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="광고 이미지 생성 삭제 요청을 찾을 수 없습니다.")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"이미지 생성 요청 삭제 실패: {e}")


# ******************************************* AdvertisementImagePreservation CRUD ******************************************

@router.post("/{ad_id}/image-preservations", response_model=schemas.AdvertisementImagePreservationRead, status_code=status.HTTP_201_CREATED)
def create_ad_image_preservation(
    ad_id: int,
    image_pres_create: schemas.AdvertisementImagePreservationCreate,
    db: Annotated[Session, Depends(get_session)]
) -> Union[DBImagePreservation, HTTPException]:
    """광고에 대한 이미지 보존 요청 기록을 생성합니다."""
    try:
        db_ad = crud.get_advertisement_by_id(db, ad_id)
        if not db_ad:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="광고를 찾을 수 없습니다.")

        new_image_pres = crud.create_image_preservation_request(
            db,
            advertisement_id=ad_id,
            preserved_image_path=image_pres_create.preserved_image_path
        )
        return new_image_pres
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"광고 이미지 보존 요청 생성 실패: {e}")

@router.get("/{ad_id}/image-preservations", response_model=List[schemas.AdvertisementImagePreservationRead])
def read_ad_image_preservations(ad_id: int, db: Annotated[Session, Depends(get_session)]) -> Union[List[DBImagePreservation], HTTPException]:
    """특정 광고에 연결된 모든 이미지 보존 요청 기록을 조회합니다."""
    try:
        db_ad = crud.get_advertisement_by_id(db, ad_id)
        if not db_ad:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="광고를 찾을 수 없습니다.")
        return db_ad.image_preservations
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"광고 {ad_id}에 대한 이미지 보존 요청 조회 실패: {e}")

@router.get("/image-preservations/{image_pres_id}", response_model=schemas.AdvertisementImagePreservationRead)
def read_single_ad_image_preservation(image_pres_id: int, db: Annotated[Session, Depends(get_session)]) -> Union[DBImagePreservation, HTTPException]:
    """단일 이미지 보존 요청 기록을 아이디로 조회합니다."""
    try:
        image_pres = crud.get_image_preservation_by_id(db, image_pres_id)
        if not image_pres:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="이미지 보존 요청을 찾을 수 없습니다.")
        return image_pres
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"이미지 보존 요청 {image_pres_id} 조회 실패: {e}")

@router.patch("/image-preservations/{image_pres_id}", response_model=schemas.AdvertisementImagePreservationRead)
def update_ad_image_preservation(
    image_pres_id: int,
    image_pres_update: schemas.AdvertisementImagePreservationUpdate,
    db: Annotated[Session, Depends(get_session)]
) -> Union[DBImagePreservation, HTTPException]:
    """특정 이미지 보존 요청 기록을 업데이트합니다."""
    try:
        db_image_pres = crud.get_image_preservation_by_id(db, image_pres_id)
        if not db_image_pres:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="이미지 보존 요청을 찾을 수 없습니다.")

        updated_image_pres = crud.update_image_preservation_request(
            db,
            image_pres_entry=db_image_pres,
            new_preserved_image_path=image_pres_update.preserved_image_path 
        )
        return updated_image_pres
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"광고 이미지 보존 요청 업데이트 실패: {e}")

@router.delete("/image-preservations/{image_pres_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ad_image_preservation(image_pres_id: int, db: Annotated[Session, Depends(get_session)]) -> Union[Response, HTTPException]:
    """특정 이미지 보존 요청 기록을 삭제합니다."""
    try:
        success = crud.delete_image_preservation_request(db, image_pres_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image preservation request not found")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to delete image preservation request: {e}")

# ******************************************* AdvertisementCopy CRUD ******************************************

@router.post("/{ad_id}/copies", response_model=schemas.AdvertisementCopyRead, status_code=status.HTTP_201_CREATED)
def create_ad_copy(
    ad_id: int,
    ad_copy_create: schemas.AdvertisementCopyCreate,
    db: Annotated[Session, Depends(get_session)]
) -> Union[DBAdvertisementCopy, HTTPException]:
    """광고에 대한 문구 기록을 생성합니다."""
    try:
        db_ad = crud.get_advertisement_by_id(db, ad_id)
        if not db_ad:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="광고를 찾을 수 없습니다.")
        
        new_ad_copy = crud.create_advertisement_copy(
            db,
            advertisement_id=ad_id,
            copy_text=ad_copy_create.copy_text,
            ad_type=ad_copy_create.ad_type,
            user_prompt_for_generation=ad_copy_create.user_prompt_for_generation
        )
        return new_ad_copy
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"광고 문구 생성 실패: {e}")

@router.get("/{ad_id}/copies", response_model=List[schemas.AdvertisementCopyRead])
def read_ad_copies(ad_id: int, db: Annotated[Session, Depends(get_session)]) -> Union[List[DBAdvertisementCopy], HTTPException]:
    """특정 광고에 연결된 모든 문구 기록을 조회합니다."""
    try:
        db_ad = crud.get_advertisement_by_id(db, ad_id)
        if not db_ad:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="광고를 찾을 수 없습니다.")
        return db_ad.copies
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"광고 문구 조회 실패: {e}")

@router.get("/copies/{copy_id}", response_model=schemas.AdvertisementCopyRead)
def read_single_ad_copy(copy_id: int, db: Annotated[Session, Depends(get_session)]) -> Union[DBAdvertisementCopy, HTTPException]:
    """단일 광고 문구 기록을 ID로 조회합니다."""
    try:
        ad_copy = crud.get_advertisement_copy_by_id(db, copy_id)
        if not ad_copy:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="광고 문구를 찾을 수 없습니다.")
        return ad_copy
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"광고 문구 조회 실패: {e}")

@router.patch("/copies/{copy_id}", response_model=schemas.AdvertisementCopyRead)
def update_ad_copy(
    copy_id: int,
    ad_copy_update: schemas.AdvertisementCopyUpdate,
    db: Annotated[Session, Depends(get_session)]
) -> Union[DBAdvertisementCopy, HTTPException]:
    """특정 광고 문구 기록을 업데이트합니다."""
    try:
        db_ad_copy = crud.get_advertisement_copy_by_id(db, copy_id)
        if not db_ad_copy:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="광고 문구를 찾을 수 없습니다.")

        updated_ad_copy = crud.update_advertisement_copy(
            db,
            ad_copy_entry=db_ad_copy,
            new_copy_text=ad_copy_update.copy_text,
            new_ad_type=ad_copy_update.ad_type, 
            new_user_prompt_for_generation=ad_copy_update.user_prompt_for_generation
        )
        return updated_ad_copy
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"광고 문구 업데이트 실패: {e}")

@router.delete("/copies/{copy_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ad_copy(copy_id: int, db: Annotated[Session, Depends(get_session)]) -> Union[Response, HTTPException]:
    """특정 광고 문구 기록을 삭제합니다."""
    try:
        success = crud.delete_advertisement_copy(db, copy_id)
        if not success:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="광고 문구를 찾을 수 없습니다.")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"광고 문구 삭제 실패: {e}")