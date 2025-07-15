# backend/app/cache.py
from threading import Lock
from PIL import Image
from typing import Dict, Union, Optional
import json

# 사용자별 캐시 (스레드 안전)
"""
세션 ID를 키로 사용하여 이미지나 문자열 데이터를 저장하는 캐시
- 세션 ID: str
- 캐시 데이터: Dict[str, Union[Image.Image, str]]
- 예시:
  {
      "session_123": {
          "resized_img": <PIL.Image.Image>,
          "back_rm_canv": <PIL.Image.Image>,
          "user_prompt": "사용자 입력",
          "generated_text": "생성된 텍스트"
      }
  }
"""
session_cache: Dict[str, Dict[str, Union[Image.Image, str]]] = {}
cache_lock = Lock()

def get_session_cache(session_id: str) -> Dict[str, Union[Image.Image, str]]:
    """세션 ID로 캐시 조회"""
    with cache_lock:
        return session_cache.get(session_id, {})

def set_session_cache(session_id: str, cache_data: Dict[str, Union[Image.Image, str]]):
    """세션 ID로 캐시 설정"""
    with cache_lock:
        session_cache[session_id] = cache_data

def update_session_cache(session_id: str, key: str, value: Union[Image.Image, str]):
    """세션 ID로 특정 키-값 쌍 업데이트"""
    with cache_lock:
        if session_id not in session_cache:
            session_cache[session_id] = {}
        session_cache[session_id][key] = value

def clear_session_cache(session_id: str):
    """세션 ID로 캐시 삭제"""
    with cache_lock:
        session_cache.pop(session_id, None)

def get_all_session_ids() -> list:
    """모든 세션 ID 목록 반환 (디버깅용)"""
    with cache_lock:
        return list(session_cache.keys())