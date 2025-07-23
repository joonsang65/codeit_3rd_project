import yaml
from typing import Any, Dict, Optional, Tuple, Union
import logging
import io
import base64
import os
import time
from functools import wraps
from PIL import Image, ImageFilter
from rembg import remove
import cv2
import numpy as np

def load_config(path: str = "config.yaml") -> Dict[str, Any]:
    '''
    설정 로드
    
    Args:
        - config.yaml이 저장되어있는 경로 (예: 현재경로 "config.yaml", 상위 폴더 "../config.yaml")
    
    returns:
        - config dictionary
    '''
    try:
        with open(path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        # 필수 섹션 검사
        for key in ["sd_pipeline", "paths"]:
            if key not in config:
                raise ValueError(f"Config missing required section: {key}")
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"[ERROR] 설정 파일을 찾을 수 없습니다: {path}")
    except yaml.YAMLError as e:
        raise ValueError(f"[ERROR] YAML 파싱 오류: {e}")


def setup_logger(name: str, level: int = logging.INFO, log_to_file: Optional[str] = None) -> logging.Logger:
    '''로거를 설정한다.'''
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.hasHandlers():
        logger.handlers.clear()

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

def log_execution_time(label=None):
    '''각 기능의 추론시간 파악을 위한 데코레이터'''
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
    keep_aspect_ratio: bool = True
) -> str:
    '''
    GPT에서 그림을 이해할 수 있도록 하는 전처리 작업으로, 
    이미지를 base64로 인코딩한다.
    Args:
        - image: 변환하려는 이미지
        - size: 이미지 크기
    
    returns:
        - image (base64 encoded)
    '''
    try:
        logger.info(f"Encoding image to size {size}")
        if isinstance(image, str):
            logger.debug(f"Opening image from path: {image}")
            image = Image.open(image)

        if not isinstance(image, Image.Image):
            raise TypeError(f"Unsupported image type: {type(image)}")

        image = image.convert("RGB")

        if size:
            image = image.copy()
            if keep_aspect_ratio:
                image.thumbnail(size, Image.Resampling.LANCZOS)
            else:
                image = image.resize(size, Image.Resampling.LANCZOS)

        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    except Exception as e:
        logger.error(f"Failed to encode image: {e}")
        raise


@log_execution_time(label="Remove Background...")
def remove_background(image: Union[str, Image.Image]) -> Tuple[Image.Image, Image.Image]:
    """
    이미지에서 배경을 제거하고 RGBA로 반환합니다.
    
    Args:
        image (str or PIL.Image.Image): 파일 경로 또는 PIL 이미지 객체

    Returns:
        Tuple[Image.Image, Image.Image]: (원본 RGBA 이미지, 배경제거된 RGBA 이미지)
    """
    try:
        # 1. 이미지 로딩 및 바이트 변환
        if isinstance(image, str):
            logger.info(f"🔍 Removing background from image path: {image}")
            with open(image, "rb") as f:
                input_data = f.read()
            original_image = Image.open(io.BytesIO(input_data)).convert("RGBA")

        elif isinstance(image, Image.Image):
            logger.info("🔍 Removing background from PIL.Image object")
            buffered = io.BytesIO()
            image.convert("RGBA").save(buffered, format="PNG")
            input_data = buffered.getvalue()
            original_image = image.convert("RGBA")
        else:
            raise TypeError(f"❌ Unsupported image type: {type(image)}")

        # 2. rembg 처리
        output_data = remove(input_data)
        transparent_image = Image.open(io.BytesIO(output_data)).convert("RGBA")

        # 3. 사이즈 불일치 로그
        if original_image.size != transparent_image.size:
            logger.warning(f"⚠️ Image size mismatch: original={original_image.size}, result={transparent_image.size}")

        return original_image, transparent_image

    except Exception as e:
        logger.error(f"❌ Background removal failed: {str(e)}")
        raise


@log_execution_time(label="Resize to Ratio")
def resize_to_ratio(image: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
    '''이미지의 크기를 resample 기법으로 변환한다.'''
    try:
        image = image.convert("RGB")
        original_width, original_height = image.size
        target_width, target_height = target_size

        ratio = min(target_width / original_width, target_height / original_height)
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)

        return image.resize((new_width, new_height), Image.LANCZOS)
    except Exception as e:
        logger.error(f"Resize failed: {e}")
        raise
    
@log_execution_time(label="Resize with padding")
def resize_with_padding(image, size=(512,512), fill_color=(255,255,255)):
    '''
    입력 이미지의 비율을 가로형, 세로형, 사각형으로 변환시킬 때 중점이 되는 제품 이미지의
    비율이 망가지지 않도록 padding으로 조정.
    '''
    image = image.convert("RGB")
    image.thumbnail(size, Image.LANCZOS)
    new_img = Image.new("RGB", size, fill_color)
    paste_x = (size[0] - image.size[0]) // 2
    paste_y = (size[1] - image.size[1]) // 2
    new_img.paste(image, (paste_x, paste_y))
    return new_img

@log_execution_time(label="Create Masking image...")
def create_mask(product_image: Image.Image, threshold: int = 250, blur_radius: int = 5, rebin:bool = False) -> Image.Image:
    '''
    이미지의 마스크를 생성한다. Gaussian Blur를 추가하여 이미지 경계에 대한 정보를 흐릿하게 만들었다.

    Args:
        - product_image: 마스킹 작업이 필요한 제품 이미지
        - threshold: 마스킹 생성시 설정하는 임계치 (0~254)
        - blur_radius: 경계 정보에 추가할 노이즈의 정도
    
    returns:
        - mask 이미지
    '''
    logger.info("Creating soft mask from alpha channel")

    if product_image.mode != "RGBA":
        logger.warning(f"Image mode is {product_image.mode}, converting to RGBA")
        product_image = product_image.convert("RGBA")

    try:
        alpha = product_image.getchannel("A")
        mask = alpha.point(lambda a: 255 if a > threshold else 0).convert("L")

        if blur_radius > 0:
            logger.info(f"Applying GaussianBlur with radius {blur_radius}")
            mask = mask.filter(ImageFilter.GaussianBlur(radius=blur_radius))

        if rebin:
            logger.info("Re-binarizing blurred mask")
            mask = mask.point(lambda p: 255 if p > 128 else 0)

        return mask
    except Exception as e:
        logger.error(f"Failed to create mask: {e}")
        raise


@log_execution_time(label="Overlaying product image...")
def overlay_product(background: Image.Image, product: Image.Image, position: Tuple[int, int] = (120, 360)):
    '''이미지를 배경 혹은 캔버스에 overlay한다. 포지션 입력으로 제품의 위치를 변경할 수 있다.'''
    try:
        bg = background.convert("RGBA")
        fg = product.convert("RGBA")

        if position[0] + fg.width > bg.width or position[1] + fg.height > bg.height:
            logger.warning("Overlay image exceeds background dimensions")

        bg.paste(fg, position, fg)
        return bg
    except Exception as e:
        logger.error(f"Overlay failed: {e}")
        raise

def ensure_dir(path: str) -> None:
    '''폴더 존재 확인'''
    if os.path.exists(path):
        if not os.path.isdir(path):
            raise NotADirectoryError(f"{path} exists and is not a directory")
    else:
        os.makedirs(path, exist_ok=True)
        logger.info(f"Created directory: {path}")

def get_canny(image_pil):
    '''윤곽선 추출'''
    image_np = np.array(image_pil.convert("RGB"))
    gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    return Image.fromarray(edges_rgb)

def get_depth_midas(image_pil):
    '''음영 정보 추출'''
    import torch.hub
    image_np = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)
    midas = torch.hub.load("intel-isl/MiDaS", "DPT_Large").to("cuda").eval()
    transform = torch.hub.load("intel-isl/MiDaS", "transforms").dpt_transform
    input_tensor = transform(image_np).to("cuda")
    with torch.no_grad():
        prediction = midas(input_tensor)
        prediction = torch.nn.functional.interpolate(
            prediction.unsqueeze(1), size=image_np.shape[:2], mode="bicubic", align_corners=False
        ).squeeze()
    depth_np = prediction.cpu().numpy()
    depth_norm = cv2.normalize(depth_np, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
    return Image.fromarray(depth_norm).convert("L")

logger = setup_logger(__name__, logging.DEBUG)