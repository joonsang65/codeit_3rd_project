from PIL import Image, ImageDraw, ImageFont
import os
import requests

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
    ".heic": "HEIC",
}


def infer_format_from_path(path: str) -> str:
    ext = os.path.splitext(path)[1].lower()
    return EXT_TO_FORMAT.get(ext, None)


def hex_to_rgb(hex_color):
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4)) + (255,)

def download_font(font_name, font_url, save_dir="downloaded_fonts"):
    os.makedirs(save_dir, exist_ok=True)
    ext = os.path.splitext(font_url)[1]
    save_path = os.path.join(save_dir, f"{font_name}{ext}")

    if os.path.exists(save_path):
        print(f"이미 존재하는 폰트 사용: {save_path}")
        return save_path

    print(f"폰트 다운로드 중: {font_name}")
    response = requests.get(font_url)
    if response.status_code == 200:
        with open(save_path, "wb") as f:
            f.write(response.content)
        print(f"다운로드 완료: {save_path}")
        return save_path
    else:
        print(f"다운로드 실패 - 상태 코드: {response.status_code}")
        print(f"응답 내용 일부: {response.text[:300]}")
        raise RuntimeError(f"다운로드 실패: {font_url}")

def render_text_image(
    text: str,
    font_path: str,
    font_size: int = 64,
    output_path: str = "output.png",
    text_colors: list[str] | str = "#000000",
    background_size: tuple = (512, 512),
    background_color: tuple = (255, 255, 255, 0),
    stroke_colors: list[str] | str = "#FFFFFF",
    stroke_width: int = 0,
    word_based_colors: bool = False,
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

    # Determine character colors based on word_based_colors flag
    char_text_colors = []
    char_stroke_colors = []

    if word_based_colors:
        words = text.split()
        word_idx = 0
        char_idx_in_word = 0
        for char in text:
            if char == ' ' and word_idx < len(words) - 1:
                char_text_colors.append(hex_to_rgb("#000000")) # Space color (can be customized)
                char_stroke_colors.append(hex_to_rgb("#FFFFFF")) # Space stroke color
                char_idx_in_word = 0
                word_idx += 1
            else:
                if isinstance(text_colors, list) and word_idx < len(text_colors):
                    char_text_colors.append(hex_to_rgb(text_colors[word_idx]))
                else:
                    char_text_colors.append(hex_to_rgb(text_colors))

                if isinstance(stroke_colors, list) and word_idx < len(stroke_colors):
                    char_stroke_colors.append(hex_to_rgb(stroke_colors[word_idx]))
                else:
                    char_stroke_colors.append(hex_to_rgb(stroke_colors))
                char_idx_in_word += 1
    else:
        # If not word-based, use single colors for all characters
        char_text_colors = [hex_to_rgb(text_colors)] * len(text)
        char_stroke_colors = [hex_to_rgb(stroke_colors)] * len(text)

    # Calculate total text width and height for centering
    total_text_width = 0
    char_widths = []
    for char in text:
        bbox = draw.textbbox((0, 0), char, font=font)
        char_width = bbox[2] - bbox[0]
        total_text_width += char_width
        char_widths.append(char_width)

    # Calculate text height (assuming all characters have similar height for simplicity)
    if text:
        bbox_first_char = draw.textbbox((0, 0), text[0], font=font)
        text_height = bbox_first_char[3] - bbox_first_char[1]
    else:
        text_height = 0 # Handle empty text case

    start_x = (background_size[0] - total_text_width) // 2
    start_y = (background_size[1] - text_height) // 2

    current_x = start_x

    for i, char in enumerate(text):
        # Draw each character individually
        draw.text(
            (current_x, start_y),
            char,
            font=font,
            fill=char_text_colors[i],
            stroke_width=stroke_width,
            stroke_fill=char_stroke_colors[i],
        )
        current_x += char_widths[i] # Move x position for the next character

    # RGBA 지원 안 되는 포맷은 RGB로 변환
    if fmt in {"JPEG", "ICO", "PPM", "HEIF"}:
        img = img.convert("RGB")

    return img, fmt
