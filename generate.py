from PIL import Image, ImageDraw, ImageFont
import os

def render_text_image(
    text: str,
    font_path: str,
    font_size: int = 64,
    output_path: str = "output.png",
    text_color: tuple = (0, 0, 0, 255),
    background_size: tuple = (512, 512),
    background_color: tuple = (255, 255, 255, 0),  # 투명 배경 하려면 마지막 값 0 하면 됨
    # background_color=(135, 206, 235, 255),  # 하늘색 배경  -> 확인을 위함
    align: str = "center"
):
    if not os.path.exists(font_path):
        raise FileNotFoundError(f"Font file not found: {font_path}")

    img = Image.new("RGBA", background_size, background_color)
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(font_path, font_size)

    # 수정된 부분
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    if align == "center":
        position = ((background_size[0] - text_width) // 2, (background_size[1] - text_height) // 2)
    elif align == "left":
        position = (10, (background_size[1] - text_height) // 2)
    elif align == "right":
        position = (background_size[0] - text_width - 10, (background_size[1] - text_height) // 2)
    else:
        raise ValueError("align must be 'center', 'left', or 'right'")

    draw.text(position, text, font=font, fill=text_color)
    img.save(output_path)

    return output_path

