from modules.image_utils import encode_image, remove_background, overlay_product, resize_to_ratio, ensure_dir
import os, io, base64
from PIL import Image
from modules.logger import setup_logger

logger = setup_logger(__name__)

def generate_ad_banner(config, gpt_client, pipe):
    logger.info("=== Start: Generating advertisement banner ===")
    # 1) 이미지 base64 인코딩 (resize 포함)
    product_b64 = encode_image(config["paths"]["product_image"], size=tuple(config["image"]["input_size"]))
    ref_b64 = None
    if os.path.exists(config["paths"]["reference_image"]):
        ref_b64 = encode_image(config["paths"]["reference_image"], size=tuple(config["image"]["input_size"]))

    # 2) GPT 광고 기획안 생성
    logger.info("Generating ad plan from GPT")
    ad_plan = gpt_client.analyze_ad_plan(product_b64, ref_b64)
    logger.debug(f"Ad plan:\n{ad_plan}")

    # 3) SD 프롬프트 변환
    logger.info("Converting ad plan to SD prompt")
    sd_prompt = gpt_client.convert_to_sd_prompt(ad_plan)


    # 4) 광고 배경 생성
    logger.info("Generating background image using Stable Diffusion")
    bg_result = pipe(
        prompt=sd_prompt,
        negative_prompt=config["generation"]["negative_prompt"],
        num_inference_steps=config["generation"]["inference_steps"],
        guidance_scale=config["generation"]["guidance_scale"],
        height=config["image"]["output_ratios"]["square"][1],
        width=config["image"]["output_ratios"]["square"][0]
    )
    bg_image = bg_result.images[0]

    bg_image.save("debug_output.png")
    logger.info("Saved debug image: debug_output.png")

    # 5) 빈 그릇 탐지
    logger.info("Analyzing generated background for empty bowl")
    buffered = io.BytesIO()
    bg_image.save(buffered, format="PNG")
    bg_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
    empty_bowl_answer = gpt_client.analyze_empty_bowl(bg_base64)

    # 6) 음식 합성 혹은 IP-Adapter 합성
    # if "empty bowl" in empty_bowl_answer or "no food" in empty_bowl_answer:
    #     product_img = remove_background(config["paths"]["product_image"])
    #     final_img = overlay_product(bg_image, product_img, position=tuple(config["image"]["overlay_position"]))
    # else:
    from ip_adapter import IPAdapter
    ip_adapter = IPAdapter(
        pipe,
        image_encoder_path="laion/CLIP-ViT-H-14-laion2B-s32B-b79K",
        ip_ckpt="ip-adapter_sd15.bin",
        device=config["sd_pipeline"]["device"]
    )
    input_image = Image.open(config["paths"]["product_image"]).convert("RGB").resize(tuple(config["image"]["input_size"]))
    ip_images = ip_adapter.generate(
        pil_image=input_image,
        prompt=sd_prompt,
        negative_prompt=config["generation"]["negative_prompt"],
        scale=0.8,
        num_inference_steps=config["generation"]["inference_steps"],
        guidance_scale=config["generation"]["guidance_scale"]
    )
    final_img = ip_images[0]

    # 7) 출력 디렉토리 준비
    ensure_dir(config["paths"]["output_dir"])

    # 8) 비율별 이미지 저장
    for ratio_name, size in config["image"]["output_ratios"].items():
        resized = resize_to_ratio(final_img, tuple(size))
        save_path = os.path.join(config["paths"]["output_dir"], f"final_{ratio_name}.png")
        resized.save(save_path)
        print(f"[INFO] Saved {ratio_name} banner: {save_path}")

    return final_img
