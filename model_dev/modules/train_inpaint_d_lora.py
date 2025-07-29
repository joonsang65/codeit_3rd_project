import os
from pathlib import Path
import pandas as pd
from PIL import Image, ImageOps
from tqdm import tqdm

import torch
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from torch.nn.functional import mse_loss
import torchvision.transforms as transforms
from torchvision.utils import save_image

from diffusers import StableDiffusionInpaintPipeline, DDIMScheduler
from peft import LoraConfig, get_peft_model
from accelerate import Accelerator
import piq

# -------------------- Config --------------------
CFG = {
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "special_tokens": ["CDP_COS"],
    "csv_path": "CDP_COS_dataset.csv",
    "image_size": 512,
    "batch_size": 4,
    "num_epochs": 50,
    "learning_rate": 1e-6,
    "grad_accum_steps": 2,
    "num_inference_steps": 35,
    "save_every": 50,
    "output_dir": "outputs/"
}

os.makedirs(CFG["output_dir"], exist_ok=True)

# -------------------- Dataset --------------------
class DreamBoothDataset(Dataset):
    def __init__(self, csv_path, size=512, center_crop=False):
        self.df = pd.read_csv(csv_path)
        self.size = size
        interpolation = transforms.InterpolationMode.BICUBIC
        crop = transforms.CenterCrop(size) if center_crop else transforms.RandomCrop(size)

        self.image_tf = transforms.Compose([
            transforms.Resize(size, interpolation=interpolation),
            crop,
            transforms.ToTensor(),
            transforms.Normalize([0.5], [0.5]),
        ])
        self.mask_tf = transforms.Compose([
            transforms.Resize(size, interpolation=interpolation),
            crop,
            transforms.ToTensor(),
        ])

    def __len__(self):
        return len(self.df)

    def __getitem__(self, idx):
        import numpy as np
        row = self.df.loc[idx]
        input_img = np.array(Image.open(row['input']).convert("RGB"))
        # 2. 검정 픽셀 마스크 생성 (모든 채널이 0일 때)
        black_pixels = np.all(input_img[:, :, :3] == 0, axis=-1)

        # 3. 해당 픽셀을 흰색으로 변경
        input_img[black_pixels] = [255, 255, 255]

        # 4. 다시 PIL 이미지로 변환
        input_img = Image.fromarray(input_img)
        mask_img = ImageOps.invert(Image.open(row['mask']).convert("L"))
        output_img = Image.open(row['output']).convert("RGB")
        prompt = f"{row['category']} background, {row['prompt']}"

        return {
            "input_images": self.image_tf(input_img),
            "mask_images": (self.mask_tf(mask_img) > 0.5).float(),
            "output_images": self.image_tf(output_img),
            "instance_prompt": prompt,
        }

# -------------------- Utils --------------------
def print_param_stats(model, name):
    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"{name}: {trainable}/{total} trainable")

def decode_latents(vae, latents, scale):
    with torch.no_grad():
        return vae.decode(latents / scale).sample

def evaluate_and_log(pred, target, step):
    pred = (pred / 2 + 0.5).clamp(0, 1)
    target = (target / 2 + 0.5).clamp(0, 1)
    psnr = piq.psnr(pred, target, data_range=1.).item()
    ssim = piq.ssim(pred, target, data_range=1.).item()
    print(f"Step {step} - PSNR: {psnr:.4f}, SSIM: {ssim:.4f}")
    save_image(pred, os.path.join(CFG["output_dir"], f"pred_{step}.png"))
    return psnr
# -------------------- Main --------------------
def main():
    # Load pipeline
    pipe = StableDiffusionInpaintPipeline.from_pretrained("runwayml/stable-diffusion-inpainting", torch_dtype=torch.float32).to(CFG["device"])
    pipe.scheduler = DDIMScheduler.from_config(pipe.scheduler.config)
    scale = getattr(pipe, 'vae_scaling_factor', 0.18215)

    # Freeze
    pipe.unet.requires_grad_(False)
    pipe.text_encoder.requires_grad_(False)
    pipe.vae.requires_grad_(False)

    # Add special tokens
    pipe.tokenizer.add_tokens(CFG["special_tokens"], special_tokens=True)
    pipe.text_encoder.resize_token_embeddings(len(pipe.tokenizer))

    # Inject LoRA
    lora_cfg = dict(r=8, lora_alpha=16, lora_dropout=0.1, bias="none", inference_mode=False)
    pipe.text_encoder = get_peft_model(pipe.text_encoder, LoraConfig(target_modules=["q_proj", "k_proj", "v_proj", "out_proj"], **lora_cfg))
    pipe.unet = get_peft_model(pipe.unet, LoraConfig(target_modules=["to_q", "to_k", "to_v", "to_out.0"], **lora_cfg))

    print_param_stats(pipe.text_encoder, "TextEncoder")
    print_param_stats(pipe.unet, "UNet")

    # Dataset / Dataloader
    dataset = DreamBoothDataset(CFG["csv_path"], size=CFG["image_size"])
    dataloader = DataLoader(dataset, batch_size=CFG["batch_size"], shuffle=True, num_workers=4)

    # Optimizer
    optimizer = AdamW(list(pipe.unet.parameters()) + list(pipe.text_encoder.parameters()), lr=CFG["learning_rate"], weight_decay=1e-4)

    # Scheduler & Accelerator
    pipe.scheduler.set_timesteps(CFG["num_inference_steps"])
    accelerator = Accelerator()
    unet, text_encoder, optimizer, dataloader = accelerator.prepare(pipe.unet, pipe.text_encoder, optimizer, dataloader)

    vae = pipe.vae.to(CFG["device"]).half().eval()
    unet.train()
    text_encoder.train()

    global_step = 0
    for epoch in range(CFG["num_epochs"]):
        for batch in tqdm(dataloader, desc=f"Epoch {epoch+1}"):
            global_step += 1
            with accelerator.accumulate(unet):
                inputs = {k: v.to(accelerator.device, dtype=torch.float16) for k, v in batch.items() if torch.is_tensor(v)}

                tokens = pipe.tokenizer(batch["instance_prompt"], padding="max_length", truncation=True, return_tensors="pt").to(accelerator.device)
                embeds = text_encoder(input_ids=tokens.input_ids, attention_mask=tokens.attention_mask).last_hidden_state

                with torch.no_grad():
                    latents = vae.encode(inputs["input_images"]).latent_dist.sample() * scale

                noise = torch.randn_like(latents)
                t = torch.randint(0, pipe.scheduler.config.num_train_timesteps, (latents.shape[0],), device=latents.device).long()
                noisy_latents = pipe.scheduler.add_noise(latents, noise, t)

                mask = torch.nn.functional.interpolate(inputs["mask_images"], size=latents.shape[-2:], mode="nearest")
                masked_latents = noisy_latents * (1 - mask)

                # 모델 추론 (diffusers 스타일)
                noise_pred = unet(
                    noisy_latents,
                    t,
                    encoder_hidden_states=embeds,
                    added_cond_kwargs={"mask": mask, "masked_image_latents": masked_latents},
                ).sample

                loss = mse_loss(noise_pred.float(), noise.float())
                if torch.isnan(loss):
                    print("NaN detected. Skipping step.")
                    continue

                accelerator.backward(loss)
                if global_step % CFG["grad_accum_steps"] == 0:
                    optimizer.step()
                    optimizer.zero_grad()

                # 로그 및 시각화
                if global_step % CFG["save_every"] == 0:
                    with torch.no_grad():
                        pred_latents = torch.cat([
                            pipe.scheduler.step(noise_pred[i:i+1], t[i:i+1], noisy_latents[i:i+1]).prev_sample
                            for i in range(latents.shape[0])
                        ])
                        pred_images = decode_latents(vae, pred_latents, scale)
                        evaluate_and_log(pred_images, inputs["output_images"], global_step)

if __name__ == "__main__":
    main()
