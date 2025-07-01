import os
import base64
import io
from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI
import torch
from diffusers import StableDiffusionPipeline
from rembg import remove
from ip_adapter import IPAdapter

# ---------------환경 설정 및 모델 초기화 -----------------
load_dotenv()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

pipe = StableDiffusionPipeline.from_pretrained(
    "runwayml/stable-diffusion-v1-5",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    safety_checker=None
).to(device)

ip_adapter = IPAdapter(
    pipe,
    image_encoder_path="laion/CLIP-ViT-H-14-laion2B-s32B-b79K",
    ip_ckpt="ip-adapter_sd15.bin",
    device=device
)

api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# ---------------유틸 함수 -----------------
def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

def remove_background(image_path):
    with open(image_path, 'rb') as f:
        input_data = f.read()
    output_data = remove(input_data)
    return Image.open(io.BytesIO(output_data))

# ----------------프롬프트 생성---------------------------------------

def generate_ad_prompt(product_type: str, marketing_context: str = "") -> str:
    '''광고 배경용 기본 프롬프트'''
    base_prompt = (
        f"Create a clean, minimal background for an advertisement promoting {product_type}. "
        f"Use warm tones and leave ample space for text and product placement. "
        f"Design should feel inviting, professional, and suitable for print or digital media."
    )
    if marketing_context:
        base_prompt += f" The ad context: {marketing_context}."
    base_prompt += " Do NOT include the product image or any text in the background."
    return base_prompt

def generate_prompt_from_image(product_image_path: str, product_type: str, marketing_context: str = "", ad_reference_image_path: str = None) -> str:
    '''이미지 기반 배경 프롬프트 생성 (OpenAI GPT 4.1 nano 기반)'''
    try:
        product_base64 = encode_image(product_image_path)
        reference_base64 = encode_image(ad_reference_image_path) if ad_reference_image_path else None

        messages = [
            {
                "role": "system",
                "content": (
                    "Write a prompt to generate a clean background-only image for a product ad.\n"
                    "Focus on mood, setting, and color. Leave space for product placement.\n"
                    "If unclear, create a soft, neutral, object-free background.\n"
                )
                            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": generate_ad_prompt(product_type, marketing_context)},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{product_base64}"}},
                ] + ([{ "type": "image_url", "image_url": {"url": f"data:image/png;base64,{reference_base64}" }}] if reference_base64 else [])
            }
        ]

        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=messages,
            max_tokens=300
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        raise RuntimeError(f"프롬프트 생성 실패: {e}")

def generate_korean_ad_copy(product_type: str) -> str:
    '''한국어 광고 문구 생성 (OpenAI GPT 활용)'''
    try:
        messages = [
            {
                "role": "system",
                "content": (
                    "당신은 한국어 광고 문구를 작성하는 카피라이터입니다."
                    "사용자가 지정한 제품의 종류에 따라 소상공인이 사용할 수 있는 짧고 임팩트 있는 광고 문구를 한 문장으로 작성하세요."
                    "너무 일반적이거나 진부하지 않게, 제품의 장점을 부각하는 형태로 작성해 주세요."
                )
            },
            {
                "role": "user",
                "content": f"'{product_type}' 제품을 위한 한국어 광고 문구를 작성해줘."
            }
        ]

        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=messages,
            max_tokens=100
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        raise RuntimeError(f"광고 문구 생성 실패: {e}")

def generate_background(prompt: str, output_path: str = None) -> Image.Image:
    '''배경 이미지 생성 (Stable Diffusion)'''
    try:
        result = pipe(prompt=prompt, negative_prompt="text, letters, watermark, products, logo, blurry, low quality")
        image = result.images[0]
        if output_path:
            image.save(output_path)
        return image
    except Exception as e:
        raise RuntimeError(f"배경 이미지 생성 실패: {e}")

def create_ad_background(
    product_img_path: str,
    product_type: str,
    marketing_context: str = "",
    reference_img_path: str = None,
    save_path: str = None
) -> dict:
    '''광고 배경 + 카피 통합 생성'''
    try:
        product_img = remove_background(product_img_path)
        temp_product_path = "temp_removed.png"
        product_img.save(temp_product_path)

        prompt = generate_prompt_from_image(temp_product_path, product_type, marketing_context, reference_img_path)
        background_img = generate_background(prompt, output_path=save_path)
        ad_copy = generate_korean_ad_copy(product_type)

        return {
            "prompt": prompt,
            "background_image": background_img,
            "ad_copy_ko": ad_copy
        }

    except Exception as e:
        return {"error": str(e)}

def create_ad_with_ip_adapter(
    user_img_path: str,
    product_type: str,
    marketing_context: str
) -> Image.Image:
    '''IP Adapter 기반 광고 이미지 생성'''
    prompt = (
        f"An advertisement banner for {product_type}. "
        f"The ad is intended for: {marketing_context}. "
        f"Use the uploaded image as main visual. Place it centered, add space for text above. "
        f"Clean, modern design with a focus on warmth and local charm."
    )
    negative_prompt = (
        "blurry, distorted, watermark, low quality, overexposed"
    )

    ref_img = Image.open(user_img_path).convert("RGB")
    return ip_adapter.generate(
        prompt=prompt,
        pil_image=ref_img,
        negative_prompt=negative_prompt,
        scale=0.6,
        guidance_scale=9
    )


def create_ad(
    user_img_path: str,
    product_type: str,
    marketing_context: str,
    mode: str = "background"  # or "ip_adapter"
):
    '''통합 호출 함수'''
    if mode == "background":
        return create_ad_background(
            product_img_path=user_img_path,
            product_type=product_type,
            marketing_context=marketing_context
        )
    elif mode == "ip_adapter":
        return {
            "generated_image": create_ad_with_ip_adapter(
                user_img_path, product_type, marketing_context
            )
        }