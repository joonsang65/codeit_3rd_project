import asyncio
from models import OpenAIClient

async def generate_ad_texts(
    ad_type: str,
    mode_input: str = None,  # "1" or "2" or None (poster는 None)
    product_name: str = "",
    product_use: str = "",
    brand_name: str = "",
    extra_info: str = None
):
    """
    광고 문구 생성 요청 함수 (FastAPI 연동용)

    Args:
        ad_type (str): 광고 유형 ("인스타그램", "블로그", "포스터")
        mode_input (str or None): 모드 선택 ("1", "2"), poster는 None
        product_name (str): 상품 이름
        product_use (str): 상품 용도
        brand_name (str): 브랜드명
        extra_info (str or None): 추가 정보

    Returns:
        dict: 플랫폼별 온도별 광고 문구 생성 결과
    """
    openai_client = OpenAIClient()

    # 모드 결정
    if ad_type in ["인스타그램", "블로그"]:
        if mode_input not in ["1", "2"]:
            raise ValueError("인스타그램 또는 블로그 광고는 mode_input을 '1' 또는 '2'로 지정해야 합니다.")
        mode = "광고 문구만 생성" if mode_input == "1" else "광고 문구 + 텍스트 이미지용 문구 생성"
    else:
        mode = "광고 문구만 생성"

    platforms = [ad_type]

    results = await openai_client.generate_multiple_responses(
        platforms,
        product_name,
        product_use,
        brand_name,
        extra_info,
        mode
    )

    return results
