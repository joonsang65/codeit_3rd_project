# modules/ad_generator.py
import os, io, base64
from PIL import Image, ImageOps
from typing import Dict, Tuple, Optional
from modules.image_utils import (
    encode_images, remove_background, overlay_product,
    resize_to_ratio, ensure_dir, create_mask_from_product
)
from modules.logger import setup_logger
import logging

logger = setup_logger(__name__, logging.DEBUG)


def run_inpainting(pipe, original_image: Image.Image, product_mask: Image.Image, prompt: str, config: Dict) -> Image.Image:
    """
    제품을 제외한 배경 영역만 Inpainting으로 리터칭합니다.
    """
    logger.info("Running inpainting with inverted mask")
    return pipe(
        image=original_image.convert("RGB"),
        mask_image=ImageOps.invert(product_mask),
        prompt=prompt,
        num_inference_steps=config["generation"]["inference_steps"],
        guidance_scale=config["generation"]["guidance_scale"],
        num_images_per_prompt=4
    ).images


def generate_background(pipe, prompt: str, config: Dict) -> Image.Image:
    """
    Stable Diffusion을 통해 광고 배경 이미지를 생성합니다.
    """
    logger.info("Generating background image with prompt")
    result = pipe(
        prompt=prompt,
        negative_prompt=config["generation"]["negative_prompt"],
        num_inference_steps=config["generation"]["inference_steps"],
        guidance_scale=config["generation"]["guidance_scale"],
        height=config["image"]["output_ratios"]["square"][1],
        width=config["image"]["output_ratios"]["square"][0]
    )
    image = result.images[0]
    image.save("debug_output.png")
    logger.debug("Saved debug background: debug_output.png")
    return image


def analyze_bowl_presence(gpt_client, image: Image.Image) -> str:
    """
    배경 이미지에 빈 그릇이 있는지 GPT에게 분석 요청.
    """
    logger.info("Analyzing generated background for empty bowl")
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    b64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return gpt_client.analyze_empty_bowl(b64)


def apply_ip_adapter(pipe, config: Dict, prompt: str, background_image: Image.Image) -> Image.Image:
    """
    IP-Adapter를 활용해 배경과 제품 이미지를 조화롭게 합성합니다.
    """
    logger.info("Running IP-Adapter fusion")

    from ip_adapter import IPAdapter
    ip_adapter = IPAdapter(
        pipe,
        image_encoder_path="laion/CLIP-ViT-H-14-laion2B-s32B-b79K",
        ip_ckpt="ip-adapter_sd15.bin",
        device=config["sd_pipeline"]["device"]
    )

    input_image = Image.open(config["paths"]["product_image"]).convert("RGB").resize(
        tuple(config["image"]["input_size"])
    )

    ip_images = ip_adapter.generate(
        pil_image=input_image,
        image=background_image,
        prompt=prompt,
        negative_prompt=config["generation"]["negative_prompt"],
        scale=0.7,
        num_inference_steps=config["generation"]["inference_steps"],
        guidance_scale=config["generation"]["guidance_scale"]
    )
    return ip_images[0]


def save_resized_versions(image: Image.Image, config: Dict) -> None:
    """
    비율별 광고 배너로 리사이징 후 저장.
    """
    ensure_dir(config["paths"]["output_dir"])
    for ratio_name, size in config["image"]["output_ratios"].items():
        resized = resize_to_ratio(image, tuple(size))
        save_path = os.path.join(config["paths"]["output_dir"], f"final_{ratio_name}.png")
        resized.save(save_path)
        logger.info(f"Saved banner: {save_path}")


def generate_ad_banner(config: Dict, gpt_client, pipe) -> Image.Image:
    """
    전체 광고 배너 생성 프로세스를 순차적으로 실행합니다.
    """
    logger.info("=== Start: Generating advertisement banner ===")

    # 1) 이미지 인코딩
    product_b64, ref_b64 = encode_images(config)

    # 2) 광고 기획 생성
    ad_plan = gpt_client.analyze_ad_plan(product_b64, ref_b64, product_type="tour place")
    logger.debug(f"Ad plan:\n{ad_plan}")

    # 3) SD용 영어 프롬프트 변환
    sd_prompt = gpt_client.convert_to_sd_prompt(ad_plan)
    logger.debug(f"Prompt: {sd_prompt}")


    # 4) 배경 이미지 생성
    bg_image = generate_background(pipe, sd_prompt, config)

    # 5) 빈 그릇 여부 분석
    bowl_result = analyze_bowl_presence(gpt_client, bg_image)
    logger.debug(f"BOWL result: {bowl_result}")

    # 6) 제품 이미지 합성 (IP-Adapter 사용)
    final_img = apply_ip_adapter(pipe, config, sd_prompt, bg_image)

    # 7) 리사이즈 및 저장
    save_resized_versions(final_img, config)

    logger.info("✅ Ad banner generation complete.")
    return final_img
