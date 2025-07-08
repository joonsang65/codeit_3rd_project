import os
from modules import utils, pipeline_utils, gpt_module, ad_generator
from typing import Literal
from PIL import Image
import logging 
from dotenv import load_dotenv
load_dotenv()

try:
    config = utils.load_config("model_dev/model_config.yaml")
    print(config)
except Exception as e:
    print(f"경로를 찾지 못했습니다: {e}")
    
def resolve_path(path):
    if not os.path.isabs(path):
        return os.path.abspath(os.path.join(os.path.dirname(__file__), path))
    return path

for key in config['paths']:
    config['paths'][key] = resolve_path(config['paths'][key])

product_image_path = config['paths']['product_image']

logger = utils.setup_logger(__name__, logging.DEBUG)

def main(mode: Literal['inpaint', 'text2img'] = 'inpaint'):
    utils.ensure_dir(config['paths']['output_dir'])
    # config 내부에는 존재 하지 않으나
    # User input으로 받을 경우 product type으로 config에 등록하기
    config['product_type'] = "food"
    # canvas_size를 저장하여 최종 출력 반영하기 (UI에서 받아오기)
    config['canvas_size'] = (512, 512)

    # input_image의 경우 PIL.Image.Image 형태로 입력하기
    # 데이터에서 참조할 경우 마찬가지로 config에 입력해 주기
    # config['paths']['product_image'] = 경로 (예: '.images/product.png')
    # utils.remove_background(input_image: PIL.Image.Image) <- 이미지 입력 가능(사용자 입력이 있는 경우)
    logger.info("이미지 배경 제거 중...")
    orig_img, back_rm_img = utils.remove_background(config['paths']['product_image'])
    
    # 배경이 제거된 이미지를 사용자가 원하는 사이즈로 변경 Tuple 가져오기
    logger.info("이미지 사이즈 변경 중...")
    resized_img = utils.resize_to_ratio(back_rm_img, (128, 128))

    # 변경 정보 빈 캠퍼스에 반영하기 (위치 정보 포함)
    canvas = Image.new("RGBA", config['canvas_size'], (255, 255, 255, 255))
    canvas = utils.overlay_product(canvas, resized_img, (300, 220))
    canv_img, back_rm_canv = utils.remove_background(canvas)

    logger.info("OpenAI 모델 불러오기...")
    client = gpt_module.GPTClient(
        api_key=os.getenv(config['openai']['api_key_env']), 
        model_name=config['openai']['gpt_model']
        )
    
    if mode == 'inpaint':
        # 사이즈 변경된 이미지 대상으로 마스킹 시도('inpaint'의 경우)
        logger.info(f"{mode.upper()} 설정 확인!")
        logger.info(f"이미지 마스킹 생성 중...")
        mask = utils.create_mask(back_rm_canv)
        # image를 base64로 인코딩하여 OpenAI에게 참조형으로 보내기
        # 예시 광고 이미지가 있다면 마찬가지로 인코딩해서 진행하기
        logger.info(f"이미지 인코딩 -> base64...")
        img_base64 = utils.encode_image(back_rm_canv)
        # ref_base64 = utils.encode_image(ref_image) # UI에서 받기
        ref_base64 = None

        # 광고 플랜 생성하기
        logger.info(f"광고 전략 생성 중...")
        ad_plan = client.analyze_ad_plan(
            product_b64=img_base64, 
            ref_b64=ref_base64 , 
            product_type=config['product_type'], 
            marketing_type="인풋 이미지를 마스킹한 상태에서 배경 생성하기"
            )
        logger.debug(ad_plan)

        logger.info(f"광고 전략 -> 프롬프트 변경 진행 중...")
        prompt = client.convert_to_sd_prompt(ad_plan)
        logger.debug(prompt)

        logger.info("파이프라인 불러오기...")
        base_pipe = pipeline_utils.load_base_pipe(config, mode)
        # 카테고리 또한 UI에서 받아오는 식이나, 입력에서 추출하여 food, cosmetics, furniture로 나누는게 좋아보인다.
        pipe = pipeline_utils.apply_loras(base_pipe, config, category="cosmetics") 

        logger.info("Inference 진행 중...")
        image = ad_generator.run_inpainting(pipe, back_rm_canv, mask, prompt, config)

        logger.info("생성 이미지 저장 중...")
        if len(image) > 1:
            for i, img in enumerate(image):
                img.save(f"{config['paths']['output_dir']}/inprint_gen{i+1}.png")
        elif len(image) == 1:
            image.save(f"{config['paths']['output_dir']}/inprint_gen.png")
        else:
            raise ValueError("이미지 생성에 실패했습니다.")

    else:
        logger.info(f"{mode.upper()} 설정 확인!")
        message = [
            {
                "role": "system", 
                "content": (
                    "You are an advertisement planner, How would you plan given the advertisement with for the product? "
                    "You are only allow to describe background which fits to the product.\n"
                    "Do NOT metion about product, human, or text in the background, only the mood, color, design." 
                    )
            },
            {
                "role": "user",
                "content": "화장품 광고에 맞는 배경" 
            }
        ]
        logger.info(f"광고 전략 생성 중...")
        ad_plan = client.chat(messages=message, max_tokens=200)
        logger.debug(ad_plan)

        logger.info(f"광고 전략 -> 프롬프트 변경 진행 중...")
        prompt = client.convert_to_sd_prompt(ad_plan)
        logger.debug(prompt)

        logger.info("파이프라인 불러오기...")
        base_pipe = pipeline_utils.load_base_pipe(config, 'text2img')
        pipe_t2i = pipeline_utils.apply_loras(base_pipe, config, category='cosmetics')

        logger.info("배경 이미지 생성 중...")
        gen_backs = ad_generator.generate_background(pipe_t2i, prompt, config)

        logger.info("IP-Adapter 설정하기...")
        ip_adapter = pipeline_utils.load_ip_adapter(pipe_t2i, config)

        ip_gen = ad_generator.ip_adapter_inference(ip_adapter, config, prompt, gen_backs, resized_img)

        if len(ip_gen) > 1:
            for i, img in enumerate(ip_gen):
                img.save(f"{config['paths']['output_dir']}/ip_gen{i+1}.png")
        elif len(ip_gen) == 1:
            ip_gen.save(f"{config['paths']['output_dir']}/ip_gen.png")
        else:
            raise ValueError("이미지 생성 실패")


if __name__ == "__main__":
    main(mode='inpaint')
