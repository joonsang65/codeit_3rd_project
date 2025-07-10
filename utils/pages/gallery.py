import streamlit as st
import base64
from pathlib import Path
from utils.pages.CSS import gallery_base_CSS

### -------------------------------------------------------------------------------------------
### 📦 유틸 함수: 이미지 목록을 base64로 인코딩
def encode_images_to_base64(image_dir: Path):
    """
    지정한 디렉토리 내 PNG 이미지를 base64로 인코딩하여 리스트로 반환.
    """
    image_files = sorted(image_dir.glob("*.png"))
    encoded_imgs = []

    for path in image_files:
        with open(path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            encoded_imgs.append(f"data:image/png;base64,{b64}")

    return encoded_imgs

### -------------------------------------------------------------------------------------------
### 🎞️ 슬라이더용 HTML/CSS 생성 함수
def generate_slider_html(images, animation_name, duration):
    """
    이미지 리스트를 기반으로 슬라이더 HTML 문자열 생성
    """
    # 공통 CSS 정의
    base_css = gallery_base_CSS(animation_name, duration)

    # 무한 슬라이딩 효과를 위해 이미지 2배 복제
    image_tags = "".join([f'<img src="{img}"/>' for img in images * 2])

    html = base_css + f"""
    <div class="slider">
        <div class="slide-track">
            {image_tags}
        </div>
    </div>
    """
    return html

### -------------------------------------------------------------------------------------------
### 🖼️ 슬라이딩 갤러리 메인 렌더 함수
def render():
    """
    슬라이딩 갤러리 페이지 렌더링 함수
    - utils/images 폴더 내 PNG 이미지들을 3줄 슬라이더 형태로 보여줌
    - 각 줄은 좌우 방향과 속도가 다르게 애니메이션 처리됨
    """
    st.title("🎞️ 슬라이딩 갤러리")

    # 이미지 경로 설정
    image_dir = Path(__file__).parent.parent / "images"
    encoded_imgs = encode_images_to_base64(image_dir)

    if not encoded_imgs:
        st.warning("이미지가 없습니다.")
        return

    # 이미지 3줄로 균등 분할
    chunks = [encoded_imgs[i::3] for i in range(3)]

    # 각 줄의 애니메이션 방향 및 속도 정의
    directions = ["scroll-left", "scroll-right", "scroll-left"]
    durations = [50, 60, 70]

    for i in range(3):
        html = generate_slider_html(chunks[i], directions[i], durations[i])
        st.components.v1.html(html, height=180)
