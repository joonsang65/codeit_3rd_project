import streamlit as st
from PIL import Image
import base64
from io import BytesIO

# 이미지 resize 후 base64 변환
def get_base64_resized_image(image_path, height=240):
    '''
    이미지 경로를 받아 크기를 조정하는 역할
    '''
    img = Image.open(image_path)
    aspect_ratio = img.width / img.height
    resized_img = img.resize((int(height * aspect_ratio), height))
    buffer = BytesIO()
    resized_img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


# 카드 렌더링 - 전체 카드가 <a>로 감싸짐
def render_clickable_card(col, title, image_path, caption, page_route, icon, bg_color):
    '''
    Streamlit에서 "클릭 가능한 카드 UI"를 HTML 마크업으로 만들어서, 각 광고 항목을 하나의 카드처럼 보이게 하며, 클릭 시 지정한 페이지로 이동하게 하는 역할
    '''
    with col:
        img_data_url = get_base64_resized_image(image_path)

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
                a.card-link {{
                    text-decoration: none;
                }}
            </style>

            <a href="/{page_route}" class="card-link">
                <div class="clickable-card" style="background-color: {bg_color};">
                    <h4>{icon} {title}</h4>
                    <img src="{img_data_url}" alt="{caption}" />
                    <p>{caption}</p>
                </div>
            </a>
            """,
            unsafe_allow_html=True
        )


# 페이지 설정
st.set_page_config(page_title="AI 광고 제작 앱", layout="wide")
st.title("📢 생성형 AI 광고 제작 앱")
st.markdown("### 광고 용도에 맞는 예시를 보고 원하는 형식의 광고를 만들어보세요!")

# 3열 카드 배치
col1, col2, col3 = st.columns(3)

render_clickable_card(
    col1,
    "블로그 광고",
    "src/image/blog_ad.png",
    "예시: 블로그 광고 이미지",
    "generate_blog_ad",  # 경로에서 'pages/' 제거하고 확장자 제거
    "📝",
    "#FFF9E6"
)

render_clickable_card(
    col2,
    "인스타그램 광고",
    "src/image/instagram_ad.png",
    "예시: 인스타그램 광고 이미지",
    "generate_instagram_ad",
    "📸",
    "#F3F0FF"
)

render_clickable_card(
    col3,
    "포스터 광고",
    "src/image/poster_ad.png",
    "예시: 포스터 광고 이미지",
    "generate_poster_ad",
    "🖼️",
    "#E6FFF9"
)
