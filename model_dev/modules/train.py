import os, csv, shutil, gc, subprocess
from PIL import Image
import torch
import torchvision.transforms as T
from transformers import BlipProcessor, BlipForConditionalGeneration
import argparse
from modules.utils import resize_with_padding

# 1. 폴더 초기화 함수
def delete_folder(folder):
    '''학습이 끝난 뒤 이미지 증강과 학습에 사용된 폴더 (예:'./aug') 제거'''
    if os.path.exists(folder):
        shutil.rmtree(folder)
 
def get_images(dir_path, prefix=None):
    '''경로 내부 탐색, prefix로 해당 이미지만 가져온다.'''
    return [f for f in os.listdir(dir_path)
            if (prefix is None or prefix in f) and f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]

# 3. BLIP 캡션 생성 함수
def generate_caption(image_path, processor, model, device="cuda"):
    '''불러온 이미지의 captioning을 자동화'''
    image = resize_with_padding(Image.open(image_path))
    inputs = processor(image, return_tensors="pt").to(device)
    ids = model.generate(**inputs, max_new_tokens=50, num_beams=5, early_stopping=True)
    return processor.decode(ids[0], skip_special_tokens=True)

# 4. 증강 및 CSV 작성 함수
def create_augmented_dataset(image_dir, output_dir, csv_path, category_token, prefix, processor, model, num_aug=5, device="cuda"):
    '''
    1. 위의 방식으로 불러온 이미지에 captioning을 진행
    2. augmentation으로 이미지 증강 및 데이터량 증폭 (caption은 원본과 증강이미지가 같도록 유지)
    3. 해당이미지의 경로를 file_name으로 해당되는 caption을 caption column으로 매핑
    4. csv 저장
    '''
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)

    with open(csv_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["file_name", "caption"])
        for fname in get_images(image_dir, prefix):
            img_path = os.path.join(image_dir, fname)
            token = f"{category_token}_0 {category_token}_1"
            caption = generate_caption(img_path, processor, model, device=device)
            full_caption = f"a photo of {token} {caption}"
            print(f"[📝] {fname} -> {full_caption}")

            img = Image.open(img_path)
            if img.size[0] < 512 or img.size[1] < 512:
                img = resize_with_padding(img)

            transform = T.Compose([
                T.RandomRotation(20),
                T.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3)
            ])

            for i in range(num_aug):
                aug_img = transform(img)
                if aug_img.mode == "RGBA":
                    aug_img = aug_img.convert("RGB")
                save_name = f"{os.path.splitext(fname)[0]}_aug_{i}.jpg"
                save_path = os.path.join(output_dir, save_name)
                # 파일명 충돌 방지
                idx = i
                while os.path.exists(save_path):
                    idx += 1
                    save_name = f"{os.path.splitext(fname)[0]}_aug_{idx}.jpg"
                    save_path = os.path.join(output_dir, save_name)
                aug_img.save(save_path)
                writer.writerow([save_path, full_caption])
    print(f"[✅] CSV 저장 완료: {csv_path}")

# 5. 학습 명령어 실행 함수
def train_lora(module_path, image_id, csv_dir, train_epochs=10, base_model="../std_v1.5_cdp", accumulation_steps=None, resume=False):
    '''
    학습 트리거
    
    Args:
        - 
    '''
    
    # inpaint 모델의 경우 checkpoint 저장 경로 변경
    save_dir = f"inp_{image_id}" if "inp" in base_model else image_id
    output_dir = os.path.join(os.path.dirname(base_model), f"output_models/{save_dir}")

    # warm_up step, epoch에 따라 동적 계산, resume의 경우 0부터 시작이 아닌 멈췄던 step 부터 시작이므로, 
    # 추가 학습의 경우 기본 20 epochs으로 설정
    warm_steps = estimate_warmup_steps(
            csv_path='model_dev/aug/captions.csv',
            batch_size=2, 
            accumulation_steps=accumulation_steps or 1,
            num_epochs=train_epochs if not resume else 20
            )
    
    command = [
        "accelerate", "launch", module_path,
        "--pretrained_model_name_or_path", base_model,
        "--dataset_name", "csv",
        "--dataset_config_name", csv_dir,
        "--image_column", "file_name",
        "--caption_column", "caption",
        "--instance_prompt", f"a photo of {image_id}_0 {image_id}_1 perfume bottle",  # 학습된 특수 토큰 방식으로 넣기 (단, 기본 프롬프트는 json 의 형태로 학습되며 이건 특)
        "--resolution", "512",
        "--train_batch_size", "2",
        "--num_train_epochs", str(train_epochs),
        "--output_dir", output_dir,
        "--validation_prompt", f"a photo of {image_id}_0 {image_id}_1 perfume bottle",
        "--rank", "2",
        "--lora_dropout", "0.3",
        "--learning_rate", "2e-5",
        "--lr_scheduler", "cosine_with_restarts",
        "--warmup_steps", str(warm_steps),
        "--checkpointing_steps", "100",
        "--validation_epochs", "5",
        "--mixed_precision", "fp16" if not resume else "no",
        "--max_grad_norm", "1.0",
        "--report_to", "wandb",
    ]

    if resume:
        command += ["--resume_from_checkpoint", "latest"]
    if accumulation_steps:
        command += ["--gradient_accumulation_steps", str(accumulation_steps)]

    print("[🚀] 학습 시작...")
    result = subprocess.run(command)
    if result.returncode == 0:
        print(f"[✅] 학습 완료: {output_dir}")
    else:
        print("[❌] 학습 실패")
    return result

def estimate_warmup_steps(csv_path, batch_size, accumulation_steps, num_epochs, ratio=0.03, min_warmup=10):
    with open(csv_path) as f:
        num_images = sum(1 for _ in f) - 1
    total_steps = int((num_images / batch_size / accumulation_steps) * num_epochs)
    return max(min_warmup, int(total_steps * ratio))


# 6. 필요 시 BLIP 모델 및 processor 초기화 함수
def load_blip_model(device="cuda"):
    processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").eval().to(device, torch.float16)
    return processor, model

# 7. main 함수 패턴 적용 예시
def main():
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if not base_path.endswith("model_dev"):
        raise ValueError(f"기본 경로가 맞지 않습니다. {base_path}")

    module_path = os.path.join(os.path.dirname(base_path), "diffusers/examples/advanced_diffusion_training/train_dreambooth_lora_sd15_advanced.py")
    if not os.path.exists(module_path):
        raise ValueError(f"모듈의 경로를 찾을 수 없습니다. {module_path}")
    try:
        if not os.path.exists(base_path):
            raise ValueError(f"기본 경로가 존재하지 않습니다: {base_path}")
        image_dir = os.path.join(base_path, 'images')
        augmented_dir = os.path.join(base_path, 'aug')
        csv_path = os.path.join(augmented_dir, 'captions.csv')
        category_token = 'CDP_COS'
        search_image_prefix="PER"
        device="cuda"
        model_name = ['std_v1.5_cdp', 'std_inpaint_cdp']
        base_model = os.path.join(base_path, model_name[0])
        if not os.path.exists(base_model):
            raise ValueError(f"모델을 찾을수 없습니다. {base_model}")
    except Exception as e:
        raise ValueError(f"경로를 찾을 수 없습니다. {e}")
    
    # 이미지 증강 중복 검열
    delete_folder(augmented_dir)

    # captioning
    processor, model = load_blip_model(device=device)

    # dataset 구성하기
    create_augmented_dataset(
        image_dir=image_dir,
        output_dir=augmented_dir,
        csv_path=csv_path,
        category_token=category_token,
        prefix=search_image_prefix,
        processor=processor,
        model=model,
        num_aug=5,
        device=device,
    )
    # 자원 해제
    del processor, model
    gc.collect()
    torch.cuda.empty_cache()

    # 학습 실행
    result = train_lora(
        module_path=module_path,
        image_id=category_token, 
        csv_dir=csv_path, 
        train_epochs=50, 
        base_model=base_model,
        accumulation_steps=4,
        resume=False
        )
    if result.returncode == 0:
        delete_folder(augmented_dir)

# def parse_args(input_args=None):
#     parser = argparse.ArgumentParser(description="Training Script")
#     parser.add_argument(
#         "--category_token",
#         type=str,
#         default=None,
#         required=False,
#         help=(
#             'The choose between trained speical tokens, ["CDP_FOOD", "CDP_COS", "CDP_FUR"],'
#             'to optimize the generated image from text2img or inpaint with our fine-tuned dreambooth-lora'
#         )
#     )
if __name__ == "__main__":
    main()