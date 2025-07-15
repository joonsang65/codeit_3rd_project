import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import csv

from modules import utils, pipeline_utils, gpt_module, ad_generator, evaluation

from typing import Literal
from PIL import Image
import logging 
from dotenv import load_dotenv

load_dotenv()

logger = utils.setup_logger(__name__, logging.INFO)

try:
    if os.path.exists("./model_config.yaml"):
        cfg = utils.load_config("model_config.yaml")
    else:
        cfg = utils.load_config("model_dev/model_config.yaml")
except Exception as e:
    logger.warning(f"경로를 찾지 못했습니다: {e}")

API_KEY = os.getenv(cfg['openai']['api_key_env'])
CANVAS_SIZE = (512, 512)
CATEGORY = "cosmetics"

def resolve_path(path):
    if not os.path.isabs(path):
        return os.path.abspath(os.path.join(os.path.dirname(__file__), path))
    return path

for key in cfg['paths']:
    cfg['paths'][key] = resolve_path(cfg['paths'][key])

def run_pipe(mode:str):
    cfg['product_type'] = CATEGORY
    cfg['canvas_size'] = CANVAS_SIZE
    cfg['generation']['guidance_scale'] = 6
    cfg['generation']['inference_steps'] = 40

    client = gpt_module.GPTClient(api_key=API_KEY, model_name=cfg['openai']['gpt_model'])
    if mode == 'text2img':
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
                "content": "화장품 광고에 맞는 배경"
            }
        ]
        logger.info("✅ 광고 전략 생성 중...")
        ad_plan = client.chat(messages=message_for_ad_plan, max_tokens=200)
        logger.info(f"\n🎯 광고 전략:\n{ad_plan}")

        prompt = client.convert_to_sd_prompt(ad_plan)
        logger.info(f"\n🎨 SD 프롬프트:\n{prompt}")

        pipe = pipeline_utils.load_pipeline_by_type(cfg, mode, controlnet_types=None)
        if hasattr(pipe, "unload_lora_weights"):
            pipe.unload_lora_weights()
        pipeline_utils.apply_loras(pipe, cfg, category=CATEGORY)
        logger.info(f"활성 LoRA: {pipe.get_active_adapters()}")

        logger.info("배경 생성 중...")
        images = ad_generator.generate_background(pipe, prompt, cfg)
        
    elif mode == 'inpaint':
        product_image = Image.open(cfg['paths']['product_image'])
        reference_image = None

        logger.info("이미지 배경 제거 중...")
        _, back_rm_img = utils.remove_background(product_image)

        logger.info("이미지 사이즈 변경 중...")

        TARGET_SIZE = (256, 256)

        resized_img = utils.resize_to_ratio(back_rm_img, TARGET_SIZE)
        canvas = Image.new("RGBA", cfg['canvas_size'], (255, 255, 255, 255))

        POSITION = (300, 220)

        canvas = utils.overlay_product(canvas, resized_img, POSITION)
        _, back_rm_canv = utils.remove_background(canvas)
        mask = utils.create_mask(back_rm_canv)
        
        PURPOSE = f"{CATEGORY}에 맞는 배경 생성"

        product_b64 = utils.encode_image(canvas)
        reference_image = utils.encode_image(reference_image) if reference_image else None

        logger.info("✅ 광고 전략 생성 중...")
        ad_plan = client.analyze_ad_plan(
            product_b64, 
            reference_image, 
            product_type=CATEGORY, 
            marketing_type=PURPOSE
            )
        logger.info(f"\n🎯 광고 전략:\n{ad_plan}")

        prompt = client.convert_to_sd_prompt(ad_plan)
        logger.info(f"\n🎨 SD 프롬프트:\n{prompt}")

        pipe = pipeline_utils.load_pipeline_by_type(cfg, mode, controlnet_types=None)
        if hasattr(pipe, "unload_lora_weights"):
            pipe.unload_lora_weights()
        pipeline_utils.apply_loras(pipe, cfg, category=CATEGORY)
        logger.info(f"활성 LoRA: {pipe.get_active_adapters()}")

        images = ad_generator.run_inpainting(pipe, canvas, mask, prompt, cfg)

    else:
        raise ValueError(f"The Mode is Not Supported. {mode}")
    logger.info("생성된 이미지 평가 진행 중...")
    evaluator = evaluation.ImageEvaluator()
    eval_logs = [evaluator.evaluate_image(img, prompt) for img in images]
    
    SAVE_DIR = 'outputs/eval_results'
    utils.ensure_dir(SAVE_DIR)
    csv_path = os.path.join(SAVE_DIR, "evaluation_results.csv")

    with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
        writer = None  # 초기화
        if mode == 'text2img':
            PREFIX = "bg"
        elif mode == 'inpaint':
            PREFIX = 'inp'
        else:
            raise ValueError(f"{mode} is not supported")
        
        for idx, (img, log) in enumerate(zip(images, eval_logs)):
            # 1. 이미지 저장
            filename = f"{PREFIX}_{idx:02d}.png"
            img.save(os.path.join(SAVE_DIR, filename))

            # 2. CSV 저장용 dict 구성
            row = {"index": idx, "filename": filename}
            row.update(log)  # log가 dict라고 가정

            # 3. 첫 줄에 헤더 작성
            if writer is None:
                fieldnames = list(row.keys())
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

            # 4. 로그 저장
            writer.writerow(row)

if __name__ == "__main__":
    run_pipe(mode='inpaint')
