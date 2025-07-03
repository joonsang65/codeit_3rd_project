# /rag_pipeline/image_generation/visual_analyzer.py.
from openai import OpenAI
from PIL import Image
from typing import List
import accelerate, torch

def analyze_image(chat_pipeline, image: Image.Image, accelerator: accelerate.Accelerator) -> str:
    """Analyzes a generated image and provides a description using a chat pipeline."""
    generator = torch.Generator(device = accelerator.device).manual_seed(0)
    results = chat_pipeline(
        prompt = "Please provide a detailed description of this image, focusing on elements, mood, and style that would be useful for writing advertisement copy.",
        input_images = [image],
        generator = generator,
    )
    return results.text
