import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ["HF_HOME"] = "D:/huggingface"

from typing import Literal
from PIL import Image
import logging 

from image_modules import utils, pipeline_utils, gpt_module, ad_generator


logger = utils.setup_logger(__name__, logging.DEBUG)
base_dir = os.path.dirname(os.path.abspath(__file__))  # 즉: app/services/
try:
    config_path = os.path.join(base_dir, "model_config.yaml")
    config = utils.load_config(config_path)
    logger.info(config)
except Exception as e:
    logger.warning(f"경로를 찾지 못했습니다: {e}")

# try:
#     if os.path.exists("./model_config.yaml"):
#         config = utils.load_config("model_config.yaml")
#     else:
#         config = utils.load_config("backend/services/model_config.yaml")

#     logger.info(config)
# except Exception as e:
#     logger.warning(f"경로를 찾지 못했습니다: {e}")
    
def resolve_path(path):
    if not os.path.isabs(path):
        return os.path.abspath(os.path.join(os.path.dirname(__file__), path))
    return path

for key in config['paths']:
    config['paths'][key] = resolve_path(config['paths'][key])

def step1(img: Image.Image):
    """
    Step 1: 이미지 전처리 및 배경 제거
    - 입력된 이미지의 배경을 제거하고, 지정된 크기로 리사이즈합니다.
    - 최종적으로 빈 캔버스에 리사이즈된 이미지를 오버레이합니다.

    input:
    - img_path (str): 배경 제거할 이미지의 경로
    output:
    - back_rm_canv (PIL.Image.Image): 배경이 제거된 캔버스 이미지
    """
    utils.ensure_dir(config['paths']['output_dir'])
    # config 내부에는 존재 하지 않으나
    # User input으로 받을 경우 product type으로 config에 등록하기
    config['product_type'] = "food"
    # canvas_size를 저장하여 최종 출력 반영하기 (UI에서 받아오기)
    config['canvas_size'] = (512, 512)

    # input_image의 경우 PIL.Image.Image 형태로 입력하기
    # 데이터에서 참조할 경우 마찬가지로 config에 입력해 주기
    #config['paths']['product_image'] = img_path # 경로 (예: '.images/product.png')
    # utils.remove_background(input_image) # <- 이미지 입력 가능(사용자 입력이 있는 경우)

    logger.info("이미지 배경 제거 중...")
    orig_img, back_rm_img = utils.remove_background(img)
    
    # 배경이 제거된 이미지를 사용자가 원하는 사이즈로 변경 Tuple 가져오기
    logger.info("이미지 사이즈 변경 중...")
    resized_img = utils.resize_to_ratio(back_rm_img, (128, 128))

    # 변경 정보 빈 캠퍼스에 반영하기 (위치 정보 포함)
    canvas = Image.new("RGBA", config['canvas_size'], (255, 255, 255, 255))
    canvas = utils.overlay_product(canvas, resized_img, (300, 220))
    canv_img, back_rm_canv = utils.remove_background(canvas)

    return resized_img, back_rm_canv

def step2(
    mode: Literal['inpaint', 'text2img'] = 'inpaint',
    resized_img: Image.Image = None, 
    back_rm_canv: Image.Image = None
) -> Image.Image | list[Image.Image]:
    """
    Step 2: 광고 전략 생성 및 이미지 생성
    - OpenAI API를 사용하여 광고 전략을 생성합니다.
    - 생성된 광고 전략을 기반으로 Stable Diffusion 파이프라인을 통해 이미지를 생성합니다.
    - 생성된 PIL 이미지 객체 또는 이미지 리스트를 반환합니다.
    
    Args:
        mode (str): 'inpaint' 또는 'text2img' 생성 모드 선택
        resized_img (PIL.Image.Image): 리사이즈된 상품 이미지
        back_rm_canv (PIL.Image.Image): 배경 제거된 캔버스 이미지
    
    Returns:
        PIL.Image.Image 또는 리스트: 생성된 이미지 또는 이미지 리스트
    """
    logger.info("OpenAI 모델 불러오기...")
    api_key = os.getenv(config['openai']['api_key_env'])
    if not api_key:
        raise RuntimeError(f"{config['openai']['api_key_env']} 환경 변수가 설정되어 있지 않습니다.")
    client = gpt_module.GPTClient(
        api_key=api_key,
        model_name=config['openai']['gpt_model']
    )
    
    if mode == 'inpaint':
        logger.info(f"{mode.upper()} 설정 확인!")
        logger.info("이미지 마스킹 생성 중...")
        mask = utils.create_mask(back_rm_canv)

        logger.info("이미지 인코딩 -> base64...")
        img_base64 = utils.encode_image(back_rm_canv)
        ref_base64 = None  # 필요시 UI에서 받기

        logger.info("광고 전략 생성 중...")
        ad_plan = client.analyze_ad_plan(
            product_b64=img_base64,
            ref_b64=ref_base64,
            product_type=config['product_type'],
            marketing_type="인풋 이미지를 마스킹한 상태에서 배경 생성하기"
        )
        logger.debug(ad_plan)

        logger.info("광고 전략 -> 프롬프트 변경 진행 중...")
        prompt = client.convert_to_sd_prompt(ad_plan)
        logger.debug(prompt)

        logger.info("파이프라인 불러오기...")
        base_pipe = pipeline_utils.load_base_pipe(config, mode)
        pipe = pipeline_utils.apply_loras(base_pipe, config, category="cosmetics")

        logger.info("Inference 진행 중...")
        images = ad_generator.run_inpainting(pipe, back_rm_canv, mask, prompt, config)

        # 파일 저장은 호출자에게 위임
        return images

    else:  # mode == 'text2img'
        logger.info(f"{mode.upper()} 설정 확인!")
        message = [
            {
                "role": "system", 
                "content": (
                    "You are an advertisement planner, How would you plan given the advertisement with for the product? "
                    "You are only allow to describe background which fits to the product.\n"
                    "Do NOT mention about product, human, or text in the background, only the mood, color, design." 
                )
            },
            {
                "role": "user",
                "content": "화장품 광고에 맞는 배경" 
            }
        ]
        logger.info("광고 전략 생성 중...")
        ad_plan = client.chat(messages=message, max_tokens=200)
        logger.debug(ad_plan)

        logger.info("광고 전략 -> 프롬프트 변경 진행 중...")
        prompt = client.convert_to_sd_prompt(ad_plan)
        logger.debug(prompt)

        logger.info("파이프라인 불러오기...")
        base_pipe = pipeline_utils.load_base_pipe(config, 'text2img')
        pipe_t2i = pipeline_utils.apply_loras(base_pipe, config, category='cosmetics')

        logger.info("배경 이미지 생성 중...")
        gen_backs = ad_generator.generate_background(pipe_t2i, prompt, config)

        logger.info("IP-Adapter 설정하기...")
        ip_adapter = pipeline_utils.load_ip_adapter(pipe_t2i, config)

        logger.info("IP-Adapter Inference 진행 중...")
        ip_gen = ad_generator.ip_adapter_inference(ip_adapter, config, prompt, gen_backs, resized_img)

        return ip_gen

