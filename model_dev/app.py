import streamlit as st
from PIL import Image
from modules import utils, gpt_module, pipeline_utils, evaluation, ad_generator
import os

@st.cache_resource
def load_pipes(cfg, p_type='text2img'):
    evaluator = evaluation.ImageEvaluator()
    pipelines = pipeline_utils.load_pipeline_by_type(cfg, pipeline_type=p_type)
    # for name in pipelines:
    #     for pipe in pipelines[name].values():
    #         pipe.enable_attention_slicing()
    #         pipe.enable_vae_slicing()
    #         pipe.enable_model_cpu_offload()
    return pipelines, evaluator

# 설정 및 API 키 로드
cfg = utils.load_config("model_config.yaml")
api_key = os.getenv(cfg['openai']['api_key_env'])

pipelines, evaluator = load_pipes(cfg)
client = gpt_module.GPTClient(api_key=api_key, model_name=cfg['openai']['gpt_model'])

# UI 입력 받기
type = st.radio('제품 타입', ['food', 'cosmetics', 'furniture'])
intention = st.text_input('광고 목적', placeholder='예: 화장품 광고')

# 광고 전략 (GPT 호출 최소화)
if 'intention' not in st.session_state or st.session_state.intention != intention:
    st.session_state.intention = intention
    st.session_state.ad_plan = None
    st.session_state.prompt = None

if intention and st.session_state.ad_plan is None:
    with st.spinner("광고 전략 생성 중..."):
        message_for_ad_plan = [
            {
                "role": "system",
                "content": (
                    "You are an advertisement planner. Plan the advertisement background for a product. "
                    "Do NOT mention the product, human, or text. Only describe mood, color, and background design."
                )
            },
            {
                "role": "user",
                "content": f"{intention}에 맞는 배경"
            }
        ]
        st.session_state.ad_plan = client.chat(message_for_ad_plan, max_tokens=200)
        st.session_state.prompt = client.convert_to_sd_prompt(st.session_state.ad_plan)

if st.session_state.ad_plan:
    with st.expander('광고 전략'):
        st.write(st.session_state.ad_plan)
    with st.expander('프롬프트 생성'):
        st.code(st.session_state.prompt, wrap_lines=True)

# 캔버스 크기 선택
canv_size = st.radio("canvas size", ['세로', '가로', '정사각형'])
if canv_size == '가로':
    canvas_size = (720, 512)
elif canv_size == '세로':
    canvas_size = (512, 720)
else:
    canvas_size = (512, 512)

cfg.update({"canvas_size": canvas_size})
st.write(f"선택한 캔버스: {canv_size} ({canvas_size})")

# 배경 생성 버튼 및 상태 플래그
if st.button("배경 생성하기"):
    st.session_state.generate_background = True

if st.session_state.get('generate_background'):
    with st.spinner("배경 생성 중..."):
        images = ad_generator.generate_background(pipelines, st.session_state.prompt, cfg)
        st.session_state.images = images
    st.session_state.generate_background = False

# 생성 이미지 보여주기 및 선택
if 'images' in st.session_state and st.session_state.images:
    images = st.session_state.images
    eval_logs = [evaluator.evaluate_image(img, st.session_state.prompt) for img in images]
    cols = st.columns(2)
    for i, (img, log) in enumerate(zip(images, eval_logs)):
        with cols[i % 2]:
            st.image(img, caption=f"Image {i+1}\n{log}", use_container_width=True)
        if i % 2 == 1 and i != len(images) - 1:
            cols = st.columns(2)

    numbs = st.number_input('이미지 선택', min_value=1, max_value=len(images), step=1)
    if numbs:
        st.session_state.back_img = images[numbs - 1]
        st.image(st.session_state.back_img, caption="🎯 선택된 배경 이미지", use_container_width=True)

# 제품 이미지 업로드 및 합성 등...
uploaded_file = st.file_uploader("제품 이미지 업로드", type=["png", "jpg", "jpeg", "jfif"])
if uploaded_file:
    product_img = Image.open(uploaded_file).convert("RGBA")
    st.image(product_img, caption="원본 이미지", use_container_width=True)

    st.write(product_img.size)
    canvas_size = cfg['canvas_size']

    # 배경 캔버스 설정
    canvas = st.session_state.back_img.copy() if st.session_state.back_img else Image.new("RGBA", canvas_size, (255, 255, 255, 255))

    # 위치 및 크기 슬라이더
    st.write("📐 배치 조정")
    scale = st.slider("크기 (%)", min_value=10, max_value=200, value=100, step=10)
    pos_x = st.slider("X 위치", 0, canvas_size[0], value=100)
    pos_y = st.slider("Y 위치", 0, canvas_size[1], value=100)

    # 크기 조정
    new_size = tuple([int(dim * scale / 100) for dim in product_img.size])
    resized = product_img.resize(new_size)
    _, transparent = utils.remove_background(resized)
    # 합성
    canvas.paste(transparent, (pos_x, pos_y), transparent)

    # 결과 출력
    st.image(canvas, caption="🧪 최종 합성 결과", use_container_width=True)
    st.code(f"Position: ({pos_x}, {pos_y})")
    st.code(f"Size: {new_size}")

    # 위치 정보 전달
    st.code(f"back_rm_img: {transparent.size}")
    resieze_image = utils.resize_to_ratio(transparent, new_size)
    st.code(f"resized_image: {resieze_image.size}")

    canvas = Image.new("RGBA", canvas_size, (255, 255, 255, 0))
    canvas.paste(resieze_image, (pos_x, pos_y), resieze_image)

    mask = utils.create_mask(canvas)

    cols = st.columns([5,5])
    with cols[0]:
        st.write(canvas)
    with cols[1]:
        st.write(mask)

    # canvas.save("model_dev/images/product.png")
    # cfg['paths']['product_image'] = "./images/product.png"

    # if st.button("GPT 분석"):
    #     img_base64 = utils.encode_image(canvas)
    #     ref_base64 = utils.encode_image(st.session_state.back_img)
    #     ad_plan = client.analyze_ad_plan(img_base64, ref_base64, type, intention)

    #     st.write("GPT 분석 진행")
    #     st.code(ad_plan)
    #     prompt = client.convert_to_sd_prompt(ad_plan)
    #     st.code(prompt)
        
    #     pipelines = load_pipes(cfg, 'inpaint')
    #     pipe = pipeline_utils.apply_loras(pipelines, cfg, category=type)

#         mode = st.radio('모드', ['inpaint', 'text2img'])
#         if mode == "inpaint":
#             with st.spinner('inpaint 생성 중'):
#                 gen_imgs = ad_generator.run_inpainting(pipe, canvas, mask, prompt, cfg)
#                 for i, img in enumerate(gen_imgs):
#                     st.image(img, caption=f"Inpainted Image {i+1}")
#                 if st.button("clear"):
#                     st.cache_resource.clear()
                
#                 st.write("Load IP-Adapter")
#         else:
#             pass
# st.markdown(f"### ⤵️ IP-Adapter Smoothing: Image")
# try:
#     from modules.pipeline_utils import load_ip_adapter

#     pipe_text2img = pipeline_utils.apply_loras(pipelines, cfg, category=type)
#     ip_adapter = load_ip_adapter(pipe_text2img, cfg)
#     ip_gen = ad_generator.ip_adapter_inference(ip_adapter, cfg, st.session_state.prompt, st.session_state.back_img, transparent)
#     st.image(ip_gen)
# except Exception as e:
#     st.error(f"IP-Adapter failed: {e}")
        