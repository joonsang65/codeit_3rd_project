# backend/crud/advertisement_crud.py

from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import Session, select 
from ..database.models import (
    Advertisement as DBAdvertisement,
    AdvertisementImageGeneration as DBImageGeneration,
    AdvertisementImagePreservation as DBImagePreservation,
    AdvertisementCopy as DBAdvertisementCopy
)

# ****************************************** 광고 CRUD ******************************************
def get_advertisement_by_id(db: Session, ad_id: int) -> Optional[DBAdvertisement]:
    """
    광고 ID로 데이터베이스에서 광고를 검색합니다.

    Args:
        db: 데이터베이스 세션.
        ad_id: 검색할 광고의 아이디.

    Returns:
        광고가 발견되면 Advertisement 객체를 반환하고, 그렇지 않으면 None을 반환합니다.
    """
    return db.get(DBAdvertisement, ad_id)

def get_advertisements_by_user_id(db: Session, user_id: int) -> List[DBAdvertisement]:
    """
    사용자 ID로 데이터베이스에서 광고들을 검색합니다.

    Args:
        db: 데이터베이스 세션.
        user_id: 검색할 사용자의 아이디.

    Returns:
        해당 사용자의 광고 리스트를 반환합니다.
    """
    return db.exec(select(DBAdvertisement).where(DBAdvertisement.user_id == user_id)).all()

def get_all_advertisements(db: Session) -> List[DBAdvertisement]:
    """
    데이터베이스에서 모든 광고를 검색합니다.

    Args:
        db: 데이터베이스 세션.

    Returns:
        모든 광고 리스트를 반환합니다.
    """
    return db.exec(select(DBAdvertisement)).all()

def create_advertisement(db: Session, user_id: int, title: str, description: str, user: Optional[DBAdvertisement] = None) -> DBAdvertisement:
    """
    광고를 데이터베이스에 생성합니다.

    Args:
        db: 데이터베이스 세션.
        user_id: 광고를 생성한 사용자의 아이디.
        title: 광고의 제목.
        description: 광고의 설명.
        user: 선택 사항. 광고를 생성한 사용자 객체.

    Returns:
        새로 생성된 Advertisement 객체.
    """
    new_ad = DBAdvertisement(user_id=user_id, title=title, description=description, user=user)
    db.add(new_ad)
    db.commit()
    db.refresh(new_ad)
    return new_ad

def update_advertisement(db: Session, ad_entry: DBAdvertisement, new_title: Optional[str] = None, new_description: Optional[str] = None) -> DBAdvertisement:
    """
    광고 정보를 업데이트합니다.

    Args:
        db: 데이터베이스 세션.
        ad_entry: 업데이트할 광고 객체.
        new_title: 새 제목 (선택 사항).
        new_description: 새 설명 (선택 사항).

    Returns:
        업데이트된 Advertisement 객체.
    """
    if new_title:
        ad_entry.title = new_title
    if new_description:
        ad_entry.description = new_description

    db.add(ad_entry)
    db.commit()
    db.refresh(ad_entry)
    return ad_entry

def delete_advertisement(db: Session, ad_id: int) -> bool:
    """
    광고를 데이터베이스에서 삭제합니다.

    Args:
        db: 데이터베이스 세션.
        ad_id: 삭제할 광고의 아이디.

    Returns:
        광고가 성공적으로 삭제되면 True, 그렇지 않으면 False를 반환합니다.
    """
    ad_to_delete = db.get(DBAdvertisement, ad_id)
    if ad_to_delete:
        db.delete(ad_to_delete)
        db.commit()
        return True
    return False

# ****************************************** 광고 이미지 생성 CRUD ******************************************
def get_image_generation_by_id(db: Session, image_gen_id: int) -> Optional[DBImageGeneration]:
    """
    광고 이미지 생성 요청 ID로 데이터베이스에서 요청을 검색합니다.

    Args:
        db: 데이터베이스 세션.
        image_gen_id: 검색할 이미지 생성 요청의 아이디.

    Returns:
        이미지 생성 요청이 발견되면 AdvertisementImageGeneration 객체를 반환하고, 그렇지 않으면 None을 반환합니다.
    """
    return db.get(DBImageGeneration, image_gen_id)

def get_all_image_generations(db: Session) -> List[DBImageGeneration]:
    """
    데이터베이스에서 모든 광고 이미지 생성 요청을 검색합니다.

    Args:
        db: 데이터베이스 세션.

    Returns:
        모든 광고 이미지 생성 요청 리스트를 반환합니다.
    """
    return db.exec(select(DBImageGeneration)).all()

def create_image_generation_request(db: Session, advertisement_id: int, image_path: str) -> DBImageGeneration:
    """
    광고 이미지 생성 요청을 데이터베이스에 생성합니다.

    Args:
        db: 데이터베이스 세션.
        advertisement_id: 광고의 아이디.
        image_path: 생성된 이미지의 경로.

    Returns:
        새로 생성된 AdvertisementImageGeneration 객체.
    """
    new_image_gen = DBImageGeneration(advertisement_id=advertisement_id, image_path=image_path, created_at=datetime.now(timezone.utc))
    db.add(new_image_gen)
    db.commit()
    db.refresh(new_image_gen)
    return new_image_gen

def update_image_generation_request(db: Session, image_gen_entry: DBImageGeneration, new_image_path: str) -> DBImageGeneration:
    """
    광고 이미지 생성 요청을 업데이트합니다.

    Args:
        db: 데이터베이스 세션.
        image_gen_entry: 업데이트할 이미지 생성 요청 객체.
        new_image_path: 새 이미지 경로.

    Returns:
        업데이트된 AdvertisementImageGeneration 객체.
    """
    image_gen_entry.image_path = new_image_path
    db.add(image_gen_entry)
    db.commit()
    db.refresh(image_gen_entry)
    return image_gen_entry

def delete_image_generation_request(db: Session, image_gen_id: int) -> bool:
    """
    광고 이미지 생성 요청을 데이터베이스에서 삭제합니다.

    Args:
        db: 데이터베이스 세션.
        image_gen_id: 삭제할 이미지 생성 요청의 아이디.

    Returns:
        이미지 생성 요청이 성공적으로 삭제되면 True, 그렇지 않으면 False를 반환합니다.
    """
    image_gen_entry = db.get(DBImageGeneration, image_gen_id)
    if image_gen_entry:
        db.delete(image_gen_entry)
        db.commit()
        return True
    return False

# ****************************************** 광고 이미지 보전 CRUD ******************************************
def get_image_preservation_by_id(db: Session, image_preservation_id: int) -> Optional[DBImagePreservation]:
    """
    광고 이미지 보전 요청 ID로 데이터베이스에서 요청을 검색합니다.

    Args:
        db: 데이터베이스 세션.
        image_preservation_id: 검색할 이미지 보전 요청의 아이디.

    Returns:
        이미지 보전 요청이 발견되면 AdvertisementImagePreservation 객체를 반환하고, 그렇지 않으면 None을 반환합니다.
    """
    return db.get(DBImagePreservation, image_preservation_id)

def get_all_image_preservations(db: Session) -> List[DBImagePreservation]:
    """
    데이터베이스에서 모든 광고 이미지 보전 요청을 검색합니다.

    Args:
        db: 데이터베이스 세션.

    Returns:
        모든 광고 이미지 보전 요청 리스트를 반환합니다.
    """
    return db.exec(select(DBImagePreservation)).all()

def create_image_preservation_request(db: Session, advertisement_id: int, preserved_image_path: str) -> DBImagePreservation:
    """
    광고 이미지 보전 요청을 데이터베이스에 생성합니다.

    Args:
        db: 데이터베이스 세션.
        advertisement_id: 광고의 아이디.
        preserved_image_path: 보존된 이미지의 경로.

    Returns:
        새로 생성된 AdvertisementImagePreservation 객체.
    """
    new_image_preservation = DBImagePreservation(
        advertisement_id=advertisement_id,
        preserved_image_path=preserved_image_path,
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_image_preservation)
    db.commit()
    db.refresh(new_image_preservation)
    return new_image_preservation

def update_image_preservation_request(db: Session, image_preservation_entry: DBImagePreservation, new_preserved_image_path: str) -> DBImagePreservation:
    """
    광고 이미지 보전 요청을 업데이트합니다.

    Args:
        db: 데이터베이스 세션.
        image_preservation_entry: 업데이트할 이미지 보전 요청 객체.
        new_preserved_image_path: 새 보존 이미지 경로.

    Returns:
        업데이트된 AdvertisementImagePreservation 객체.
    """
    image_preservation_entry.preserved_image_path = new_preserved_image_path
    db.add(image_preservation_entry)
    db.commit()
    db.refresh(image_preservation_entry)
    return image_preservation_entry

def delete_image_preservation_request(db: Session, image_preservation_id: int) -> bool:
    """
    광고 이미지 보전 요청을 데이터베이스에서 삭제합니다.

    Args:
        db: 데이터베이스 세션.
        image_preservation_id: 삭제할 이미지 보전 요청의 아이디.

    Returns:
        이미지 보전 요청이 성공적으로 삭제되면 True, 그렇지 않으면 False를 반환합니다.
    """
    image_preservation_entry = db.get(DBImagePreservation, image_preservation_id)
    if image_preservation_entry:
        db.delete(image_preservation_entry)
        db.commit()
        return True
    return False

# ****************************************** 광고 문구 CRUD ******************************************
def get_advertisement_copy_by_id(db: Session, ad_copy_id: int) -> Optional[DBAdvertisementCopy]:
    """
    광고 문구 아이디로 데이터베이스에서 광고 문구를 검색합니다.

    Args:
        db: 데이터베이스 세션.
        ad_copy_id: 검색할 광고 문구의 아이디.

    Returns:
        광고 문구가 발견되면 AdvertisementCopy 객체를 반환하고, 그렇지 않으면 None을 반환합니다.
    """
    return db.get(DBAdvertisementCopy, ad_copy_id)

def get_all_advertisement_copies(db: Session) -> List[DBAdvertisementCopy]:
    """
    데이터베이스에서 모든 광고 문구를 검색합니다.

    Args:
        db: 데이터베이스 세션.

    Returns:
        모든 광고 문구 리스트를 반환합니다.
    """
    return db.exec(select(DBAdvertisementCopy)).all()

def create_advertisement_copy(db: Session, advertisement_id: int, copy_text: str, ad_type: str, user_prompt_for_generation: str) -> DBAdvertisementCopy:
    """
    광고 문구를 데이터베이스에 생성합니다.

    Args:
        db: 데이터베이스 세션.
        advertisement_id: 광고의 아이디.
        copy_text: 광고 문구의 텍스트.
        user_prompt_for_generation: 광고 문구 생성을 위한 사용자 프롬프트.

    Returns:
        새로 생성된 AdvertisementCopy 객체.
    """
    new_ad_copy = DBAdvertisementCopy(
        advertisement_id=advertisement_id, 
        copy_text=copy_text,
        ad_type=ad_type,
        user_prompt_for_generation=user_prompt_for_generation, 
        created_at=datetime.now(timezone.utc)
    )
    db.add(new_ad_copy)
    db.commit()
    db.refresh(new_ad_copy)
    return new_ad_copy

def update_advertisement_copy(db: Session, ad_copy_entry: DBAdvertisementCopy, new_copy_text: str, new_ad_type: str, new_user_prompt_for_generation: str) -> DBAdvertisementCopy:
    """
    광고 문구를 업데이트합니다.

    Args:
        db: 데이터베이스 세션.
        ad_copy_entry: 업데이트할 광고 문구 객체.
        new_copy_text: 새 광고 문구 텍스트.
        new_ad_type: 새 광고 유형.
        new_user_prompt_for_generation: 새 사용자 프롬프트.

    Returns:
        업데이트된 AdvertisementCopy 객체.
    """
    ad_copy_entry.copy_text = new_copy_text
    ad_copy_entry.ad_type = new_ad_type
    ad_copy_entry.user_prompt_for_generation = new_user_prompt_for_generation
    db.add(ad_copy_entry)
    db.commit()
    db.refresh(ad_copy_entry)
    return ad_copy_entry

def delete_advertisement_copy(db: Session, ad_copy_id: int) -> bool:
    """
    광고 문구를 데이터베이스에서 삭제합니다.

    Args:
        db: 데이터베이스 세션.
        ad_copy_id: 삭제할 광고 문구의 아이디.

    Returns:
        광고 문구가 성공적으로 삭제되면 True, 그렇지 않으면 False를 반환합니다.
    """
    ad_copy_entry = db.get(DBAdvertisementCopy, ad_copy_id)
    if ad_copy_entry:
        db.delete(ad_copy_entry)
        db.commit()
        return True
    return False