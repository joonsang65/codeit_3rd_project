# backebnd/crud/user_crud.py

from typing import Optional, List
from sqlmodel import Session, select 
from ..database.models import User as DBUser, Session as DBSession, Advertisement as DBAdvertisement

# ****************************************** 사용자 조회 ******************************************
def get_user_by_id(db: Session, user_id: int) -> Optional[DBUser]:
    """
    사용자 아이디로 데이터베이스에서 사용자를 검색합니다.

    Args:
        db: 데이터베이스 세션.
        user_id: 검색할 사용자의 아이디.

    Returns:
        사용자가 발견되면 User 객체를 반환하고, 그렇지 않으면 None을 반환합니다.
    """
    return db.get(DBUser, user_id)

def get_user_by_email(db: Session, email: str) -> Optional[DBUser]:
    """
    이메일로 데이터베이스에서 사용자를 검색합니다.

    Args:
        db: 데이터베이스 세션.
        email: 검색할 사용자의 이메일 주소.

    Returns:
        사용자가 발견되면 User 객체를 반환하고, 그렇지 않으면 None을 반환합니다.
    """
    return db.exec(select(DBUser).where(DBUser.email == email)).one_or_none()

def get_all_users(db: Session) -> List[DBUser]:
    """
    데이터베이스에서 모든 사용자를 검색합니다.

    Args:
        db: 데이터베이스 세션.

    Returns:
        모든 사용자 리스트를 반환합니다.
    """
    return db.exec(select(DBUser)).all()

# ****************************************** 사용자 생성 ******************************************
def create_user(db: Session, username: str, email: str, hashed_password: str) -> DBUser:
    """
    사용자 정보를 데이터베이스에 생성합니다.

    Args:
        db: 데이터베이스 세션.
        username: 사용자의 이름.
        email: 사용자의 이메일 주소.
        hashed_password: 해시된 비밀번호.

    Returns:
        새로 생성된 User 객체.
    """
    new_user = DBUser(username=username, email=email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# ****************************************** 사용자 업데이트 ******************************************
def update_user(
        db: Session, 
        user_entry: DBUser, 
        new_username: Optional[str] = None, 
        new_email: Optional[str] = None,
        new_hashed_password: Optional[str] = None
) -> DBUser:
    """
    사용자 정보를 업데이트합니다.

    Args:
        db: 데이터베이스 세션.
        user_entry: 업데이트할 User 객체.
        new_username: 새 사용자 이름 (선택 사항).
        new_email: 새 이메일 주소 (선택 사항).
        new_hashed_password: 새 해시된 비밀번호 (선택 사항).

    Returns:
        업데이트된 User 객체.
    """
    if new_username:
        user_entry.username = new_username
    if new_email:
        user_entry.email = new_email
    if new_hashed_password:
        user_entry.hashed_password = new_hashed_password

    db.add(user_entry)
    db.commit()
    db.refresh(user_entry)
    return user_entry

# ****************************************** 사용자 삭제 ******************************************
def delete_user(db: Session, user_id: int) -> bool:
    """
    사용자 정보를 데이터베이스에서 삭제합니다.

    Args:
        db: 데이터베이스 세션.
        user_id: 삭제할 사용자의 아이디.
    
    Returns:
        True 사용자가 성공적으로 삭제되었고, False 사용자가 존재하지 않는 경우.
    """
    user_to_delete = db.get(DBUser, user_id)
    if user_to_delete:
        db.delete(user_to_delete)
        db.commit()
        return True
    return False