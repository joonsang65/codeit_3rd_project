from PIL import Image, ImageDraw, ImageFont
import os
import streamlit as st

# 확장자 → 포맷 매핑 (Pillow에서 지원하는 주요 저장 포맷들)
EXT_TO_FORMAT = {
    ".jpg": "JPEG",
    ".jpeg": "JPEG",
    ".png": "PNG",
    ".bmp": "BMP",
    ".gif": "GIF",
    ".tif": "TIFF",
    ".tiff": "TIFF",
    ".webp": "WEBP",
    ".ico": "ICO",
    ".ppm": "PPM",
    ".pbm": "PPM",
    ".pgm": "PPM",
    ".pnm": "PPM",
    ".heif": "HEIF",
    ".heic": "HEIF",
}


def infer_format_from_path(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return EXT_TO_FORMAT.get(ext, None)


def render_text_image(
    text: str,
    font_path: str,
    font_size: int = 64,
    output_path: str = "output.png",
    text_color: tuple = (0, 0, 0, 255),
    background_size: tuple = (512, 512),
    background_color: tuple = (255, 255, 255, 0),
):
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Font file not found: {font_path}")

    # 포맷 추론
    fmt = infer_format_from_path(output_path)
    if fmt is None:
        raise ValueError(f"❌ 지원하지 않는 이미지 포맷입니다: {output_path}")

    img = Image.new("RGBA", background_size, background_color)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, font_size)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    position = ((background_size[0] - text_width) // 2, (background_size[1] - text_height) // 2)

    draw.text(position, text, font=font, fill=text_color)

    # JPEG, ICO 등 RGBA 지원 안 되는 포맷은 RGB로 변환
    if fmt in {"JPEG", "ICO", "PPM", "HEIF"}:
        img = img.convert("RGB")

    img.save(output_path, format=fmt)
    return output_path, fmt