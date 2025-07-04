from PIL import Image, ImageOps
import io
import base64
import os
from rembg import remove
from typing import Tuple, Optional, Union
from modules.logger import setup_logger
import logging

logger = setup_logger(__name__, logging.DEBUG)

def encode_image(image: Union[str, Image.Image], size: Tuple[int, int] = (512, 512)) -> str:
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

        image = image.convert("RGB").resize(size)
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    except Exception as e:
        logger.error(f"Failed to encode image: {e}")
        raise

def encode_images(config: dict,
                  product_img: Optional[Union[str, Image.Image]] = None,
                  ref_img: Optional[Union[str, Image.Image]] = None
) -> Tuple[str, Optional[str]]:
    """
    설정에 따라 제품 이미지와 (옵션) 참고 이미지를 base64로 인코딩합니다.

    Args:
        config (dict): 설정 객체
        product_img (str or PIL.Image): 제품 이미지 경로 또는 이미지
        ref_img (str or PIL.Image): 참조 이미지 경로 또는 이미지 (Optional)

    Returns:
        Tuple[str, Optional[str]]: 제품 이미지 b64, 참조 이미지 b64 (없으면 None)
    """
    input_size = tuple(config["image"]["input_size"])

    # 기본 경로 사용
    if product_img is None:
        product_img = config["paths"]["product_image"]
    if ref_img is None and "reference_image" in config["paths"]:
        ref_img = config["paths"]["reference_image"]

    product_b64 = encode_image(product_img, size=input_size)

    ref_b64 = None
    if ref_img:
        try:
            if isinstance(ref_img, str) and not os.path.exists(ref_img):
                logger.warning(f"Reference image path does not exist: {ref_img}")
            else:
                ref_b64 = encode_image(ref_img, size=input_size)
        except Exception as e:
            logger.warning(f"Failed to encode reference image: {e}")

    return product_b64, ref_b64

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

def overlay_product(background: Image.Image, product: Image.Image, position=(120,360)):
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

def ensure_dir(path: str) -> None:
    """
    지정한 경로가 없으면 디렉토리를 생성합니다.
    """
    if not os.path.exists(path):
        os.makedirs(path)
        logger.info(f"Created directory: {path}")

def create_mask_from_product(product_image: Image.Image, threshold: int = 10) -> Image.Image:
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