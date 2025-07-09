import streamlit as st
from PIL import Image
import base64
from io import BytesIO
from pathlib import Path

# 이미지 resize 후 base64 변환
def get_base64_resized_image(image_path, height=240):
    '''
    이미지 경로를 받아 크기를 조정하고 base64로 변환
    '''
    img = Image.open(image_path)
    aspect_ratio = img.width / img.height
    resized_img = img.resize((int(height * aspect_ratio), height))
    buffer = BytesIO()
    resized_img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


# 카드 렌더링 (Streamlit 내부 페이지 전환 방식 적용)
def render_clickable_card(col, title, image_path, caption, icon, bg_color):
    '''
    클릭 가능한 카드 UI 생성 및 세션 상태 기반 페이지 전환
    '''
    with col:
        img_data_url = get_base64_resized_image(image_path)

        # 카드 UI 스타일
        st.markdown(
            f"""
            <style>
                .clickable-card {{
                    border: 1px solid #ddd;
                    border-radius: 12px;
                    padding: 16px;
                    text-align: center;
                    box-shadow: 2px 2px 12px rgba(0,0,0,0.05);
                    margin-bottom: 20px;
                    transition: transform 0.2s ease-in-out;
                }}
                .clickable-card:hover {{
                    transform: scale(1.02);
                    box-shadow: 4px 4px 20px rgba(0,0,0,0.1);
                }}
                .clickable-card img {{
                    max-width: 100%;
                    height: auto;
                    object-fit: contain;
                    border-radius: 8px;
                    margin-bottom: 8px;
                }}
                .clickable-card h4 {{
                    margin-bottom: 12px;
                    color: #222;
                }}
                .clickable-card p {{
                    color: #555;
                    font-size: 14px;
                }}
            </style>
            """,
            unsafe_allow_html=True
        )

        # 실제 카드 구조
        with st.container():
            st.markdown(
                f"""
                <div class="clickable-card" style="background-color: {bg_color};">
                    <h4>{icon} {title}</h4>
                    <img src="{img_data_url}" alt="{caption}" />
                    <p>{caption}</p>
                </div>
                """,
                unsafe_allow_html=True
            )
            # 클릭 시 페이지 전환 (수정된 부분)
            if st.button(f"👉 {title} 생성 시작하기", key=title):
                st.session_state["page"] = "generate_ad"  # 페이지 변경
                st.session_state["step"] = 1              # step 초기화
                st.rerun()


# ✅ 홈 페이지 렌더 함수
def render():
    st.session_state.setdefault("page", "home")
    st.title("📢 생성형 AI 광고 제작 앱")
    st.markdown("### 광고 용도에 맞는 예시를 보고 원하는 형식의 광고를 만들어보세요!")

    # 이미지 경로 설정 (utils/images 안의 이미지 사용)
    base_dir = Path(__file__).parent.parent / "images"

    # 3열 카드 배치
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
