# backend/schemas/session_schema.py
from __future__ import annotations

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

from .user_schema import UserPublic

class SessionCreate(BaseModel):
    user_id: Optional[int] = Field(None, description="사용자 아이디 (선택 사항). 로그인한 경우 세션과 연결된 사용자 아이디.")
    session_data: Optional[Dict[str, Any]] = Field(None, description="세션 데이터 (선택 사항). JSON 형식으로 저장될 수 있음.")

class SessionUpdate(BaseModel):
    session_data: Optional[Dict[str, Any]] = Field(None, description="세션 데이터 (선택 사항). JSON 형식으로 저장될 수 있음.")
    expires_at: Optional[datetime] = Field(None, description="세션의 만료 시간 (UTC). 선택 사항으로, 지정하지 않으면 기본값은 24시간 후.")

    class Config:
        from_attributes = True

class SessionRead(BaseModel):
    id: str = Field(..., description="세션의 고유 아이디 (UUID 문자열).")
    created_at: datetime = Field(..., description="세션이 생성된 시간 (UTC).")
    expires_at: datetime = Field(..., description="세션의 만료 시간 (UTC).")
    session_data: Dict[str, Any] = Field(..., description="세션 데이터 (선택 사항). JSON 형식으로 저장될 수 있음.")

    user: Optional[UserPublic] = Field(None, description="세션과 연결된 사용자 정보 (선택 사항).")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "session_12345",
                "created_at": "2023-01-01T00:00:00Z",
                "expires_at": "2023-01-02T00:00:00Z",
                "session_data": {"key": "value"},
                "user": {
                    "id": 1,
                    "username": "john_doe",
                    "email": "john_doe@example.com"
                }
            }
        }