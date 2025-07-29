from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Union

class TextImageRequest(BaseModel):
    """
    텍스트 이미지 생성 요청 모델
    
    텍스트와 폰트, 색상 등의 설정을 받아 이미지를 생성하기 위한 요청 스키마입니다.
    단일 색상 또는 단어별 색상 적용이 가능하며, 다양한 이미지 포맷을 지원합니다.
    """
    
    text: str = Field(
        ..., 
        description="이미지에 넣을 텍스트",
        example="안녕하세요 반갑습니다"
    )
    
    font_name: str = Field(
        ..., 
        description="사용할 폰트 이름",
        example="본고딕_BOLD"
    )
    
    font_size: int = Field(
        default=125, 
        ge=10, 
        le=100, 
        description="글자 크기 (50-200 사이)",
        example=50
    )
    
    text_colors: Union[str, List[str]] = Field(
        default="#000000", 
        description="텍스트 색상 (단색 또는 단어별 색상 리스트)",
        example=["#FF0000", "#0000FF"]
    )
    
    stroke_colors: Union[str, List[str]] = Field(
        default="#FFFFFF", 
        description="테두리 색상 (단색 또는 단어별 색상 리스트)",
        example=["#FFFFFF", "#FFFF00"]
    )
    
    stroke_width: int = Field(
        default=0, 
        ge=0, 
        le=10, 
        description="테두리 굵기 (0-10 사이)",
        example=2
    )
    
    word_based_colors: bool = Field(
        default=False, 
        description="단어별 색상 적용 여부",
        example=True
    )
    
    background_size: tuple = Field(
        default=(1024, 1024), 
        description="배경 크기 (width, height)",
        example=(800, 400)
    )
    
    background_color: tuple = Field(
        default=(255, 255, 255, 0), 
        description="배경 색상 (R, G, B, A)",
        example=(255, 255, 255, 0)
    )
    
    output_format: str = Field(
        default="PNG", 
        description="출력 이미지 포맷",
        example="PNG"
    )

    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        """텍스트가 비어있지 않은지 검증"""
        if not v or not v.strip():
            raise ValueError('텍스트는 비어있을 수 없습니다.')
        return v.strip()

    @field_validator('text_colors')
    @classmethod
    def validate_text_colors(cls, v: Union[str, List[str]]) -> Union[str, List[str]]:
        """텍스트 색상 유효성 검증"""
        if isinstance(v, str):
            if not v.startswith('#') or len(v) != 7:
                raise ValueError('색상은 #RRGGBB 형식이어야 합니다.')
        elif isinstance(v, list):
            for color in v:
                if not isinstance(color, str) or not color.startswith('#') or len(color) != 7:
                    raise ValueError('모든 색상은 #RRGGBB 형식이어야 합니다.')
        return v

    @field_validator('stroke_colors')
    @classmethod
    def validate_stroke_colors(cls, v: Union[str, List[str]]) -> Union[str, List[str]]:
        """테두리 색상 유효성 검증"""
        if isinstance(v, str):
            if not v.startswith('#') or len(v) != 7:
                raise ValueError('테두리 색상은 #RRGGBB 형식이어야 합니다.')
        elif isinstance(v, list):
            for color in v:
                if not isinstance(color, str) or not color.startswith('#') or len(color) != 7:
                    raise ValueError('모든 테두리 색상은 #RRGGBB 형식이어야 합니다.')
        return v

    @field_validator('background_size')
    @classmethod
    def validate_background_size(cls, v: tuple) -> tuple:
        """배경 크기 검증"""
        if len(v) != 2:
            raise ValueError('배경 크기는 (width, height) 형태의 튜플이어야 합니다.')
        width, height = v
        if not isinstance(width, int) or not isinstance(height, int):
            raise ValueError('배경 크기는 정수여야 합니다.')
        if width <= 0 or height <= 0:
            raise ValueError('배경 크기는 0보다 커야 합니다.')
        if width > 2048 or height > 2048:
            raise ValueError('배경 크기는 2048을 초과할 수 없습니다.')
        return v

    @field_validator('background_color')
    @classmethod
    def validate_background_color(cls, v: tuple) -> tuple:
        """배경 색상 검증"""
        if len(v) != 4:
            raise ValueError('배경 색상은 (R, G, B, A) 형태의 튜플이어야 합니다.')
        for component in v:
            if not isinstance(component, int) or component < 0 or component > 255:
                raise ValueError('색상 값은 0-255 범위의 정수여야 합니다.')
        return v

    @field_validator('output_format')
    @classmethod
    def validate_output_format(cls, v: str) -> str:
        """출력 포맷 검증"""
        valid_formats = ["PNG", "JPEG", "JPG", "WEBP", "BMP", "GIF", "TIFF"]
        if v.upper() not in valid_formats:
            raise ValueError(f'지원하지 않는 포맷입니다. 지원 포맷: {", ".join(valid_formats)}')
        return v.upper()

class TextImageResponse(BaseModel):
    """
    텍스트 이미지 생성 응답 모델
    
    이미지 생성 결과를 담는 응답 스키마입니다.
    성공 시 Base64 인코딩된 이미지 데이터를 포함합니다.
    """
    
    success: bool = Field(
        description="작업 성공 여부",
        example=True
    )
    
    message: str = Field(
        description="응답 메시지",
        example="이미지 생성이 완료되었습니다."
    )
    
    image_base64: Optional[str] = Field(
        default=None,
        description="Base64 인코딩된 이미지 데이터",
        example="iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    )
    
    format: Optional[str] = Field(
        default=None,
        description="생성된 이미지의 포맷",
        example="PNG"
    )

class FontListResponse(BaseModel):
    """
    사용 가능한 폰트 목록 응답 모델
    
    시스템에서 사용 가능한 모든 폰트의 목록을 반환합니다.
    """
    
    success: bool = Field(
        description="작업 성공 여부",
        example=True
    )
    
    fonts: List[str] = Field(
        description="사용 가능한 폰트 이름 목록",
        example=["본고딕_BOLD", "본고딕_REGULAR", "베이글", "쿠키런 블랙"]
    )

class ErrorResponse(BaseModel):
    """
    에러 응답 모델
    
    API 요청 처리 중 발생한 오류 정보를 담는 응답 스키마입니다.
    """
    
    success: bool = Field(
        default=False,
        description="작업 성공 여부 (항상 False)",
        example=False
    )
    
    message: str = Field(
        description="오류 메시지",
        example="폰트 파일을 찾을 수 없습니다."
    )
    
    error_code: Optional[str] = Field(
        default=None,
        description="오류 코드 (선택적)",
        example="FONT_NOT_FOUND"
    )