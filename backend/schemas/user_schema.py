# backend/schemas/user_schema.py
from __future__ import annotations 

from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field 

class UserPublic(BaseModel):
    id: int = Field(..., description="사용자의 고유 아이디.")
    username: str = Field(..., min_length=3, max_length=20, description="사용자의 이름. 3자 이상 20자 이하.")
    email: EmailStr = Field(..., description="사용자의 이메일 주소. 유효한 이메일 형식이어야 함.")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "john_doe@example.com"
            }
        }

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=20, description="사용자의 이름. 3자 이상 20자 이하.")
    email: EmailStr = Field(..., description="사용자의 이메일 주소. 유효한 이메일 형식이어야 함.")

class UserCreate(UserBase):
    password: str = Field(..., min_length=4, max_length=20, description="사용자의 비밀번호. 4자 이상 20자 이하.")

class UserLogin(BaseModel):
    email: EmailStr = Field(..., description="로그인할 사용자의 이메일 주소.")
    password: str = Field(..., min_length=4, max_length=20, description="로그인할 사용자의 비밀번호.")

class UserUpdate(UserBase):
    username: Optional[str] = Field(None, min_length=3, max_length=20, description="사용자의 이름. 3자 이상 20자 이하.")
    email: Optional[EmailStr] = Field(None, description="사용자의 이메일 주소. 유효한 이메일 형식이어야 함.")
    password: Optional[str] = Field(None, min_length=4, max_length=20, description="사용자의 비밀번호. 4자 이상 20자 이하.")

class UserRead(UserBase):
    id: int = Field(..., description="사용자의 고유 아이디.")
    advertisements: List["AdvertisementRead"] = Field([], description="사용자가 게시한 광고 리스트.")
    sessions: List["SessionRead"] = Field([], description="사용자의 세션 리스트.")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "john_doe",
                "email": "john_doe@example.com",
                "advertisements": [
                    {
                        "id": 1,
                        "title": "Ad Title 1",
                        "description": "Ad Description 1",
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
                                "copy_text": "Ad Copy Text",
                                "created_at": "2023-01-01T00:00:00Z"
                            }
                        ]
                    }
                ],
                "sessions": [
                    {
                        "id": "session_1",
                        "created_at": "2023-01-01T00:00:00Z",
                        "expires_at": "2023-01-02T00:00:00Z",
                        "session_data": {}
                    }
                ]
            }
        }

class Token(BaseModel):
    access_token: str = Field(..., description="JWT 액세스 토큰.")
    token_type: str = Field(..., description="토큰 종류. 일반적으로 'bearer'로 설정됨.")
    user: "UserRead" = Field(..., description="로그인한 사용자 정보.")
