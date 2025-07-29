# backebnd/crud/session_crud.py

import json
from typing import Optional, List
from datetime import datetime, timezone, timedelta
from sqlmodel import Session, select 
from sqlalchemy.orm.attributes import flag_modified
from database.connection import create_db_and_tables, get_session
from database.models import User as DBUser, Session as DBSession

# ****************************************** 세션 조회 ******************************************
def get_session_by_id(db: Session, session_id: str) -> Optional[DBSession]:
    """
    세션 ID로 데이터베이스에서 세션을 검색합니다.

    Args:
        db: 데이터베이스 세션.
        session_id: 검색할 세션의 아이디 (UUID 문자열).

    Returns:
        세션이 발견되면 Session 객체를 반환하고, 그렇지 않으면 None을 반환합니다.
    """
    return db.get(DBSession, session_id)

def get_sessions_by_user_id(db: Session, user_id: int) -> List[DBSession]:
    """
    사용자 ID로 데이터베이스에서 세션들을 검색합니다.

    Args:
        db: 데이터베이스 세션.
        user_id: 검색할 사용자의 아이디.

    Returns:
        해당 사용자의 세션 리스트를 반환합니다.
    """
    return db.exec(select(DBSession).where(DBSession.user_id == user_id)).all()

def get_all_sessions(db: Session) -> List[DBSession]:
    """
    데이터베이스에서 모든 세션을 검색합니다.

    Args:
        db: 데이터베이스 세션.

    Returns:
        모든 세션 리스트를 반환합니다.
    """
    return db.exec(select(DBSession)).all()


# ****************************************** 세션 생성 ******************************************
def create_session(db: Session, session_id: str, session_data: dict, user_id: Optional[int] = None, user: Optional[DBUser] = None) -> DBSession:
    """
    세션을 데이터베이스에 생성합니다.

    Args:
        db: 데이터베이스 세션.
        session_id: 새 세션의 고유 아이디 (UUID 문자열).
        session_data: 세션에 저장할 데이터.
        user: 선택 사항. 로그인한 경우 이 세션과 연결된 사용자 객체.
        user_id: 선택 사항. 로그인한 경우 이 세션과 연결된 사용자 아이디.

    Returns:
        새로 생성된 Session 객체.
    """
    now_utc = datetime.now(timezone.utc)
    expires_at = now_utc + timedelta(days = 1)  # 세션 만료 시간은 현재 시간으로부터 1일 후로 설정.

    new_session = DBSession(
        id = session_id,
        created_at = now_utc,
        expires_at = expires_at,
        session_data = session_data,
        user_id = user_id if user_id else (user.id if user else None),
        user = user if user else None
    )

    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return new_session


# ****************************************** 세션 업데이트 ******************************************
def update_session_timestamp(db: Session, session_entry: DBSession) -> DBSession:
    """
    업데이트 된 세션의 "created_at" 및 "expires_at" (또는 "last_active") 타임스탬프를 갱신합니다.

    Args:
        db: 데이터베이스 세션.
        session_entry: 업데이트할 Session 객체.

    Returns:
        업데이트 된 Session 객체.
    """
    now_utc = datetime.now(timezone.utc)
    session_entry.created_at = now_utc # 현재 시간으로 갱신.
    # 세션 만료 시간을 현재 시간으로부터 1일 후로 설정.
    session_entry.expires_at = now_utc + timedelta(days = 1)
    
    db.add(session_entry)
    db.commit()
    db.refresh(session_entry)
    return session_entry

def update_session_data(db: Session, session_entry: DBSession, new_data: dict) -> DBSession:
    """
    세션 데이터를 업데이트합니다.

    Args:
        db: 데이터베이스 세션.
        session_entry: 업데이트할 세션 객체.
        new_data: 업데이트할 데이터.
    
    Returns:
        업데이트 된 Session 객체.
    """
    current_session_data = session_entry.session_data

    if current_session_data is None:
        current_session_data = {}
    elif not isinstance(current_session_data, dict):
        try:
            current_session_data = json.loads(current_session_data)
        except (json.JSONDecodeError, TypeError):
            current_session_data = {}

    current_session_data.update(new_data)
    session_entry.session_data = current_session_data 
    
    # SQLAlchemy가 변경 사항을 감지할 수 있도록 합니다.
    flag_modified(session_entry, "session_data") 

    db.add(session_entry) 
    db.commit()          
    db.refresh(session_entry) 
    
    return session_entry


# ****************************************** 세션 삭제 ******************************************
def delete_session(db: Session, session_id: str) -> bool:
    """
    세션 ID로 데이터베이스에서 세션을 삭제합니다.

    Args:
        db: 데이터베이스 세션.
        session_id: 삭제할 세션의 아이디 (UUID 문자열).
    
    Returns:
        True 세션이 성공적으로 삭제되었고, False 세션이 존재하지 않는 경우.
    """
    session_entry = db.get(DBSession, session_id)
    if session_entry:
        db.delete(session_entry)
        db.commit()
        return True
    else:
        raise ValueError(f"세션 아이디 {session_id}에 해당하는 세션이 존재하지 않습니다.")
    return False

def delete_sessions_by_user_id(db: Session, user_id: int) -> int:
    """
    사용자 ID로 데이터베이스에서 해당 사용자의 모든 세션을 삭제합니다.

    Args:
        db: 데이터베이스 세션.
        user_id: 삭제할 사용자의 아이디.
    
    Returns:
        삭제된 세션의 수를 반환합니다.
    """
    sessions_to_delete =  get_sessions_by_user_id(db, user_id)
    if not sessions_to_delete:
        return 0  # 삭제할 세션이 없으면 0 반환.
    for session in sessions_to_delete:
        db.delete(session)
    db.commit()
    return len(sessions_to_delete)