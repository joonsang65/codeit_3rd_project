import torch
import os
from diffusers import AutoPipelineForText2Image
from modules.logger import setup_logger

logger = setup_logger(__name__)

def load_pipe_with_loras(config, category: str):
    """
    지정된 카테고리에 따라 LoRA 어댑터를 적용한 Stable Diffusion 파이프라인을 로드합니다.

    Args:
        config (dict): 설정 값을 담은 딕셔너리 (config.yaml 파싱 결과).
        category (str): 적용할 LoRA 카테고리 이름 (예: "food", "cosmetics" 등).

    Returns:
        diffusers.StableDiffusionPipeline: LoRA가 적용된 텍스트-투-이미지 파이프라인 객체.
    """
    logger.info(f"Loading pipeline with category: {category}")
    pipe = AutoPipelineForText2Image.from_pretrained(
        config["sd_pipeline"]["model_id"],
        torch_dtype=getattr(torch, config["sd_pipeline"]["torch_dtype"]),
        variant="fp16" if config["sd_pipeline"]["torch_dtype"] == "float16" else None,
    ).to(config["sd_pipeline"]["device"])

    if category:
        lora_dir = config['paths']['lora_dir']
        lora_items = config['lora']['category_map'].get(category, 'furniture')

        logger.info(f"Applying LoRAs: {[l['name'] for l in lora_items]}")

        adapter_names = []
        adapter_weights = []

        for lora in lora_items:
            lora_name = lora['name']
            scale = lora.get('scale', 1.0)
            adapter_name = lora_name

            # lora_path = os.path.join(lora_dir, f"{lora_name}.safetensors")

            pipe.load_lora_weights(
                pretrained_model_name_or_path_or_dict=lora_dir,
                weight_name=f"{lora_name}.safetensors",
                adapter_name=adapter_name
            )

            adapter_names.append(adapter_name)
            adapter_weights.append(scale)

        pipe.set_adapters(adapter_names, adapter_weights)
    else:
        logger.warning("No LoRA category specified. Using base model only.")

    return pipe
