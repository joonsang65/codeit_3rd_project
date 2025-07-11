import streamlit as st
from pathlib import Path
from PIL import Image
from io import BytesIO
from utils.fonts import FONTS
from utils.pages.CSS import sub3_CSS

#######################################################################################################
# --- 세션 상태 초기화 ---

def init_session_state():
    """
    세션 상태 변수 초기화
    이미 값이 설정되어 있다면 변경하지 않고, 없는 경우 기본값을 설정
    """
    st.session_state.setdefault("step", 3)
    st.session_state.setdefault("ad_text", "")
    st.session_state.setdefault("product_name", "")
    st.session_state.setdefault("product_usage", "")
    st.session_state.setdefault("brand_name", "")
    st.session_state.setdefault("text_prompt", "")
    st.session_state.setdefault("show_result", False)

#######################################################################################################
# --- 상품 정보 입력 폼 렌더링 ---

def render_product_info_form():
    """
    상품 이름, 용도, 브랜드명 및 추가 정보를 입력받는 폼을 렌더링함
    입력값이 충분하면 광고 문구를 자동으로 생성하여 세션 상태에 저장
    """
    st.subheader("상품 세부 정보 입력")

    with st.form("product_info_form"):
        st.text_input("📦 상품 이름", placeholder="예: 팔도 비빔장", key="product_name")
        st.text_input("🎯 상품 용도", placeholder="예: 식재료", key="product_usage")
        st.text_input("🏷️ 브랜드명", placeholder="예: 팔도", key="brand_name")
        st.text_area(
            "✍️ 추가 정보 (선택 사항)",
            placeholder="예: 행사 일정, 행사 내용, 강조할 점 등",
            key="text_prompt",
            height=100,
        )

        submitted = st.form_submit_button("🪄 광고 문구 생성")

        if submitted:
            if (
                not st.session_state["product_name"]
                or not st.session_state["product_usage"]
                or not st.session_state["brand_name"]
            ):
                st.info("상품 이름, 상품 용도, 브랜드명은 필수입니다.")
            else:
                product = st.session_state["product_name"]
                usage = st.session_state["product_usage"]
                brand = st.session_state["brand_name"]
                custom_prompt = st.session_state["text_prompt"]

                # 간단 예시 광고 문구 생성 (실제로는 사용자 입력과 AI 등을 활용해 생성 가능)
                st.session_state["ad_text"] = (
                    f"✨ {brand}의 혁신! {product}으로 {usage}를 더 편리하게!"
                )
                st.session_state["show_result"] = True


#######################################################################################################
# --- 글꼴 및 색상 설정 UI 렌더링 ---

def render_font_and_color_settings():
    """
    광고 문구에 적용할 글꼴과 글자 크기, 색상 설정 UI를 렌더링
    단어별 색상 적용 여부에 따라 각각 색상 지정 가능함
    """
    st.subheader("글꼴 및 색상 선택 (성은 코드 아직 연계 X)")

    sub1, sub2 = st.columns(2)
    with sub1:
        text = st.session_state["ad_text"]
        font_name = st.selectbox("사용할 폰트를 선택하세요", options=list(FONTS.keys()))
        size = st.slider("글자 크기를 선택하세요", min_value=50, max_value=200, value=125, step=1)
        stroke_width = st.slider("테두리 굵기를 선택하세요", min_value=0, max_value=10, value=0, step=1)

    with sub2:

        word_based_colors = st.checkbox("단어별 색상 적용")

        text_colors = []
        stroke_colors = []

        if word_based_colors:
            words = text.split()
            st.subheader("단어별 색상 설정")
            for i, word in enumerate(words):
                st.write(f"**{word}** 단어 색상")
                text_color = st.color_picker(f"텍스트 색상 {i+1}", "#000000", key=f"text_color_{i}")
                stroke_color = st.color_picker(f"테두리 색상 {i+1}", "#FFFFFF", key=f"stroke_color_{i}")
                text_colors.append(text_color)
                stroke_colors.append(stroke_color)
        else:
            # 전체 텍스트 및 테두리 색상 선택
            text_colors = st.color_picker("텍스트 색상을 선택하세요", "#000000")
            stroke_colors = st.color_picker("테두리 색상을 선택하세요", "#FFFFFF")


    # 반환 값은 현재는 미사용, 필요시 반환하거나 세션에 저장 가능
    return {
        "font_name": font_name,
        "font_size": size,
        "text_colors": text_colors,
        "stroke_colors": stroke_colors,
        "stroke_width": stroke_width,
    }


#######################################################################################################
# --- 광고 문구 및 결과 영역 렌더링 ---

def render_ad_text_and_preview(text_img_path):
    """
    생성된 광고 문구를 표시, 텍스트 이미지 미리보기 및 저장 기능
    광고 문구 재생성 버튼도 있음
    """
    col3, col4 = st.columns(2)

    with col3:
        st.subheader("생성된 광고 문구")

        if st.session_state["show_result"] and st.session_state["ad_text"]:
            st.success(st.session_state["ad_text"])
        else:
            st.info("광고 문구를 생성하면 여기에 표시됩니다.")

        if st.button("🔁 광고 문구 다시 생성"):
            st.session_state["ad_text"] = ""
            st.session_state["show_result"] = False
            st.rerun()

        st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)

    with col4:
        if st.session_state["show_result"]:
            st.subheader("텍스트 이미지 미리보기")

            # 텍스트 이미지 보여주기
            st.image(str(text_img_path), caption="생성된 텍스트 이미지", use_container_width=False)

            # 텍스트 이미지 저장 및 다운로드 기능
            if st.button("💾 텍스트 이미지 저장하기"):
                try:
                    img = Image.open(text_img_path).convert("RGBA")

                    # 저장 경로 및 파일명 설정
                    new_filename = "text_preview.png"
                    save_path = text_img_path.parent / new_filename
                    img.save(save_path)

                    st.success(f"✅ 텍스트 이미지가 저장되었습니다: `{new_filename}`")

                    # 브라우저 다운로드 버튼 생성
                    img_bytes = BytesIO()
                    img.save(img_bytes, format="PNG")
                    img_bytes.seek(0)

                    st.download_button(
                        label="📥 이미지 다운로드",
                        data=img_bytes,
                        file_name=new_filename,
                        mime="image/png",
                    )
                except Exception as e:
                    st.error(f"이미지 저장 중 오류 발생: {e}")


#######################################################################################################
# --- 이전/다음 단계 이동 버튼 렌더링 ---

def render_step_navigation():
    st.markdown("---")
    _, col_btns, _ = st.columns([1, 1, 1])
    with col_btns:
        prev_col, next_col = st.columns(2)
        with prev_col:
            if st.button("⬅ 이전"):
                st.session_state["step"] = 2
                st.rerun()
        with next_col:
            if st.button("➡ 다음"):
                st.session_state["step"] = 4
                st.rerun()


#######################################################################################################
# --- 메인 렌더 함수 ---

def render(platform):
    """
    광고 생성 3단계 페이지 전체 UI 렌더링 함수.
    세션 상태 초기화, 스타일 적용 후, 상품 정보 입력, 글꼴/색상 설정,
    광고 문구 및 이미지 미리보기, 이전/다음 단계 버튼을 순서대로 호출한다.
    """
    # 1) 세션 상태 초기화
    init_session_state()

    # 2) 스타일 적용
    st.markdown(sub3_CSS, unsafe_allow_html=True)

    # 3) 이미지 경로
    img_path = Path(__file__).parent.parent.parent / "images"
    text_img_path = img_path / "output.png"

    # 4) 페이지 타이틀 및 구분선
    st.title("3️⃣ 광고 문구 생성")
    st.markdown("---")

    # 5) 상품 정보 입력 폼
    render_product_info_form()

    # 6) 글꼴 및 색상 설정 UI
    render_font_and_color_settings()

    st.markdown("---")

    # 7) 광고 문구 및 텍스트 이미지 미리보기 영역
    render_ad_text_and_preview(text_img_path)

    # 8) 이전 / 다음 버튼
    render_step_navigation()
