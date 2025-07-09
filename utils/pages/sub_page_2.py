import streamlit as st
from PIL import Image
from pathlib import Path

def render():
    st.session_state.setdefault("page", "sub_page_2")
    st.session_state.setdefault("bg_ready", False)
    st.session_state.setdefault("image_cache", {})

    ratio_size_map = {
        "🖼️ 가로형 (4:3)": (720, 512),
        "📱 세로형 (3:4)": (512, 720),
        "📐 정사각형 (1:1)": (512, 512)
    }

    img_path = Path(__file__).parent.parent / "images"
    RB_image = str(img_path / "composed.png")
    example_bg = str(img_path / "combine.png")

    st.markdown("""
        <style>
        .box-style {
            background-color: #f9f9f9;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 0 8px rgba(0, 0, 0, 0.05);
            height: 100%;
        }
        .center-button {
            display: flex;
            justify-content: center;
            margin-top: 10px;
        }
        .full-height-textarea textarea {
            min-height: 330px !important;
        }
        </style>
    """, unsafe_allow_html=True)

    st.title("2️⃣ 배경 이미지 생성")
    st.markdown("---")

    # 생성 방식 및 비율 선택
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("생성 방식 선택")
        st.radio("선택", ["🎨 자연스럽게 합성하기(generate)", "🖌️ 제품 그대로 붙이기(inpaint)"], horizontal=True, key="mode")
    with col2:
        st.subheader("이미지 비율")
        st.selectbox("출력 이미지 비율", list(ratio_size_map.keys()), key="ratio")

    st.markdown("---")

    mode = st.session_state["mode"]
    ratio = st.session_state["ratio"]
    width, height = ratio_size_map[ratio]

    if mode == "🖌️ 제품 그대로 붙이기(inpaint)":
        # 제품 이미지 이미 session_state로 전달되었다고 가정
        col3, col4 = st.columns(2)
        with col3:

            st.subheader("제품 이미지 사용 안내")
            st.image(RB_image, caption="1페이지의 누끼 이미지", use_container_width=False)
            st.info("이전 단계에서 전달된 제품 이미지를 기반으로 배경이 생성됩니다.")
            st.subheader("배경 설명 입력")
            st.text_area("배경 프롬프트 입력", placeholder="예: 햇살 가득한 나무 테라스 카페", key="prompt")
            st.session_state["bg_ready"] = True  # 자동으로 ready로 전환

        with col4:
            st.subheader("배경 미리보기")
            if st.session_state["bg_ready"]:
                img = Image.open(example_bg).resize((width, height))
                st.image(img, caption="🎨 smoothing 미적용", use_container_width=False)
                if st.button("🔄 다시 생성"):
                    st.session_state["bg_ready"] = False
                    st.rerun()
            else:
                st.info("제품 이미지가 준비되지 않았습니다.")

    elif mode == "🎨 자연스럽게 합성하기(generate)":
        col5, col6 = st.columns(2)
        with col5:
            st.subheader("배경 설명 입력")
            st.text_area("배경 프롬프트 입력", placeholder="예: 햇살 가득한 나무 테라스 카페", key="prompt")
            st.file_uploader("참고 이미지 업로드 (선택)", type=["png", "jpg"], key="ref_image")

            if st.button("✅ 작성 완료"):
                if st.session_state["prompt"].strip():
                    st.session_state["bg_ready"] = True
                else:
                    st.warning("프롬프트를 입력하세요.")

        with col6:
            st.subheader("배경 미리보기")
            if st.session_state["bg_ready"]:
                img = Image.open(example_bg).resize((width, height))
                st.image(img, caption="🎨 smoothing 적용", use_container_width=False)
                if st.button("🔄 다시 생성"):
                    st.session_state["bg_ready"] = False
                    st.rerun()
            else:
                st.info("왼쪽 정보를 입력 후 '작성 완료'를 눌러야 미리보기가 표시됩니다.")

    st.markdown("---")

    # 이전 / 다음 버튼
    _, col_btns, _ = st.columns([1, 1, 1])
    with col_btns:
        prev_col, next_col = st.columns(2)
        with prev_col:
            if st.button("⬅ 이전"):
                st.session_state["page"] = "sub_page_1"
                st.session_state["bg_ready"] = False
                st.rerun()
        with next_col:
            if st.button("➡ 다음"):
                st.session_state["page"] = "sub_page_3"
                st.session_state["bg_ready"] = False
                st.rerun()
