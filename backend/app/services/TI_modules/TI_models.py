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
        """HEX 색상을 RGBA 튜플로 변환"""
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4)) + (255,)
    
    def infer_format_from_name(self, format_name: str) -> str:
        """포맷 이름에서 PIL 포맷 추론"""
        format_name = format_name.upper()
        return format_name if format_name in EXT_TO_FORMAT.values() else "PNG"
    
    def get_available_fonts(self) -> List[str]:
        """사용 가능한 폰트 목록 반환"""
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
        background_size: Tuple[int, int] = (1024, 1024),
        background_color: Tuple[int, int, int, int] = (255, 255, 255, 0),
        output_format: str = "PNG"
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        텍스트 이미지를 생성합니다.
        
        Returns:
            (base64_image, format, error_message)
        """
        try:
            # 폰트 확인 및 다운로드
            if font_name not in FONTS:
                return None, None, f"지원하지 않는 폰트입니다: {font_name}"
            
            font_url = FONTS[font_name]
            font_path = font_downloader.get_font_path(font_name, font_url)
            
            if not font_path or not os.path.exists(font_path):
                return None, None, f"폰트 파일을 찾을 수 없습니다: {font_name}"
            
            # 포맷 확인
            fmt = self.infer_format_from_name(output_format)
            
            # 이미지 생성
            img = Image.new("RGBA", background_size, background_color)
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype(font_path, font_size)
            
            # 문자별 색상 결정
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
                # 단일 색상 사용
                text_color = text_colors if isinstance(text_colors, str) else text_colors[0]
                stroke_color = stroke_colors if isinstance(stroke_colors, str) else stroke_colors[0]
                char_text_colors = [self.hex_to_rgb(text_color)] * len(text)
                char_stroke_colors = [self.hex_to_rgb(stroke_color)] * len(text)
            
            # 텍스트 중앙 정렬을 위한 크기 계산
            total_text_width = 0
            char_widths = []
            
            for char in text:
                bbox = draw.textbbox((0, 0), char, font=font)
                char_width = bbox[2] - bbox[0]
                total_text_width += char_width
                char_widths.append(char_width)
            
            # 텍스트 높이 계산
            if text:
                bbox_first_char = draw.textbbox((0, 0), text[0], font=font)
                text_height = bbox_first_char[3] - bbox_first_char[1]
            else:
                text_height = 0
            
            start_x = (background_size[0] - total_text_width) // 2
            start_y = (background_size[1] - text_height) // 2
            current_x = start_x
            
            # 각 문자 그리기
            for i, char in enumerate(text):
                draw.text(
                    (current_x, start_y),
                    char,
                    font=font,
                    fill=char_text_colors[i],
                    stroke_width=stroke_width,
                    stroke_fill=char_stroke_colors[i],
                )
                current_x += char_widths[i]
            
            # RGB 변환이 필요한 포맷 처리
            if fmt in {"JPEG", "ICO", "PPM", "HEIF"}:
                img = img.convert("RGB")
            
            # Base64로 변환
            buffer = BytesIO()
            img.save(buffer, format=fmt)
            buffer.seek(0)
            
            image_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return image_base64, fmt, None
            
        except Exception as e:
            return None, None, f"이미지 생성 중 오류 발생: {str(e)}"

# 전역 인스턴스
text_image_service = TextImageService()