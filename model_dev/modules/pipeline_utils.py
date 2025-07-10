import torch
from diffusers import AutoPipelineForText2Image, StableDiffusionInpaintPipeline
from typing import Dict, Literal
import logging
from modules.utils import log_execution_time, setup_logger

import logging

logger = setup_logger(__name__, logging.DEBUG)

@log_execution_time(label="Load Stable Diffution Pipeline...")
def load_base_pipe(
    config: Dict,
    pipeline_type: Literal["inpaint", "text2img"] = "inpaint"
):
    """
    설정에 따라 Stable Diffusion 파이프라인을 로드합니다.

    Args:
        config (dict): 구성 설정
        pipeline_type (str): 'inpaint' 또는 'text2img'

    Returns:
        diffusers pipeline object
    """
    logger.info(f"Loading base pipeline: {pipeline_type}")

    if pipeline_type == "inpaint":
        pipe_cls = StableDiffusionInpaintPipeline
    elif pipeline_type == "text2img":
        pipe_cls = AutoPipelineForText2Image
    else:
        raise ValueError(f"Unsupported pipeline_type: {pipeline_type}")

    model_id = config["sd_pipeline"][pipeline_type]["model_id"]
    torch_dtype = getattr(torch, config["sd_pipeline"]["torch_dtype"])
    variant = "fp16" if config["sd_pipeline"]["torch_dtype"] == "float16" else None

    pipe = pipe_cls.from_pretrained(
        model_id,
        torch_dtype=torch_dtype,
        variant=variant,
        use_safetensors=True
    ).to(config["sd_pipeline"]["device"])

    logger.info("Pipeline loaded successfully.")
    return pipe

@log_execution_time(label="Applying LoRA Layers...")
def apply_loras(pipe, config, category=None):
    """Stable Diffusion 파이프라인에 category에 맞는 LoRA 적용하기"""
    if not category:
        if logger:
            logger.warning("No LoRA category specified. Using base model only.")
        return pipe

    lora_dir = config['paths']['lora_dir']
    category_map = config['lora']['category_map']

    lora_items = category_map.get(category, 'furniture') # 기본 furniture lora 적용
    
    logger.info(f"Applying LoRAs for category '{category}': {[l['name'] for l in lora_items]}")

    adapter_names, adapter_weights = [], []

    for lora in lora_items:
        name = lora["name"]
        scale = lora.get("scale", 1.0)
        try:
            pipe.load_lora_weights(
                pretrained_model_name_or_path_or_dict=lora_dir,
                weight_name=f"{name}.safetensors",
                adapter_name=name
            )
            adapter_names.append(name)
            adapter_weights.append(scale)
        except Exception as e:
            logger.error(f"Failed to load LoRA '{name}': {e}")

    if adapter_names:
        pipe.set_adapters(adapter_names, adapter_weights)
    logger.debug(pipe.unet.active_adapters)
    return pipe

def load_pipe_with_loras(
    config: Dict,
    category: str,
    pipeline_type: Literal["text2img", "inpaint"] = "inpaint"
):
    """
    지정한 파이프라인을 로드하고, 해당 카테고리의 LoRA를 적용합니다.
    """
    pipe = load_base_pipe(config, pipeline_type)
    return apply_loras(pipe, config, category)

@log_execution_time(label="Load IP-Adapter...")
def load_ip_adapter(pipe, config: Dict):
    """
    IP-Adapter를 로드하고 pipe에 연결합니다.

    Args:
        pipe: Stable Diffusion pipeline 객체
        config: 설정 딕셔너리
    
    Returns:
        IPAdapter 객체
    """
    from ip_adapter import IPAdapter
    checkpoint = config["ip_adapter"]["checkpoint"]
    import os
    if os.path.exists(checkpoint):
        pass
    else:
        checkpoint = "model_dev/" + checkpoint
    ip_adapter = IPAdapter(
        pipe,
        image_encoder_path=config["ip_adapter"]["image_encoder"],
        ip_ckpt=checkpoint,
        device=config["sd_pipeline"]["device"]
    )

    logger.info(f"IP-Adapter loaded: {checkpoint}")
    return ip_adapter