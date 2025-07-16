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
base_dir = os.path.dirname(os.path.abspath(__file__))
try:
    config_path = os.path.join(base_dir, "model_config.yaml")
    cfg = utils.load_config(config_path)
    logger.info(cfg)
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

def generate_prompt(client, category):
    messages = [
        {
            "role": "system",
            "content": (
                "You are an advertisement planner. Plan the advertisement background for a product. "
                "Do NOT mention the product, human, or text. Only describe mood, color, and background design."
            )
        },
        {"role": "user", "content": f"{category} 광고에 맞는 배경"}
    ]
    logger.info("✅ 광고 전략 생성 중...")
    ad_plan = client.chat(messages=messages, max_tokens=200)
    logger.info(f"\n🎯 광고 전략:\n{ad_plan}")
    prompt = client.convert_to_sd_prompt(ad_plan)
    logger.info(f"\n🎨 SD 프롬프트:\n{prompt}")
    return prompt

def prepare_pipeline(cfg, mode, category):
    pipe = pipeline_utils.load_pipeline_by_type(cfg, mode, controlnet_types=None)
    if hasattr(pipe, "unload_lora_weights"):
        pipe.unload_lora_weights()
    pipeline_utils.apply_loras(pipe, cfg, category=category)
    logger.info(f"활성 LoRA: {pipe.get_active_adapters()}")
    return pipe

def evaluate_and_save(images, prompt, mode):
    logger.info("생성된 이미지 평가 진행 중...")
    evaluator = evaluation.ImageEvaluator()
    eval_logs = [evaluator.evaluate_image(img, prompt) for img in images]

    save_dir = 'outputs/eval_results'
    utils.ensure_dir(save_dir)
    csv_path = os.path.join(save_dir, "evaluation_results.csv")
    prefix = "bg" if mode == 'text2img' else "inp"

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = None
        for idx, (img, log) in enumerate(zip(images, eval_logs)):
            filename = f"{prefix}_{idx:02d}.png"
            img.save(os.path.join(save_dir, filename))
            row = {"index": idx, "filename": filename, **log}
            if writer is None:
                writer = csv.DictWriter(f, fieldnames=row.keys())
                writer.writeheader()
            writer.writerow(row)

def run_text2img(cfg):
    client = gpt_module.GPTClient(api_key=API_KEY, model_name=cfg['openai']['gpt_model'])
    prompt = generate_prompt(client, CATEGORY)
    pipe = prepare_pipeline(cfg, "text2img", CATEGORY)

    logger.info("배경 생성 중...")
    images = ad_generator.generate_background(pipe, prompt, cfg)
    evaluate_and_save(images, prompt, mode="text2img")

def run_inpaint(cfg):
    client = gpt_module.GPTClient(api_key=API_KEY, model_name=cfg['openai']['gpt_model'])
    product_image = Image.open(cfg['paths']['product_image'])

    logger.info("이미지 배경 제거 중...")
    _, back_rm_img = utils.remove_background(product_image)

    logger.info("이미지 사이즈 변경 중...")
    resized_img = utils.resize_to_ratio(back_rm_img, (256, 256))
    canvas = Image.new("RGBA", cfg['canvas_size'], (255, 255, 255, 255))
    canvas = utils.overlay_product(canvas, resized_img, (300, 220))

    _, back_rm_canv = utils.remove_background(canvas)
    mask = utils.create_mask(back_rm_canv)

    PURPOSE = f"{CATEGORY}에 맞는 배경 생성"
    product_b64 = utils.encode_image(canvas)
    reference_image = None

    logger.info("✅ 광고 전략 생성 중...")
    ad_plan = client.analyze_ad_plan(
        product_b64,
        ref_b64=reference_image,
        product_type=CATEGORY,
        marketing_type=PURPOSE
    )
    logger.info(f"\n🎯 광고 전략:\n{ad_plan}")

    prompt = client.convert_to_sd_prompt(ad_plan)
    logger.info(f"\n🎨 SD 프롬프트:\n{prompt}")

    pipe = prepare_pipeline(cfg, "inpaint", CATEGORY)
    images = ad_generator.run_inpainting(pipe, canvas, mask, prompt, cfg)
    evaluate_and_save(images, prompt, mode="inpaint")

def run_pipe(mode: str, cfg=cfg):
    cfg['product_type'] = CATEGORY
    cfg['canvas_size'] = CANVAS_SIZE
    cfg['generation']['guidance_scale'] = 6
    cfg['generation']['inference_steps'] = 40

    if mode == 'text2img':
        run_text2img(cfg)
    elif mode == 'inpaint':
        run_inpaint(cfg)
    else:
        raise ValueError(f"The Mode is Not Supported: {mode}")

def post_process(
        mode:str=None,
        image:Image.Image=None, 
        mask:Image.Image=None, 
        gen_image:Image.Image=None, 
        cfg:dict=cfg
        ):
    '''
    상위 생성 작업에서 모드를 계승받아 판단하au, 해당 모드에 맞는 후처리 작업을
    ControlNet, IP-Adapter의 방식으로 처리.

    Args:
        - mode: 생성 작업에서의 모드를 계승
        - image: 제품 이미지
        - mask: 전 단계에서 만든 마스크 이미지 (있다면)
        - gen_img: 후처리가 필요한 생성이미지 (제품과의 합성 or 구도, 스타일 수정)
    '''
    pass


if __name__ == "__main__":
    MODE = 'inpaint'
    run_pipe(mode=MODE)
