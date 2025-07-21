# backend/app/routers/TI.py
from fastapi import APIRouter, HTTPException, status
from services.TI_modules.TI_schemas import TextImageRequest, TextImageResponse, FontListResponse
from services.TI_modules.TI_models import text_image_service

router = APIRouter()

@router.get("/fonts", response_model=FontListResponse)
async def get_available_fonts():
    """사용 가능한 폰트 목록을 반환합니다."""
    try:
        fonts = text_image_service.get_available_fonts()
        return FontListResponse(success=True, fonts=fonts)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"폰트 목록을 가져오는 중 오류 발생: {str(e)}"
        )

@router.post("/generate", response_model=TextImageResponse)
async def generate_text_image(request: TextImageRequest):
    """텍스트 이미지를 생성합니다."""
    try:
       
        # 텍스트 검증
        if not request.text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="텍스트는 비어있을 수 없습니다."
            )
        
        # 단어별 색상 검증
        if request.word_based_colors:
            words = request.text.split()
            if isinstance(request.text_colors, list) and len(request.text_colors) != len(words):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="단어별 색상 모드에서는 테두리 색상 개수가 단어 개수와 일치해야 합니다."
                )
        
        # 이미지 생성
        image_base64, format_name, error_message = text_image_service.generate_text_image(
            text=request.text,
            font_name=request.font_name,
            font_size=request.font_size,
            text_colors=request.text_colors,
            stroke_colors=request.stroke_colors,
            stroke_width=request.stroke_width,
            word_based_colors=request.word_based_colors,
            background_size=request.background_size,
            background_color=request.background_color,
            output_format=request.output_format
        )
        
        if error_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )
        
        return TextImageResponse(
            success=True,
            message="이미지 생성이 완료되었습니다.",
            image_base64=image_base64,
            format=format_name
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"서버 오류가 발생했습니다: {str(e)}"
        )