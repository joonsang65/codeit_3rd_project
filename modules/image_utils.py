from PIL import Image
import io
import base64
from rembg import remove
import os
from modules.logger import setup_logger

logger = setup_logger(__name__)

def encode_image(image_path, size=(512, 512)):
    """
    이미지를 주어진 크기로 리사이즈하고 base64로 인코딩합니다.

    Args:
        image_path (str): 이미지 파일 경로.
        size (tuple): 리사이즈할 크기 (width, height).

    Returns:
        str: base64 인코딩된 이미지 문자열.
    """
    logger.info(f"Encoding image: {image_path} to size {size}")
    image = Image.open(image_path).convert("RGB").resize(size)
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def remove_background(image_path):
    """
    rembg를 사용해 이미지 배경을 제거합니다.

    Args:
        image_path (str): 이미지 파일 경로.

    Returns:
        PIL.Image: 배경이 제거된 이미지.
    """
    logger.info(f"Removing background from image: {image_path}")
    with open(image_path, "rb") as f:
        input_data = f.read()
    output_data = remove(input_data)
    return Image.open(io.BytesIO(output_data))

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
    fg = product.convert("RGBA").resize((256, 256))
    bg.paste(fg, position, fg)
    return bg

def resize_to_ratio(image: Image.Image, target_size):
    """
    이미지를 주어진 크기로 리사이즈합니다.

    Args:
        image (PIL.Image): 리사이즈할 이미지.
        target_size (tuple): 목표 크기 (width, height).

    Returns:
        PIL.Image: 리사이즈된 이미지.
    """
    return image.resize(target_size, Image.LANCZOS)

def ensure_dir(path):
    """
    지정한 경로가 없으면 디렉토리를 생성합니다.

    Args:
        path (str): 생성할 디렉토리 경로.
    """
    if not os.path.exists(path):
        os.makedirs(path)
