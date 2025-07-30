# Inpainting-Specific Training with DreamBooth + LoRA

## Overview

This project implements a **DreamBooth + LoRA training pipeline optimized for product-centered inpainting**.  
By introducing **category-specific special tokens**, the model learns to generate appropriate backgrounds tailored to different product types.  
Even with a **small dataset**, this approach enables **high-quality outpainting** results.

---

## Dataset Structure

The dataset is stored in CSV format with the following fields:

| Column     | Description                                                                 |
|------------|-----------------------------------------------------------------------------|
| `input`    | Randomly cropped product image (center portion retained)                    |
| `mask`     | Inverted binary mask indicating which regions to inpaint (white = restore)  |
| `output`   | Full original image including product and background                        |
| `prompt`   | Descriptive caption of the original image                                   |
| `category` | Product category (e.g., `CDP_COS`, `CDP_FOOD`, etc.)                         |

---

## Training Strategy

- **Model**: [`StableDiffusionInpaintPipeline`](https://huggingface.co/runwayml/stable-diffusion-inpainting)

- **Trainable Components**:
  - `UNet` (for masked latent denoising)
  - `CLIPTextEncoder` (for prompt conditioning)  
  → Both components are wrapped with **LoRA**

- **Prompt Formatting with Special Tokens**:  
  Custom tokens are added to the tokenizer to represent product categories. Prompts during training are formatted as:
  ```text
  {special_token} background, {original_prompt}
  Example: CDP_COS background, elegant cosmetic product on glass table
  ```

- **Learning Objectives**:
- `UNet`: Learns to restore noise within the masked latent region
- `TextEncoder`: Learns to interpret category-aware prompts for better conditioning

---

## Purpose & Goals

- **Category-specific background generation**  
Enable distinct background generation styles for each product type (e.g., cosmetics, food)

- **Efficient learning from small datasets**  
Leverage data augmentation and special tokens to generalize well from limited samples

- **Lightweight deployment with LoRA**  
Export LoRA weights per category for easy integration into:
- Diffusers pipelines  
- ONNX inference environments  
- API-based services

---

## Project Structure Assumptions

- Training scripts are expected to run inside the `notebooks/` directory
- CSV files and image resources should be located relative to that path

---
