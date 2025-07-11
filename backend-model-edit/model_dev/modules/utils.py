import yaml
from typing import Any, Dict, Optional
import logging
import io
import base64
import os
from rembg import remove
from typing import Tuple, Optional, Union
import time
from functools import wraps
from PIL import Image

def load_config(path: str = "model_dev/config.yaml") -> Dict[str, Any]:
    """
    YAML 구성 파일을 로드하여 딕셔너리로 반환합니다.

    Args:
        path (str): YAML 파일 경로

    Returns:
        dict: 구성 데이터
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        raise FileNotFoundError(f"[ERROR] 설정 파일을 찾을 수 없습니다: {path}")
    except yaml.YAMLError as e:
        raise ValueError(f"[ERROR] YAML 파싱 오류: {e}")

def setup_logger(name: str, level: int = logging.INFO, log_to_file: Optional[str] = None) -> logging.Logger:
    """
    모듈별 로거를 설정합니다.

    Args:
        name (str): 로거 이름
        level (int): 로그 레벨
        log_to_file (str, optional): 로그를 파일로 저장할 경로

    Returns:
        Logger: 설정된 로거 인스턴스
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if not logger.handlers:
        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(level)
        logger.addHandler(stream_handler)

        if log_to_file:
            file_handler = logging.FileHandler(log_to_file, encoding="utf-8")
            file_handler.setFormatter(formatter)
            file_handler.setLevel(level)
            logger.addHandler(file_handler)

    return logger

logger = setup_logger(__name__, logging.DEBUG)

def log_execution_time(label=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = label or func.__name__
            logger.debug(f"[START] {name}")
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            logger.info(f"[TIME] {name} 실행 시간: {elapsed:.3f}초")
            return result
        return wrapper
    return decorator

@log_execution_time(label="Encode image to base64...")
def encode_image(
    image: Union[str, Image.Image], 
    size: Optional[Tuple[int, int]] = None, 
    keep_aspect_ratio:bool = True
) -> str:
    """
    이미지를 리사이즈하고 base64로 인코딩합니다.

    Args:
        image (str or PIL.Image.Image): 이미지 경로 또는 Image 객체
        size (Tuple[int, int]): 리사이즈 크기

    Returns:
        str: base64 인코딩 문자열
    """
    try:
        logger.info(f"Encoding image to size {size}")
        if isinstance(image, str):
            logger.debug(f"Opening image from path: {image}")
            image = Image.open(image)

        if not isinstance(image, Image.Image):
            raise TypeError(f"Unsupported image type: {type(image)}")

        image = image.convert("RGB")

        if size:
            if keep_aspect_ratio:
                image.thumbnail(size, Image.Resampling.LANCZOS)
            else:
                image = image.resize(size)
        
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    except Exception as e:
        logger.error(f"Failed to encode image: {e}")
        raise

@log_execution_time(label="Remove Background...")
def remove_background(image: Union[str, Image.Image]) -> Tuple[Image.Image, Image.Image]:
    """
    rembg를 사용해 이미지 배경을 제거합니다.

    Args:
        image (str or PIL.Image.Image): 이미지 경로 또는 Image 객체

    Returns:
        Tuple[PIL.Image, PIL.Image]: (원본 이미지, 배경 제거된 이미지)
    """
    try:
        # 경로일 경우 파일 읽기
        if isinstance(image, str):
            logger.info(f"Removing background from image path: {image}")
            with open(image, "rb") as f:
                input_data = f.read()
            original_image = Image.open(image).convert("RGBA")
        elif isinstance(image, Image.Image):
            logger.info("Removing background from PIL.Image object")
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            input_data = buffered.getvalue()
            original_image = image.convert("RGBA")
        else:
            raise TypeError(f"Unsupported image type: {type(image)}")

        # rembg로 배경 제거
        output_data = remove(input_data)
        transparent_image = Image.open(io.BytesIO(output_data)).convert("RGBA")

        return original_image, transparent_image

    except Exception as e:
        logger.error(f"Background removal failed: {e}")
        raise
    
def resize_to_ratio(image: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
    """
    이미지를 주어진 크기로 리사이즈합니다.

    Args:
        image (PIL.Image): 리사이즈할 이미지.
        target_size (tuple): 목표 크기 (width, height).

    Returns:
        PIL.Image: 리사이즈된 이미지.
    """
    return image.resize(target_size, Image.LANCZOS)

@log_execution_time(label="Create Masking image...")
def create_mask(product_image: Image.Image, threshold: int = 250) -> Image.Image:
    """
    RGBA 제품 이미지에서 알파 채널을 기반으로 마스크 이미지를 생성합니다.

    Args:
        product_image (PIL.Image): RGBA 이미지
        threshold (int): 알파값 기준. 이 값보다 작으면 '배경'(흰색), 크면 '제품'(검정)

    Returns:
        PIL.Image: 마스크 이미지 (제품 제외 영역이 흰색인 1채널 이미지)
    """
    logger.info("Creating mask from alpha channel")

    if product_image.mode != "RGBA":
        logger.warning(f"Image mode is {product_image.mode}, converting to RGBA")
        product_image = product_image.convert("RGBA")

    try:
        alpha = product_image.getchannel("A")
        mask = Image.eval(alpha, lambda a: 255 if a > threshold else 0)
        return mask.convert("L")
    except Exception as e:
        logger.error(f"Failed to create mask: {e}")
        raise

@log_execution_time(label="Overlaying product image...")
def overlay_product(background: Image.Image, product: Image.Image, position: Tuple[int, int]=(120,360)):
    """
    배경 이미지 위에 제품 이미지를 지정한 위치에 합성합니다.

    Args:
        background (PIL.Image): 배경 이미지.
        product (PIL.Image): 합성할 제품 이미지.
        position (tuple): 제품을 배치할 좌표 (x, y).

    Returns:
        PIL.Image: 합성된 최종 이미지.
    """
    bg = background.convert("RGBA")
    fg = product.convert("RGBA")
    bg.paste(fg, position, fg)
    return bg

def ensure_dir(path: str) -> None:
    """
    지정한 경로가 없으면 디렉토리를 생성합니다.
    """
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        logger.info(f"Created directory: {path}")


