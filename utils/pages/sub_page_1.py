import streamlit as st
from PIL import Image
from pathlib import Path
from io import BytesIO
from streamlit_drawable_canvas import st_canvas


# 세션 상태 초기화
def init_session_state():
    defaults = {
        "page": "sub_page_1",
        "uploaded_image": None,
        "ai_generated": False,
        "current_mode": "직접 업로드",
        "image_scale": 10,
        "image_x": 200,
        "image_y": 200
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# 이미지 크기 조절 및 위치 지정
def resize_and_position_image(image, scale, x_offset, y_offset, canvas_width, canvas_height):
    original_width, original_height = image.size
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)

    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    canvas_image = Image.new('RGBA', (canvas_width, canvas_height), (255, 255, 255, 0))

    center_x, center_y = canvas_width // 2, canvas_height // 2
    paste_x = center_x - new_width // 2 + x_offset
    paste_y = center_y - new_height // 2 + y_offset

    if resized_image.mode == 'RGBA':
        canvas_image.paste(resized_image, (paste_x, paste_y), resized_image)
    else:
        canvas_image.paste(resized_image, (paste_x, paste_y))

    return canvas_image


# 스타일 적용
def apply_styles():
    st.markdown("""
        <style>
        .container-box {
            background-color: #F4F6FA;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            margin-bottom: 20px;
            min-height: 500px;
        }
        .stSlider label { color: #262730 !important; }
        .stSlider > div > div > div > div > div > div { color: #262730 !important; }
        </style>
    """, unsafe_allow_html=True)


# 모드 전환 처리
def handle_mode_change(mode):
    if mode != st.session_state["current_mode"]:
        st.session_state.update({
            "current_mode": mode,
            "uploaded_image": None,
            "ai_generated": False,
            "image_scale": 10,
            "image_x": 200,
            "image_y": 200
        })


# 입력 영역 UI
def render_input_section(mode, raw_product):
    st.subheader("입력 이미지")

    if mode == "직접 업로드":
        uploaded_file = st.file_uploader("제품 이미지를 업로드하세요", type=["png"])
        if uploaded_file:
            st.session_state["uploaded_image"] = uploaded_file
            st.session_state["ai_generated"] = False
    else:
        btn_text = "✨ 제품 이미지 생성 (예시)" if not st.session_state["ai_generated"] else "🔄 다시 생성"
        if st.button(btn_text, key="generate_btn"):
            st.session_state["ai_generated"] = True
            st.session_state["uploaded_image"] = None
            st.session_state.update({"image_scale": 10, "image_x": 200, "image_y": 200})
            st.rerun()

    # 시각화
    if st.session_state["uploaded_image"]:
        st.image(st.session_state["uploaded_image"], caption="업로드한 이미지", use_container_width=True)
    elif st.session_state["ai_generated"]:
        st.image(raw_product, caption="AI 생성 이미지 예시", use_container_width=True)


# 캔버스 영역 UI
def render_canvas_section(rb_product):
    st.subheader("누끼 이미지 조정")

    if not (st.session_state["uploaded_image"] or st.session_state["ai_generated"]):
        st.info("이미지를 먼저 업로드하거나 생성해주세요.")
        return

    st.markdown("**이미지 조작 설정**")
    sliders = [
        ("크기 조정", "image_scale", 0, 20, 1),
        ("X 위치", "image_x", 0, 400, 10),
        ("Y 위치", "image_y", 0, 400, 10)
    ]
    for label, key, min_val, max_val, step in sliders:
        st.session_state[key] = st.slider(
            label, min_val, max_val, int(st.session_state[key]), step, key=f"{key}_slider"
        )

    st.markdown("---")

    canvas_width = canvas_height = 512
    try:
        original_img = Image.open(rb_product).convert("RGBA")
        processed_img = resize_and_position_image(
            original_img,
            st.session_state["image_scale"] / 10,
            st.session_state["image_x"] - 200,
            st.session_state["image_y"] - 200,
            canvas_width,
            canvas_height
        )

        st.markdown("**캔버스 미리보기**")
        _ = st_canvas(
            fill_color="rgba(255, 255, 255, 0.0)",
            stroke_width=1,
            stroke_color="#000000",
            background_color="#FFFFFF",
            background_image=processed_img,
            update_streamlit=True,
            height=canvas_height,
            width=canvas_width,
            drawing_mode="transform",
            key=f"canvas_{st.session_state['image_scale']}_{st.session_state['image_x']}_{st.session_state['image_y']}",
        )

        # 저장하기 버튼
        if st.button("💾 이미지 저장하기"):
            # 저장 경로 생성
            images_dir = Path(__file__).parent.parent / "images"
            images_dir.mkdir(parents=True, exist_ok=True)

            file_name = "composed.png"
            save_path = images_dir / file_name

            processed_img.save(save_path)
            st.success(f"✅ 이미지가 저장되었습니다: `{save_path}`")

            # 브라우저 다운로드도 제공
            img_bytes = BytesIO()
            processed_img.save(img_bytes, format="PNG")
            img_bytes.seek(0)

            st.download_button(
                label="📥 브라우저로 다운로드",
                data=img_bytes,
                file_name=file_name,
                mime="image/png"
            )

    except Exception as e:
        st.error(f"누끼 이미지를 처리하는 중 오류 발생: {str(e)}")


# 메인 렌더링
def render():
    init_session_state()
    apply_styles()

    img_path = Path(__file__).parent.parent / "images"
    raw_product = str(img_path / "ex_raccoon_raw.png")
    rb_product = str(img_path / "ex_raccoon_RB.png")

    st.title("1️⃣ 제품 이미지 선택 및 위치 조정")
    st.markdown("## ")

    st.subheader("제품 이미지 선택")
    mode = st.radio(" ", ["직접 업로드", "AI 생성"], horizontal=True)
    handle_mode_change(mode)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        render_input_section(mode, raw_product)
    with col2:
        render_canvas_section(rb_product)

    st.markdown("---")
    _, col_btns, _ = st.columns([1, 1, 1])
    with col_btns:
        prev_col, next_col = st.columns(2)
        with prev_col:
            st.button("⬅ 이전", disabled=True)
        with next_col:
            if st.button("➡ 다음"):
                st.session_state["page"] = "sub_page_2"
                st.rerun()