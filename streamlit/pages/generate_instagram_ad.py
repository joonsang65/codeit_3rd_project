# pages/2_인스타_광고_제작.py
import streamlit as st
from PIL import Image

st.set_page_config(page_title="인스타그램 광고 제작", layout="wide")
st.title("📸 인스타그램 광고 제작")

st.markdown("""
정사각형 비율(1:1)의 인스타그램 피드용 광고 이미지를 AI로 제작해보세요.
상품 이미지를 업로드하고, 원하는 배경 스타일과 광고 문구 스타일을 입력하면 자동으로 광고 이미지가 생성됩니다.
""")

if "insta_uploaded_image" not in st.session_state:
    st.session_state.insta_uploaded_image = None

if "insta_bg_prompt" not in st.session_state:
    st.session_state.insta_bg_prompt = ""

if "insta_ad_prompt" not in st.session_state:
    st.session_state.insta_ad_prompt = ""

with st.sidebar:
    with st.form("insta_form"):
        st.info("**배경 이미지 프롬프트 입력**", icon=None)
        with st.expander(":rainbow[**Refine your output here**]"):
            width = st.number_input("Width of output image", value=1024)
            height = st.number_input("Height of output image", value=1024)
            num_outputs = st.slider("Number of images to output", value=4, min_value=1, max_value=4)
            scheduler = st.selectbox('Scheduler', ('DDIM', 'DPMSolverMultistep', 'HeunDiscrete',
                                                   'KarrasDPM', 'K_EULER_ANCESTRAL', 'K_EULER', 'PNDM'))
            num_inference_steps = st.slider("Number of denoising steps", value=50, min_value=1, max_value=500)
            guidance_scale = st.slider("Scale for classifier-free guidance", value=7.5, min_value=1.0, max_value=50.0, step=0.1)
            prompt_strength = st.slider("Prompt strength (1.0 = strong effect)", value=0.8, max_value=1.0, step=0.1)
            refine = st.selectbox("Select refine style", ("expert_ensemble_refiner", "None"))
            high_noise_frac = st.slider("Noise fraction for refine", value=0.8, max_value=1.0, step=0.1)

        prompt = st.text_area(":orange[**배경 이미지 프롬프트 작성란✍🏾**]", value="트렌디한 카페")
        negative_prompt = st.text_area(":orange[**이미지에 들어가면 안되는 것 🙅🏽‍♂️**]", value="사람")

        submitted = st.form_submit_button("Submit", type="primary", use_container_width=True)

st.subheader("상품 이미지 업로드")
uploaded_file = st.file_uploader("인스타그램 광고에 사용할 상품 이미지를 업로드하세요", type=["png", "jpg", "jpeg"])

if uploaded_file:
    st.session_state.insta_uploaded_image = Image.open(uploaded_file)
    st.image(st.session_state.insta_uploaded_image, caption="업로드한 상품 이미지", use_column_width=True)

if st.button("🪄 인스타그램 광고 이미지 생성하기"):
    if not st.session_state.insta_uploaded_image:
        st.warning("상품 이미지를 먼저 업로드해주세요.")
    elif not st.session_state.insta_bg_prompt or not st.session_state.insta_ad_prompt:
        st.warning("배경 스타일과 광고 문구 스타일을 모두 입력해주세요.")
    else:
        with st.spinner("AI가 이미지를 생성 중입니다... (샘플 결과 표시 중)"):
            st.success("✅ 이미지 생성 완료! 아래 결과를 확인하세요.")

            cols = st.columns(4)
            for i in range(4):
                with cols[i]:
                    st.image(st.session_state.insta_uploaded_image, caption=f"광고 이미지 {i+1} (샘플)")
                    st.button(f"선택하기 {i+1}", key=f"insta_select_{i+1}")

st.subheader("이미지 다듬기 (준비 중)")
st.info("텍스트 위치, 색상, 크기 등을 조절하는 기능은 추후 제공될 예정입니다.")
