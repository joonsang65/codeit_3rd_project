## ref :https://github.com/joonsang65/codeit_3rd_project/blob/frontend/streamlit/app.py

import streamlit as st
from PIL import Image
import base64
from io import BytesIO
from pathlib import Path
from utils.pages.CSS import home_card_CSS
### ------------------------------------------------------------------------------------------------
### 📦 유틸 함수: 이미지 base64 인코딩
def get_base64_resized_image(image_path, height=240):
    """
    특정 경로의 이미지를 열어 주어진 높이로 리사이즈한 뒤,
    PNG 형식으로 인코딩하고 base64 문자열로 변환하여 반환.

    Args:
        image_path (str | Path): 이미지 경로
        height (int): 리사이즈할 높이(px)

    Returns:
        str: HTML img 태그에서 사용할 base64 이미지 URI
    """
    img = Image.open(image_path)
    aspect_ratio = img.width / img.height
    resized_img = img.resize((int(height * aspect_ratio), height))
    
    buffer = BytesIO()
    resized_img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/png;base64,{img_str}"

### ------------------------------------------------------------------------------------------------
### 🃏 카드 UI 렌더링 함수
def render_clickable_card(col, title, image_path, caption, icon, bg_color):
    """
    Streamlit 컬럼(col)에 하나의 카드 형태 UI를 렌더링.
    내부적으로 이미지 base64 변환 후 HTML 마크업 삽입.
    
    Args:
        col (streamlit.delta_generator.DeltaGenerator): 사용할 컬럼 객체
        title (str): 카드 상단 제목
        image_path (str | Path): 이미지 파일 경로
        caption (str): 이미지 설명
        icon (str): 제목 왼쪽에 붙일 이모지
        bg_color (str): 카드 배경 색상 (HEX 코드)
    """
    with col:
        img_data_url = get_base64_resized_image(image_path)

        # 카드 CSS 정의 (한 번만 선언되도록 위치 분리 가능)
        st.markdown(home_card_CSS, unsafe_allow_html=True)

        # 카드 콘텐츠 삽입
        st.markdown(
            f"""
            <div class="clickable-card" style="background-color: {bg_color};">
                <h4>{icon} {title}</h4>
                <img src="{img_data_url}" alt="{caption}" />
                <p>{caption}</p>
                <p style="color:#4A8CF1; font-weight:bold; cursor:pointer;">
                    사이드 바의 광고 생성 페이지로 이동해서
                </p>
                <p style="color:#4A8CF1; font-weight:bold; cursor:pointer;">
                    [사용자]님 만의 광고를 만들어보세요 !
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

### ------------------------------------------------------------------------------------------------
### 🏠 홈 화면 렌더 함수
def render():
    """
    Streamlit 홈 페이지 렌더링 함수.
    - 광고 예시(블로그, 인스타, 포스터)를 카드 형태로 3열 구성
    - 사이드바에서 이어지는 생성 플로우 안내
    """
    st.session_state.setdefault("page", "home")
    st.title("📢 생성형 AI 광고 제작 앱")
    st.markdown("### 광고 용도에 맞는 예시를 보고 원하는 형식의 광고를 만들어보세요!")

    ### 이미지 경로 세팅
    base_dir = Path(__file__).parent.parent / "images"

    ### 카드 3열 구성
    col1, col2, col3 = st.columns(3)

    render_clickable_card(
        col1,
        "블로그 광고",
        base_dir / "blog_ad.png",
        "예시: 블로그 광고 이미지",
        "📝",
        "#FFF9E6"
    )
    render_clickable_card(
        col2,
        "인스타그램 광고",
        base_dir / "instagram_ad.png",
        "예시: 인스타그램 광고 이미지",
        "📸",
        "#F3F0FF"
    )
    render_clickable_card(
        col3,
        "포스터 광고",
        base_dir / "poster_ad.png",
        "예시: 포스터 광고 이미지",
        "🖼️",
        "#E6FFF9"
    )
