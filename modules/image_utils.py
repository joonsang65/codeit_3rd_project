from PIL import Image
import io
import base64
from rembg import remove
import os
from modules.logger import setup_logger

logger = setup_logger(__name__)

def encode_image(image_path, size=(512, 512)):
    logger.info(f"Encoding image: {image_path} to size {size}")
    image = Image.open(image_path).convert("RGB").resize(size)
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

def remove_background(image_path):
    logger.info(f"Removing background from image: {image_path}")
    with open(image_path, "rb") as f:
        input_data = f.read()
    output_data = remove(input_data)
    return Image.open(io.BytesIO(output_data))

def overlay_product(background: Image.Image, product: Image.Image, position=(120,360)):
    bg = background.convert("RGBA")
    fg = product.convert("RGBA").resize((256, 256))
    bg.paste(fg, position, fg)
    return bg

def resize_to_ratio(image: Image.Image, target_size):
    return image.resize(target_size, Image.LANCZOS)

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
