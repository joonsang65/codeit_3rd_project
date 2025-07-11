import streamlit as st
from PIL import Image
from pathlib import Path
from io import BytesIO
from streamlit_drawable_canvas import st_canvas
from utils.pages.CSS import sub1_CSS

#######################################################################################################
# 세션 상태 초기화
def init_session_state():
    """
    세션 상태에 필요한 기본 변수들 초기화.
    """
    defaults = {
        "step": 1,
        "uploaded_image": None,
        "ai_generated": False,
        "current_mode": "직접 업로드",
        "image_scale": 10,
        "image_x": 200,
        "image_y": 200,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

#######################################################################################################
# 이미지 크기 조절 및 위치 지정
def resize_and_position_image(image, scale, x_offset, y_offset, canvas_width, canvas_height):
    """
    이미지 원본을 주어진 scale로 크기 조정 후,
    캔버스 내에서 x_offset, y_offset 만큼 위치를 조정하여
    투명 배경 캔버스에 붙여넣은 새로운 이미지를 반환.
    """
    original_width, original_height = image.size
    new_width = int(original_width * scale)
    new_height = int(original_height * scale)

    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    canvas_image = Image.new("RGBA", (canvas_width, canvas_height), (255, 255, 255, 0))

    center_x, center_y = canvas_width // 2, canvas_height // 2
    paste_x = center_x - new_width // 2 + x_offset
    paste_y = center_y - new_height // 2 + y_offset

    if resized_image.mode == "RGBA":
        canvas_image.paste(resized_image, (paste_x, paste_y), resized_image)
    else:
        canvas_image.paste(resized_image, (paste_x, paste_y))

    return canvas_image

#######################################################################################################
# 모드 전환 처리
def handle_mode_change(mode):
    """
    직접 업로드 / AI 생성 모드가 바뀔 때마다
    관련 세션 상태 변수 초기화.
    """
    if mode != st.session_state["current_mode"]:
        st.session_state.update({
            "current_mode": mode,
            "uploaded_image": None,
            "ai_generated": False,
            "image_scale": 10,
            "image_x": 200,
            "image_y": 200,
        })

#######################################################################################################
# 입력 이미지 섹션 렌더링
def render_input_section(mode, raw_product):
    """
    mode에 따라 파일 업로드 위젯 또는 AI 생성 버튼을 보여주고,
    이미지가 있으면 화면에 출력.
    """
    st.subheader("입력 이미지")

    if mode == "직접 업로드":
        uploaded_file = st.file_uploader("제품 이미지를 업로드하세요 (PNG 형식)", type=["png"])
        if uploaded_file:
            st.session_state["uploaded_image"] = uploaded_file
            st.session_state["ai_generated"] = False
    else:  # AI 생성 모드
        btn_text = "✨ 제품 이미지 생성 (예시)" if not st.session_state["ai_generated"] else "🔄 다시 생성"
        if st.button(btn_text, key="generate_btn"):
            st.session_state["ai_generated"] = True
            st.session_state["uploaded_image"] = None
            st.session_state.update({"image_scale": 10, "image_x": 200, "image_y": 200})
            st.rerun()

    # 이미지 출력
    if st.session_state["uploaded_image"]:
        st.image(st.session_state["uploaded_image"], caption="업로드한 이미지", use_container_width=True)
    elif st.session_state["ai_generated"]:
        st.image(raw_product, caption="AI 생성 이미지 예시", use_container_width=True)

#######################################################################################################
# 캔버스 섹션 렌더링
def render_canvas_section(rb_product):
    """
    이미지 누끼 조정을 위한 캔버스 영역 출력.
    이미지가 없으면 안내 메시지 표시.
    먼저 미리보기 이미지를 출력하고,
    이후 슬라이더 조작 UI 및 저장 기능 제공.
    슬라이더 변경사항은 세션 상태에 즉시 반영.
    """
    st.subheader("누끼 이미지 조정")

    if not (st.session_state["uploaded_image"] or st.session_state["ai_generated"]):
        st.info("이미지를 먼저 업로드하거나 생성해주세요.")
        return

    canvas_width = canvas_height = 512

    try:
        # 🔧 슬라이더 조작값 실시간 반영
        st.markdown("**이미지 조작 설정**")

        image_scale = st.slider("크기 조정", 0, 20, st.session_state["image_scale"], step=1)
        image_x = st.slider("X 위치", 0, 400, st.session_state["image_x"], step=10)
        image_y = st.slider("Y 위치", 0, 400, st.session_state["image_y"], step=10)

        st.session_state["image_scale"] = image_scale
        st.session_state["image_x"] = image_x
        st.session_state["image_y"] = image_y

        st.markdown("---")

        # 🖼️ 미리보기 이미지 생성
        original_img = Image.open(rb_product).convert("RGBA")
        processed_img = resize_and_position_image(
            original_img,
            image_scale / 10,
            image_x - 200,
            image_y - 200,
            canvas_width,
            canvas_height,
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
            key=f"canvas_{image_scale}_{image_x}_{image_y}",
        )

        # 💾 이미지 저장 기능
        st.markdown("---")
        if st.button("💾 이미지 저장하기"):
            images_dir = Path(__file__).parent.parent / "images"
            images_dir.mkdir(parents=True, exist_ok=True)

            file_name = "composed.png"
            save_path = images_dir / file_name
            processed_img.save(save_path)
            st.success(f"✅ 이미지가 저장되었습니다: `{save_path}`")

            # 브라우저 다운로드 제공
            img_bytes = BytesIO()
            processed_img.save(img_bytes, format="PNG")
            img_bytes.seek(0)

            st.download_button(
                label="📥 브라우저로 다운로드",
                data=img_bytes,
                file_name=file_name,
                mime="image/png",
            )

    except Exception as e:
        st.error(f"누끼 이미지를 처리하는 중 오류 발생: {str(e)}")



#######################################################################################################
# 메인 렌더 함수
def render(platform):
    """
    페이지 메인 렌더링 함수.
    세션 상태 초기화 및 스타일 적용 후,
    좌측에 입력 이미지 선택/생성 UI,
    우측에 누끼 이미지 조정 캔버스 UI 출력.
    """
    init_session_state()
    st.markdown(sub1_CSS, unsafe_allow_html=True)

    img_path = Path(__file__).parent.parent.parent / "images"
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
                st.session_state["step"] = 2
                st.rerun()

