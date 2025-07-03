# /rag_pipeline/image_generation/generator.py.
import accelerate, torch
from diffusers import StableDiffusionPipeline
from typing import List
from PIL import Image

def generate_image(pipeline, prompt: str, negative_prompt: str, accelerator: accelerate.Accelerator, width: int = 1024, height: int = 1024) -> List[Image.Image]:
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
        num_images_per_prompt = 1,
        generator = generator,
        output_type = "pil",
    )
    return results.images
