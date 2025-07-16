import torch
from diffusers import (
    StableDiffusionPipeline,
    StableDiffusionInpaintPipeline,
    StableDiffusionControlNetPipeline,
    StableDiffusionControlNetInpaintPipeline,
    ControlNetModel,
)
from typing import Dict, Literal
import logging
from modules.utils import log_execution_time, logger

# Mapping 정의
PIPELINE_CLASSES = {
    "text2img": StableDiffusionPipeline,
    "inpaint": StableDiffusionInpaintPipeline,
    "controlnet": StableDiffusionControlNetPipeline,
    "controlnet_inpaint": StableDiffusionControlNetInpaintPipeline,
}

CONTROLNET_MODEL_MAP = {
    "canny": "lllyasviel/sd-controlnet-canny",
    "depth": "lllyasviel/sd-controlnet-depth",
    "mlsd": "lllyasviel/sd-controlnet-mlsd",
    "hed": "lllyasviel/sd-controlnet-hed",
    "openpose": "lllyasviel/sd-controlnet-openpose",
}

@log_execution_time(label="Load ControlNets")
def load_controlnets(config, names: list[str], dtype=torch.float16, device="cuda"):
    '''controlnet을 로드한다. names인자에 여러 조건이 들어올경우 다중으로 controlnet을 로드한다.'''
    controlnets = []
    for name in names:
        if name not in CONTROLNET_MODEL_MAP:
            raise ValueError(f"[ControlNet] '{name}'은 지원되지 않는 타입입니다.")
        model_id = CONTROLNET_MODEL_MAP[name]
        controlnet = ControlNetModel.from_pretrained(model_id, torch_dtype=dtype).to(device)
        controlnets.append(controlnet)
    return controlnets

@log_execution_time(label="Create SD Pipeline")
def create_pipeline(cls, model_id, device="cuda", torch_dtype=torch.float16, controlnet=None):
    '''설정값에 맞는 파이프라인을 로드하며, 해당 파이프라인에 맞는 인자를 설정한다.'''
    variant = "fp16" if torch_dtype == torch.float16 else None
    if controlnet:
        return cls.from_pretrained(
            model_id,
            controlnet=controlnet,
            torch_dtype=torch_dtype,
            variant=variant,
            use_safetensors=True
        ).to(device)
    return cls.from_pretrained(
        model_id,
        torch_dtype=torch_dtype,
        variant=variant,
        use_safetensors=True
    ).to(device)

@log_execution_time(label="Load SD Pipeline by Type")
def load_pipeline_by_type(config: Dict, pipeline_type: str, controlnet_types: list[str] = None):
    '''
    파이프라인을 type에 맞게 로드하며, controlnet계열의 경우 적용하려는 controlnet type을 리스트로 주어져야한다.

    Args:
        - config: 설정값
        - pipeline_type: ['text2img', 'inpaint', 'controlnet', 'controlnet_inpaint] 중 하나.
        - controlnet_types: ['canny', 'depth', 'mlsd', 'hed', 'openpose'] 중 선택 가능 또한 다중으로 적용이 가능하다.
    
    Returns:
        Stable Diffusion pipeline
    '''
    model_id = config["sd_pipeline"].get(pipeline_type, {}).get("model_id")
    torch_dtype = getattr(torch, config["sd_pipeline"].get("torch_dtype", "float16"))
    device = config["sd_pipeline"].get("device", "cuda")

    pipe_cls = PIPELINE_CLASSES.get(pipeline_type)
    if pipe_cls is None:
        raise ValueError(f"Unsupported pipeline_type: {pipeline_type}, Choose from {list(PIPELINE_CLASSES.keys())}")

    controlnet = None
    if "controlnet" in pipeline_type:
        types = controlnet_types or config.get("controlnet", {}).get("types", ["canny"])
        controlnet = load_controlnets(config, types, dtype=torch_dtype, device=device)

    return create_pipeline(pipe_cls, model_id, device, torch_dtype, controlnet)

@log_execution_time(label="Load All Pipelines")
def load_pipelines(config):
    '''현재 설정된 네가지 파이프라인 모두를 로드한다.'''
    pipelines = {}
    for pipe_type in PIPELINE_CLASSES.keys():
        try:
            pipelines[pipe_type] = load_pipeline_by_type(config, pipe_type)
        except Exception as e:
            logger.warning(f"Failed to load pipeline '{pipe_type}': {e}")
    return pipelines

@log_execution_time(label="Apply LoRA Layers")
def apply_loras(pipe, config, category=None):
    '''저장된 LoRA를 카테고리에 맞게 추적하여 로드한다.'''
    if not category:
        logger.warning("No LoRA category specified. Using base model only.")
        return pipe

    lora_dir = config['paths']['lora_dir']
    category_map = config['lora']['category_map']
    lora_items = category_map.get(category, 'furniture')

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
    return pipe

@log_execution_time(label="Load IP-Adapter")
def load_ip_adapter(pipe, config: Dict):
    '''ip_adapter를 초기화 한다.'''
    from ip_adapter import IPAdapter
    import os

    checkpoint = config["ip_adapter"].get("checkpoint")
    if not os.path.exists(checkpoint):
        checkpoint = os.path.join("model_dev", checkpoint)

    ip_adapter = IPAdapter(
        pipe,
        image_encoder_path=config["ip_adapter"]["image_encoder"],
        ip_ckpt=checkpoint,
        device=config["sd_pipeline"].get("device", "cuda")
    )

    logger.info(f"IP-Adapter loaded: {checkpoint}")
    return ip_adapter

@log_execution_time(label="Load Pipe with LoRAs")
def load_pipe_with_loras(config: Dict, category: str, pipeline_type: str = "inpaint"):
    '''pipeline을 로드할떄 lora를 적용한다.'''
    pipe = load_pipeline_by_type(config, pipeline_type)
    return apply_loras(pipe, config, category)