# backend/database/models.py

from datetime import datetime, timezone, timedelta
from typing import Optional, List
from sqlmodel import Field, Relationship, SQLModel

class Session(SQLModel, table = True):
    """사용자 세션 모델, 데이터베이스에 저장되는 사용자 세션 정보."""
    __tablename__ = "sessions"
    # 세션 아이디를 기본 키로 사용(React에서 정의한 sessionId와 일치).
    id: Optional[str] = Field(default=None, primary_key=True, index=True, description="Unique identifier for the session.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False, description="Time-stamp when the session was created.")
    expires_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc) + timedelta(days=1), description="Expiration time-stamp of the session.")
    session_data: Optional[dict] = Field(default=None, description="Session data stored as a dictionary.") # JSON 형식으로 저장될 수 있음.

    # 상위 클래스와의 관계를 정의.
    user: Optional["User"] = Relationship(back_populates="sessions", sa_relationship_kwargs={"lazy": "selectin"})
    user_id: int = Field(foreign_key="users.id", description="Foreign key to the user.")

class User(SQLModel, table = True):
    """사용자 모델, 데이터베이스에 저장되는 사용자 정보."""
    __tablename__ = "users"
    id: Optional[int] = Field(default=None, primary_key=True, description="Unique identifier for the user.")
    username: str = Field(index=True, description="User-name of the user.")
    email: str = Field(index=True, description="E-mail address of the user.")
    password: str = Field(description="Password of the user.")

    # 하위 클래스와의 관계를 정의.
    advertisements: List["Advertisement"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"})
    sessions: List["Session"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"})

class Advertisement(SQLModel, table = True):
    """데이터베이스에 저장되는 광고 모델."""
    __tablename__ = "advertisements"
    id: Optional[int] = Field(default=None, primary_key=True, description="Unique identifier for the advertisement.")
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", description="Foreign key to the user who created the advertisement.")
    title: str = Field(index=True, description="Title of the advertisement.")
    description: str = Field(description="Description of the advertisement.")

    # 상위 클래스와의 관계를 정의.
    user: Optional["User"] = Relationship(back_populates="advertisements", sa_relationship_kwargs={"lazy": "selectin"})

    # 하위 클래스와의 관계를 정의.
    images: List["AdvertisementImageGeneration"] = Relationship(back_populates="advertisement", sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"})
    image_preservations: List["AdvertisementImagePreservation"] = Relationship(back_populates="advertisement", sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"})
    copies: List["AdvertisementCopy"] = Relationship(back_populates="advertisement", sa_relationship_kwargs={"cascade": "all, delete-orphan", "lazy": "selectin"})

class AdvertisementImageGeneration(SQLModel, table=True):
    """이미지 생성 요청 모델, 데이터베이스에 저장되는 이미지 생성 요청 정보."""
    __tablename__ = "advertisement_image_generation"
    id: Optional[int] = Field(default=None, primary_key=True, description="Unique identifier for the image generation request.")
    advertisement_id: int = Field(foreign_key="advertisements.id", description="Foreign key to the advertisement.")
    image_path: str = Field(description="Path of the generated image.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False, description="Time-stamp when the image generation request was created.")

    # 상위 클래스와의 관계를 정의.
    advertisement: Optional[Advertisement] = Relationship(back_populates="images", sa_relationship_kwargs={"lazy": "selectin"})

class AdvertisementImagePreservation(SQLModel, table=True):
    """이미지 보전 요청 모델, 데이터베이스에 저장되는 이미지 보전 요청 정보."""
    __tablename__ = "advertisement_image_preservation"
    id: Optional[int] = Field(default=None, primary_key=True, description="Unique identifier for the image preservation request.")
    advertisement_id: int = Field(foreign_key="advertisements.id", description="Foreign key to the advertisement.")
    preserved_image_path: str = Field(description="Path of the preserved image.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False, description="Time-stamp when the image preservation request was created.")

    # 상위 클래스와의 관계를 정의.
    advertisement: Optional[Advertisement] = Relationship(back_populates="image_preservations", sa_relationship_kwargs={"lazy": "selectin"})

class AdvertisementCopy(SQLModel, table=True):
    """광고 문구 모델, 데이터베이스에 저장되는 광고 문구 정보."""
    __tablename__ = "advertisement_copy"
    id: Optional[int] = Field(default=None, primary_key=True, description="Unique identifier for the advertisement copy.")
    advertisement_id: int = Field(foreign_key="advertisements.id", description="Foreign key to the advertisement.")
    copy_text: str = Field(description="Text of the advertisement copy.")
    ad_type: str = Field(description="Type of advertisement (e.g., instagram, blog, and poster).")
    user_prompt_for_generation: str = Field(default=None, description="User prompt for generating the advertisement copy.")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), nullable=False, description="Time-stamp when the advertisement copy was created.")

    # 상위 클래스와의 관계를 정의.
    advertisement: Optional[Advertisement] = Relationship(back_populates="copies", sa_relationship_kwargs={"lazy": "selectin"})