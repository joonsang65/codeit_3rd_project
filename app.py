import streamlit as st
from streamlit_drawable_canvas import st_canvas
from PIL import Image
from modules.config_loader import load_config
from modules.pipeline_utils import load_base_pipe, apply_loras
from modules.ad_generator import run_inpainting
from modules import image_utils
from modules import gpt_module
import os


config = load_config()

uploaded_file = st.file_uploader("제품 이미지 업로드", type=["png", "jpg", "jpeg", "jfif"])
if uploaded_file:
    product_img = Image.open(uploaded_file).convert("RGBA")
    st.image(product_img, caption="원본 이미지", use_container_width=True)

if st.toggle("inpaint or generate"):
    st.write("inpaint")
else:
    st.write("generate")

canv_size = st.radio("canvas size", ['세로', '가로', '정사각형'])
if canv_size == '세로':
    canvas_size = (720, 512)
elif canv_size == '가로':
    canvas_size = (512, 720)
else:
    canvas_size = (512, 512)

st.write(f"선택한 캔버스: {canv_size} ({canvas_size})")
st.write(product_img.size)

# 배경 캔버스 설정
canvas = Image.new("RGBA", canvas_size, (255, 255, 255, 255))

# 위치 및 크기 슬라이더
st.write("📐 이미지 배치 조정")

scale = st.slider("크기 (%)", min_value=10, max_value=200, value=100, step=10)
pos_x = st.slider("X 위치", 0, canvas_size[0], value=100)
pos_y = st.slider("Y 위치", 0, canvas_size[1], value=100)

# 크기 조정
new_size = tuple([int(dim * scale / 100) for dim in product_img.size])
resized = product_img.resize(new_size)
back_rm_img = image_utils.remove_background(resized)
# 합성
canvas.paste(back_rm_img[1], (pos_x, pos_y), back_rm_img[1])

# 결과 출력
st.image(canvas, caption="최종 배치 이미지")

# 위치와 크기 정보 출력
st.code(f"Position: ({pos_x}, {pos_y})")
st.code(f"Size: {new_size}")

# 위치 정보 전달

st.code(f"back_rm_img: {back_rm_img[1].size}")
resieze_image = image_utils.resize_to_ratio(back_rm_img[1], new_size)
st.code(f"resized_image: {resieze_image.size}")

canvas = Image.new("RGBA", canvas_size, (255, 255, 255, 0))
canvas.paste(resieze_image, (pos_x, pos_y), resieze_image)


mask = image_utils.create_mask_from_product(canvas)

cols = st.columns([5,5])
with cols[0]:
    st.write(canvas)
with cols[1]:
    st.write(mask)


if st.button("GPT 분석"):
    client = gpt_module.GPTClient(os.getenv(config['openai']['api_key_env']), config['openai']['gpt_model'])
    img_tuple = image_utils.encode_images(config, product_img=back_rm_img[1])
    ad_plan = client.analyze_ad_plan(img_tuple[0], img_tuple[1], "food", "배경 제작")

    st.write("GPT 분석 진행")
    st.code(ad_plan)
    prompt = client.convert_to_sd_prompt(ad_plan)
    st.code(prompt)

    base_pipe = load_base_pipe(config, 'inpaint')
    pipe = apply_loras(base_pipe, config, category="food")
    gen_imgs = run_inpainting(pipe, canvas, mask, prompt, config)
    st.write(img for img in gen_imgs)
    if st.butten("clear"):
        st.cache_resource.clear

