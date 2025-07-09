import streamlit as st
from PIL import Image
from pathlib import Path
from io import BytesIO
from datetime import datetime


def overlay_text_image(base_img, text_img, scale, x_offset, y_offset):
    """텍스트 이미지를 리사이즈하고, 위치에 맞춰 오버레이"""
    base = base_img.copy()
    text_resized = text_img.resize(
        (int(text_img.width * scale), int(text_img.height * scale)),
        Image.Resampling.LANCZOS
    )
    paste_x = base.width // 2 - text_resized.width // 2 + x_offset - 200
    paste_y = base.height // 2 - text_resized.height // 2 + y_offset - 200
    base.paste(text_resized, (paste_x, paste_y), text_resized)
    return base


def render():
    st.session_state.setdefault("page", "sub_page_4")

    # 경로 설정
    img_path = Path(__file__).parent.parent / "images"
    base_img_path = img_path / "combine.png"
    text_img_path = img_path / "output.png"

    if not base_img_path.exists() or not text_img_path.exists():
        st.error("❌ 이미지 파일이 존재하지 않습니다.")
        return

    base_img = Image.open(base_img_path).convert("RGBA")
    text_img = Image.open(text_img_path).convert("RGBA")

    st.title("4️⃣ 텍스트 이미지 추가")
    st.markdown("---")

    # 슬라이더 값 초기화
    st.session_state.setdefault("text_scale", 50)
    st.session_state.setdefault("text_x", 50)
    st.session_state.setdefault("text_y", 50)

    # 좌우 2단 UI
    col1, col2 = st.columns([3, 2])

    with col2:
        st.markdown("### 🎛️ 텍스트 조정")

        scale_ui = st.slider("크기 조정", 0, 100, key="text_scale")
        x_pos_ui = st.slider("좌 / 우", 0, 100, key="text_x")
        y_pos_ui = st.slider("상 / 하", 0, 100, key="text_y")

        # UI → 실제 값 매핑
        scale = scale_ui / 250
        x_pos = x_pos_ui * 4 
        y_pos = y_pos_ui * 4

        # 저장 및 다운로드
        if st.button("💾 최종 이미지 저장하기"):
            composed = overlay_text_image(base_img, text_img, scale, x_pos, y_pos)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"final_composed_{timestamp}.png"
            save_path = img_path / filename
            composed.save(save_path)
            st.success(f"✅ 최종 이미지가 저장되었습니다: `{filename}`")

            img_bytes = BytesIO()
            composed.save(img_bytes, format="PNG")
            img_bytes.seek(0)

            st.download_button(
                label="📥 이미지 다운로드",
                data=img_bytes,
                file_name=filename,
                mime="image/png"
            )

    with col1:
        composed = overlay_text_image(base_img, text_img, scale, x_pos, y_pos)
        st.markdown("### 🖼️ 최종 미리보기")
        st.image(composed, caption="텍스트가 합성된 미리보기", use_container_width=True)

    # 페이지 이동 버튼
    st.markdown("---")
    prev_col, next_col = st.columns(2)
    with prev_col:
        if st.button("⬅ 이전"):
            st.session_state["page"] = "sub_page_3"
            st.rerun()
    with next_col:
        if st.button("➡ 다음"):
            st.session_state["page"] = "sub_page_5"
            st.rerun()
