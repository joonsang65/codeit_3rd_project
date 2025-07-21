# backend/database/create_database.py.
import os
from typing import Generator
from sqlmodel import create_engine, Session, SQLModel
from sqlalchemy.engine import Engine

# Base directory.
base_dir = os.path.dirname(os.path.abspath(__file__))

# Define data-base URL.
sqlite_file_path = f"sqlite:///{os.path.join(base_dir, 'advertisement.db')}"
database_url = os.getenv("DATABASE_URL", sqlite_file_path)
engine = create_engine(database_url, connect_args = {"check_same_thread": False}, echo = True)

# 데이터베이스 엔진 생성 함수.
def create_db_and_tables() -> None:
    """데이터베이스 테이블을 생성합니다."""
    # 모든 모델을 포함하는 SQLModel의 하위 클래스.
    SQLModel.metadata.create_all(engine)

# 데이터베이스 세션 생성 함수.
def get_session() -> Generator[Session, None, None]:
    """데이터베이스 세션을 생성합니다."""
    with Session(engine) as session:
        yield session