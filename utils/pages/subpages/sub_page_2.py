import streamlit as st
from PIL import Image
from pathlib import Path
from utils.pages.CSS import sub2_CSS

#######################################################################################################

def render_mode_and_ratio_selection(ratio_size_map):
    """생성 방식과 이미지 비율 선택 UI 렌더링"""
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("생성 방식 선택")
        st.radio(
            "선택",
            ["🎨 자연스럽게 합성하기(generate)", "🖌️ 제품 그대로 붙이기(inpaint)"],
            horizontal=True,
            key="mode",
        )
    with col2:
        st.subheader("이미지 비율")
        st.selectbox("출력 이미지 비율", list(ratio_size_map.keys()), key="ratio")

#######################################################################################################

def render_inpaint_mode(RB_image, example_bg, width, height):
    """제품 그대로 붙이기(inpaint) 모드 UI 렌더링"""
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("배경 설명 입력")
        st.text_area("배경 프롬프트 입력", placeholder="예: 햇살 가득한 나무 테라스 카페", key="prompt")
        st.subheader("제품 이미지 사용 안내")
        # st.image(RB_image, caption="1페이지의 누끼 이미지", use_container_width=False)
        st.info("이전 단계에서 전달된 제품 이미지를 기반으로 배경이 생성됩니다.")


        # 배경 준비 완료 상태 자동 설정
        st.session_state["bg_ready"] = True

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

#######################################################################################################

def render_generate_mode(example_bg, width, height):
    """자연스럽게 합성하기(generate) 모드 UI 렌더링"""
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

#######################################################################################################

def render_navigation_buttons():
    """이전 / 다음 단계 이동 버튼 렌더링"""
    _, col_btns, _ = st.columns([1, 1, 1])
    with col_btns:
        prev_col, next_col = st.columns(2)
        with prev_col:
            if st.button("⬅ 이전"):
                st.session_state["step"] = 1
                st.session_state["bg_ready"] = False
                st.rerun()
        with next_col:
            if st.button("➡ 다음"):
                st.session_state["step"] = 3
                st.session_state["bg_ready"] = False
                st.rerun()

#######################################################################################################
# --- 메인 렌더 함수 ---

def render(platform):
    # 초기 세션 상태 설정
    st.session_state.setdefault("step", 2)
    st.session_state.setdefault("bg_ready", False)
    st.session_state.setdefault("image_cache", {})

    # 이미지 비율 별 크기 매핑
    ratio_size_map = {
        "🖼️ 가로형 (4:3)": (720, 512),
        "📱 세로형 (3:4)": (512, 720),
        "📐 정사각형 (1:1)": (512, 512),
    }

    # 이미지 경로
    img_path = Path(__file__).parent.parent / "images"
    RB_image = str(img_path / "composed.png")
    example_bg = str(img_path / "combine.png")

    # 스타일 적용
    st.markdown(sub2_CSS, unsafe_allow_html=True)

    st.title("2️⃣ 배경 이미지 생성")
    st.markdown("---")

    # UI 렌더링: 생성 방식 및 비율 선택
    render_mode_and_ratio_selection(ratio_size_map)

    st.markdown("---")

    # 선택된 모드 및 비율
    mode = st.session_state["mode"]
    ratio = st.session_state["ratio"]
    width, height = ratio_size_map[ratio]

    # 모드별 UI 분기
    if mode == "🖌️ 제품 그대로 붙이기(inpaint)":
        render_inpaint_mode(RB_image, example_bg, width, height)
    else:  # "🎨 자연스럽게 합성하기(generate)" 모드
        render_generate_mode(example_bg, width, height)

    st.markdown("---")

    # 이전 / 다음 버튼
    render_navigation_buttons()
