# /ad_project/utils/schema.py.
from pydantic import BaseModel
from typing import Literal, Annotated

# ********************************* 이미지 생성 입력 형식 *********************************
class AdvertisementGenerationRequest(BaseModel):
    """광고 생성 요청 모델."""
    korean_prompt: Annotated[str, "한국어 프롬프트 문자열."]
    image_size: Annotated[str, "생성할 이미지 크기 (예: 'INSTAGRAM', 'POSTER')."] = "INSTAGRAM"
    num_images: Annotated[int, "생성할 이미지 수. 기본값은 1."] = 1

# ********************************* 이미지 보전 입력 형식  *********************************
class ImagePreservationRequest(BaseModel):
    """이미지 보전 요청 모델."""
    mode: Literal["inpaint", "text2img"] = "inpaint"
    product_type: Literal["food", "cosmetics", "furniture"] = "cosmetics"
    canvas_size: tuple[int, int] = (512, 512)
    desired_size: tuple[int, int] = (128, 128)

# ********************************* 광고 문구 텍스트 생성 입력 형식 *********************************
class AdCopyGenerationRequest(BaseModel):
    """광고 문구 텍스트 생성 요청 모델."""
    ad_type: Literal["instagram", "blog", "poster"] = "instagram"
    user_prompt: Annotated[str, "사용자 입력 프롬프트 문자열. 🎯 생성할 광고와 제품에 대해 설명해 주길 바랍니다. 요구사항이 자세할수록 좋은 결과를 얻을 수 있습니다."]