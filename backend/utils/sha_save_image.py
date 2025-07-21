# backend/utils/sha_save_image.py

import hashlib, io, os
from typing import Union
from PIL import Image

def generate_sha_filename(image_bytes: bytes) -> str:
    """이미지 바이트로부터 SHA-256 해시를 생성하고, 이를 파일 이름으로 변환."""
    sha256_hash = hashlib.sha256(image_bytes).hexdigest()
    return f"{sha256_hash}.png"

def save_image_to_disk(image: Image.Image, directory: Union[str, os.PathLike]) -> str:
    """Pillow 이미지 객체를 디스크에 저장하고, 저장된 파일 경로(URL 상대 경로)를 변환."""
    os.makedirs(directory, exist_ok = True)
    
    # 이미지 바이트 스트림을 생성
    buffer = io.BytesIO()
    image.save(buffer, format = "PNG")
    image_bytes = buffer.getvalue()
    
    file_name = generate_sha_filename(image_bytes)
    file_path = os.path.join(directory, file_name)

    # 디스크에 이미지 저장
    with open(file_path, "wb") as f:
        f.write(image_bytes)
    
    return file_path