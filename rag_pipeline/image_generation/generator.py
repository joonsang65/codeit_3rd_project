# /rag_pipeline/image_generation/generator.py.
import accelerate, torch
from diffusers import StableDiffusionPipeline
from typing import List
from PIL import Image
# 호스트 경로.
from rag_pipeline.utils.timing_utils import timing_decorator

@timing_decorator
def generate_image(pipeline, prompt: str, negative_prompt: str, accelerator: accelerate.Accelerator, width: int = 1024, height: int = 1024, num_images: int = 1) -> List[Image.Image]:
    """Generates an image using the provided pipeline and prompts."""
    generator = torch.Generator(device = accelerator.device).manual_seed(0)
    results = pipeline(
        prompt = prompt,
        input_images = [], # Assuming text-to-image for now.
        width = width,
        height = height,
        num_inference_steps = 50,
        max_sequence_length = 1024,
        text_guidance_scale = 4.0,
        image_guidance_scale = 1.0,
        negative_prompt = negative_prompt,
        num_images_per_prompt = num_images,
        generator = generator,
        output_type = "pil",
    )
    return results.images
