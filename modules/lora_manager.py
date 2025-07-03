import torch
import os
from diffusers import AutoPipelineForText2Image

def load_pipe_with_loras(config, category: str):
    pipe = AutoPipelineForText2Image.from_pretrained(
        config["sd_pipeline"]["model_id"],
        torch_dtype=getattr(torch, config["sd_pipeline"]["torch_dtype"]),
        variant="fp16" if config["sd_pipeline"]["torch_dtype"] == "float16" else None,
    ).to(config["sd_pipeline"]["device"])

    if category:
        lora_dir = config['paths']['lora_dir']
        lora_items = config['lora']['category_map'].get(category, [])

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

    return pipe
