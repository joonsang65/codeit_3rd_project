# backend/schemas/advertisement_schema.py

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, timezone

from __future__ import annotations

# ******************************************* 광고 이미지 생성 요청 스키마 ******************************************
class AdvertisementImageGenerationBase(BaseModel):
    image_path: str = Field(..., description="생성된 이미지의 경로.")

class AdvertisementImageGenerationCreate(AdvertisementImageGenerationBase):
    # AdvertisementImageGenerationBase 클래스를 상속받습니다.
    pass

class AdvertisementImageGenerationUpdate(AdvertisementImageGenerationBase):
    """이미지 생성 요청 수정 시 사용되는 스키마."""
    image_path: Optional[str] = Field(None, description="생성된 이미지의 경로.")

    class Config:
        from_attributes = True

class AdvertisementImageGenerationRead(AdvertisementImageGenerationBase):
    id: int = Field(..., description="이미지 생성 요청의 고유 아이디.")
    advertisement_id: int = Field(..., description="광고의 고유 아이디.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="이미지 생성 요청이 생성된 시간 (UTC).")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "advertisement_id": 1,
                "image_path": "/path/to/generated/image.png",
                "created_at": "2023-01-01T00:00:00Z"
            }
        }

# ******************************************* 광고 이미지 보전 요청 스키마 ******************************************
class AdvertisementImagePreservationBase(BaseModel):
    preserved_image_path: str = Field(..., description="보존된 이미지의 경로.")

class AdvertisementImagePreservationCreate(AdvertisementImagePreservationBase):
    # AdvertisementImagePreservationBase 클래스를 상속받습니다.
    pass

class AdvertisementImagePreservationUpdate(AdvertisementImagePreservationBase):
    """이미지 보전 요청 수정 시 사용되는 스키마."""
    preserved_image_path: Optional[str] = Field(None, description="보존된 이미지의 경로.")

    class Config:
        from_attributes = True

class AdvertisementImagePreservationRead(AdvertisementImagePreservationBase):
    id: int = Field(..., description="이미지 보전 요청의 고유 아이디.")
    advertisement_id: int = Field(..., description="광고의 고유 아이디.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="이미지 보전 요청이 생성된 시간 (UTC).")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "advertisement_id": 1,
                "preserved_image_path": "/path/to/preserved/image.png",
                "created_at": "2023-01-01T00:00:00Z"
            }
        }

# ******************************************* 광고 문구 스키마 ******************************************
class AdvertisementCopyBase(BaseModel):
    copy_text: str = Field(..., min_length=1, max_length=500,description="광고 문구의 내용. 1자 이상 500자 이하.")
    ad_type: str = Field(..., description="광고 유형 (예: instagram, blog, poster).")
    user_prompt_for_generation: Optional[str] = Field(None, description="사용자가 입력한 설명. 광고 문구 생성 시 사용된 사용자 입력.")

class AdvertisementCopyCreate(AdvertisementCopyBase):
    # AdvertisementCopyBase 클래스를 상속받습니다.
    pass

class AdvertisementCopyUpdate(AdvertisementCopyBase):
    """광고 문구 수정 시 사용되는 스키마."""
    copy_text: Optional[str] = Field(None, min_length=1, max_length=500, description="광고 문구의 내용. 1자 이상 500자 이하.")
    ad_type: Optional[str] = Field(None, description="광고 유형 (예: instagram, blog, poster).")
    user_prompt_for_generation: Optional[str] = Field(None, description="사용자가 입력한 설명. 광고 문구 생성 시 사용된 사용자 입력.")

    class Config:
        from_attributes = True

class AdvertisementCopyRead(AdvertisementCopyBase):
    id: int = Field(..., description="광고 문구의 고유 아이디.")
    advertisement_id: int = Field(..., description="광고의 고유 아이디.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="광고 문구가 생성된 시간 (UTC).")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "advertisement_id": 1,
                "copy_text": "이것은 광고 문구입니다.",
                "ad_type": "instagram",
                "user_prompt_for_generation": "사용자가 입력한 설명",
                "created_at": "2023-01-01T00:00:00Z"
            }
        }

# ******************************************* 광고 스키마 ******************************************
class AdvertisementBase(BaseModel):
    """광고의 기본 정보 스키마."""
    title: str = Field(..., min_length=1, max_length=100, description="광고의 제목. 1자 이상 100자 이하.")
    description: str = Field(..., min_length=1, max_length=500, description="광고의 설명. 1자 이상 500자 이하.")

class AdvertisementCreate(AdvertisementBase):
    """광고 생성 시 사용되는 스키마."""
    pass

class AdvertisementUpdate(AdvertisementBase):
    """광고 수정 시 사용되는 스키마."""
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="광고의 제목. 1자 이상 100자 이하.")
    description: Optional[str] = Field(None, min_length=1, max_length=500, description="광고의 설명. 1자 이상 500자 이하.")
    
    class Config:
        from_attributes = True

class AdvertisementRead(AdvertisementBase):
    """광고 조회 시 반환되는 스키마."""
    id: int = Field(..., description="광고의 고유 아이디.")
    user_id: Optional[int] = Field(None, description="광고를 작성한 사용자의 아이디.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="광고가 생성된 시간 (UTC).")

    images: List[AdvertisementImageGenerationRead] = Field([], description="광고에 연결된 이미지 생성 요청 리스트.")
    image_preservations: List[AdvertisementImagePreservationRead] = Field([], description="광고에 연결된 이미지 보전 요청 리스트.")
    copies: List[AdvertisementCopyRead] = Field([], description="광고에 연결된 광고 문구 리스트.")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "title": "광고 제목",
                "description": "광고 설명",
                "user_id": 1,
                "created_at": "2023-01-01T00:00:00Z",
                "images": [
                    {
                        "id": 1,
                        "advertisement_id": 1,
                        "generated_image_path": "/path/to/generated/image.png",
                        "created_at": "2023-01-01T00:00:00Z"
                    }
                ],
                "image_preservations": [
                    {
                        "id": 1,
                        "advertisement_id": 1,
                        "preserved_image_path": "/path/to/preserved/image.png",
                        "created_at": "2023-01-01T00:00:00Z"
                    }
                ],
                "copies": [
                    {
                        "id": 1,
                        "advertisement_id": 1,
                        "copy_text": "이것은 광고 문구입니다.",
                        "ad_type": "instagram",
                        "user_prompt_for_generation": "사용자가 입력한 설명",
                        "created_at": "2023-01-01T00:00:00Z"
                    }
                ]
            }
        }