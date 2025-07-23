import os
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from typing import Union, List, Tuple, Optional
from services.TI_modules.TI_config import EXT_TO_FORMAT, FONTS
from services.TI_modules.font_downloader import font_downloader

class TextImageService:
    def __init__(self):
        pass

    def hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int, int]:
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4)) + (255,)

    def infer_format_from_name(self, format_name: str) -> str:
        format_name = format_name.upper()
        return format_name if format_name in EXT_TO_FORMAT.values() else "PNG"

    def get_available_fonts(self) -> List[str]:
        return list(FONTS.keys())

    def generate_text_image(
        self,
        text: str,
        font_name: str,
        font_size: int = 125,
        text_colors: Union[str, List[str]] = "#000000",
        stroke_colors: Union[str, List[str]] = "#FFFFFF",
        stroke_width: int = 0,
        word_based_colors: bool = False,
        background_size: Tuple[int, int] = (1024, 1024),  # 무시됨
        background_color: Tuple[int, int, int, int] = (255, 255, 255, 0),
        output_format: str = "PNG"
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        try:
            if font_name not in FONTS:
                return None, None, f"지원하지 않는 폰트입니다: {font_name}"

            font_url = FONTS[font_name]
            font_path = font_downloader.get_font_path(font_name, font_url)

            if not font_path or not os.path.exists(font_path):
                return None, None, f"폰트 파일을 찾을 수 없습니다: {font_name}"

            fmt = self.infer_format_from_name(output_format)
            font = ImageFont.truetype(font_path, font_size)

            dummy_img = Image.new("RGBA", (1, 1))
            draw = ImageDraw.Draw(dummy_img)

            lines = text.split('\n')
            line_heights = []
            line_widths = []
            max_line_width = 0
            total_height = 0
            line_char_info = []
            line_bbox_offsets = []

            for line in lines:
                line_char_widths = []
                line_width = 0
                max_char_height = 0
                for char in line:
                    bbox = font.getbbox(char)
                    width = bbox[2] - bbox[0]
                    height = bbox[3] - bbox[1]
                    line_char_widths.append(width)
                    line_width += width
                    max_char_height = max(max_char_height, height)
                bbox_line = font.getbbox(line)
                line_bbox_offsets.append((bbox_line[0], bbox_line[1]))  # ⬅︎ x_offset, y_offset 저장
                line_heights.append(bbox_line[3] - bbox_line[1])        # ⬅︎ 실제 텍스트 높이 사용
                line_widths.append(line_width)
                max_line_width = max(max_line_width, line_width)
                total_height += bbox_line[3] - bbox_line[1]
                line_char_info.append(line_char_widths)

            padding = 5
            image_width = max_line_width + 2 * padding
            image_height = total_height + 2 * padding + (len(lines) - 1) * 5

            img = Image.new("RGBA", (image_width, image_height), background_color)
            draw = ImageDraw.Draw(img)

            all_chars = list(text.replace('\n', ''))
            char_text_colors = []
            char_stroke_colors = []

            if word_based_colors:
                words = text.split()
                word_idx = 0
                for char in text:
                    if char == ' ' and word_idx < len(words) - 1:
                        char_text_colors.append(self.hex_to_rgb("#000000"))
                        char_stroke_colors.append(self.hex_to_rgb("#FFFFFF"))
                        word_idx += 1
                    elif char == '\n':
                        continue
                    else:
                        if isinstance(text_colors, list) and word_idx < len(text_colors):
                            char_text_colors.append(self.hex_to_rgb(text_colors[word_idx]))
                        else:
                            char_text_colors.append(self.hex_to_rgb(text_colors if isinstance(text_colors, str) else text_colors[0]))
                        if isinstance(stroke_colors, list) and word_idx < len(stroke_colors):
                            char_stroke_colors.append(self.hex_to_rgb(stroke_colors[word_idx]))
                        else:
                            char_stroke_colors.append(self.hex_to_rgb(stroke_colors if isinstance(stroke_colors, str) else stroke_colors[0]))
            else:
                text_color = text_colors if isinstance(text_colors, str) else text_colors[0]
                stroke_color = stroke_colors if isinstance(stroke_colors, str) else stroke_colors[0]
                char_text_colors = [self.hex_to_rgb(text_color)] * len(all_chars)
                char_stroke_colors = [self.hex_to_rgb(stroke_color)] * len(all_chars)

            current_y = padding
            color_idx = 0

            for line_idx, line in enumerate(lines):
                line_width = line_widths[line_idx]
                char_widths = line_char_info[line_idx]
                offset_x, offset_y = line_bbox_offsets[line_idx]  # ⬅︎ 보정값
                current_x = (image_width - line_width) // 2
                for i, char in enumerate(line):
                    draw.text(
                        (current_x - offset_x, current_y - offset_y),  # ⬅︎ 보정 적용
                        char,
                        font=font,
                        fill=char_text_colors[color_idx],
                        stroke_width=stroke_width,
                        stroke_fill=char_stroke_colors[color_idx],
                    )
                    current_x += char_widths[i]
                    color_idx += 1
                current_y += line_heights[line_idx] + 5

            if fmt in {"JPEG", "ICO", "PPM", "HEIF"}:
                img = img.convert("RGB")

            buffer = BytesIO()
            img.save(buffer, format=fmt)
            buffer.seek(0)
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            return image_base64, fmt, None

        except Exception as e:
            return None, None, f"이미지 생성 중 오류 발생: {str(e)}"

# 전역 인스턴스
text_image_service = TextImageService()
