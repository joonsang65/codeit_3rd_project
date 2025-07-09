
from PIL import Image, ImageOps
from typing import Dict
from model_dev.modules.utils import log_execution_time, setup_logger
import logging

logger = setup_logger(__name__, logging.DEBUG)

@log_execution_time(label="Inpainting process...")
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
        height=config['canvas_size'][1],
        width=config['canvas_size'][0],
        num_images_per_prompt=2
    ).images

@log_execution_time(label="Background image generating...")
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
        height=config['canvas_size'][1],
        width=config['canvas_size'][0],
        num_images_per_prompt=2
    ).images
    if len(result) > 1:
        for i, image in enumerate(result):
            image.save(f"{config['paths']['output_dir']}/debug_output{i}.png")
    else:
        image.save(f"{config['paths']['output_dir']}/debug_output.png")
    logger.debug("Saved debug background: debug_output.png")
    return image

@log_execution_time(label="Inference from IP-Adapter...")
def ip_adapter_inference(ip_adapter, config: Dict, prompt: str, background_image: Image.Image, input_image: Image.Image) -> Image.Image:
    """
    IP-Adapter를 활용해 배경과 제품 이미지를 조화롭게 합성합니다.
    
    Args:
        ip_adapter: IP-Adapter 객체
        config: 설정 딕셔너리
        prompt: 텍스트 프롬프트
        background_image: 배경 이미지 (PIL.Image)
        input_image: 제품 이미지 (PIL.Image) - 배경 제거된 이미지 등 동적 입력 가능
    
    Returns:
        합성된 이미지 (PIL.Image)
    """
    logger.info("Running IP-Adapter fusion")

    ip_images = ip_adapter.generate(
        pil_image=input_image,
        image=background_image,
        prompt=prompt,
        negative_prompt=config["generation"]["negative_prompt"],
        scale=0.7,
        num_inference_steps=config["generation"]["inference_steps"],
        guidance_scale=config["generation"]["guidance_scale"],
        height=config['canvas_size'][1],
        width=config['canvas_size'][0],
    )
    return ip_images