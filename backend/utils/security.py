# backend/utils/security.py

import bcrypt, hashlib

def get_password_hash(password: str) -> str:
    """비밀번호를 해시화하여 저장."""
    # bcrypt를 사용하여 비밀번호 해시 생성
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """입력된 비밀번호와 저장된 해시를 비교하여 일치 여부 확인."""
    # bcrypt를 사용하여 비밀번호 검증
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))