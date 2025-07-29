# pages/3_포스터_광고_제작.py
import streamlit as st
from PIL import Image

st.set_page_config(page_title="포스터 광고 제작", layout="wide")
st.title("🖼️ 포스터 광고 제작")

st.markdown("""
홍보용 인쇄물, 배너, 디지털 포스터 등 다양한 곳에 활용 가능한 세로형 광고 이미지를 AI로 제작해보세요.
상품 이미지를 업로드하고, 원하는 배경 스타일과 광고 문구 스타일을 입력하면 자동으로 광고 이미지가 생성됩니다.
""")

if "poster_uploaded_image" not in st.session_state:
    st.session_state.poster_uploaded_image = None

if "poster_bg_prompt" not in st.session_state:
    st.session_state.poster_bg_prompt = ""

if "poster_ad_prompt" not in st.session_state:
    st.session_state.poster_ad_prompt = ""

with st.sidebar:
    with st.form("poster_form"):
        st.info("**배경 이미지 프롬프트 입력**", icon=None)
        with st.expander(":rainbow[**Refine your output here**]"):
            width = st.number_input("Width of output image", value=768)
            height = st.number_input("Height of output image", value=1024)
            num_outputs = st.slider("Number of images to output", value=2, min_value=1, max_value=4)
            scheduler = st.selectbox('Scheduler', ('DDIM', 'DPMSolverMultistep', 'HeunDiscrete', 'KarrasDPM', 'K_EULER_ANCESTRAL', 'K_EULER', 'PNDM'))
            num_inference_steps = st.slider("Number of denoising steps", value=50, min_value=1, max_value=500)
            guidance_scale = st.slider("Scale for classifier-free guidance", value=7.5, min_value=1.0, max_value=50.0, step=0.1)
            prompt_strength = st.slider("Prompt strength (1.0 = strong effect)", value=0.8, max_value=1.0, step=0.1)
            refine = st.selectbox("Select refine style", ("expert_ensemble_refiner", "None"))
            high_noise_frac = st.slider("Noise fraction for refine", value=0.8, max_value=1.0, step=0.1)

        prompt = st.text_area(":orange[**배경 이미지 프롬프트 작성란✍🏾**]", value="가을 페스티벌 배경")
        negative_prompt = st.text_area(":orange[**이미지에 들어가면 안되는 것 🙅🏽‍♂️**]", value="사람")
        submitted = st.form_submit_button("Submit", type="primary", use_container_width=True)

st.subheader("상품 이미지 업로드")
uploaded_file = st.file_uploader("포스터 광고에 사용할 상품 이미지를 업로드하세요", type=["png", "jpg", "jpeg"])

if uploaded_file:
    st.session_state.poster_uploaded_image = Image.open(uploaded_file)
    st.image(st.session_state.poster_uploaded_image, caption="업로드한 상품 이미지", use_column_width=True)

if st.button("🪄 포스터 광고 이미지 생성하기"):
    if not st.session_state.poster_uploaded_image:
        st.warning("상품 이미지를 먼저 업로드해주세요.")
    else:
        with st.spinner("AI가 이미지를 생성 중입니다... (샘플 결과 표시 중)"):
            st.success("✅ 이미지 생성 완료! 아래 결과를 확인하세요.")

            for i in range(2):
                st.image(st.session_state.poster_uploaded_image, caption=f"광고 이미지 {i+1} (샘플)", use_column_width=True)
                st.button(f"선택하기 {i+1}", key=f"poster_select_{i+1}")

st.subheader("이미지 다듬기 (준비 중)")
st.info("텍스트 위치, 색상, 크기 등을 조절하는 기능은 추후 제공될 예정입니다.")
