import os
from pathlib import Path
import pandas as pd
from PIL import Image, ImageOps
from tqdm import tqdm

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from torch.nn.functional import mse_loss
import torchvision.transforms as transforms
from torchvision.utils import save_image

from torch.optim.lr_scheduler import ReduceLROnPlateau
from diffusers import StableDiffusionInpaintPipeline, DDIMScheduler
from peft import LoraConfig, get_peft_model
from accelerate import Accelerator
import wandb
import piq

# -------------------- Config --------------------
category = "CDP_COS"
CFG = {
    "device": "cuda" if torch.cuda.is_available() else "cpu",
    "special_tokens": [category],
    "csv_path": f"{category}_dataset.csv",
    "image_path": f"notebooks",
    "image_size": 512,
    "batch_size": 2,
    "num_epochs": 25,
    "learning_rate": 5e-5,
    "grad_accum_steps": 1,
    "num_inference_steps": 35,
    "save_every": 30,
    "output_dir": f"outputs/{category}"
}

base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

if not os.path.exists(CFG["csv_path"]):
    csv_path = os.path.join(base_path, f'notebooks/{CFG["csv_path"]}')
    CFG["csv_path"] = csv_path

output_path = os.path.join(base_path, CFG["output_dir"])
CFG['output_dir'] = output_path
os.makedirs(CFG['output_dir'], exist_ok=True)

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
        image_path = os.path.join(base_path, CFG['image_path'])
        input_path = os.path.join(image_path, row['input'])
        mask_path = os.path.join(image_path, row['mask'])
        output_path = os.path.join(image_path, row['output'])
        input_img = np.array(Image.open(input_path).convert("RGB"))
        # 검정 픽셀 마스크 생성 (모든 채널이 0일 때)
        black_pixels = np.all(input_img[:, :, :3] == 0, axis=-1)

        # 해당 픽셀을 흰색으로 변경
        input_img[black_pixels] = [255, 255, 255]

        # 다시 PIL 이미지로 변환
        input_img = Image.fromarray(input_img)
        mask_img = ImageOps.invert(Image.open(mask_path).convert("L"))
        output_img = Image.open(output_path).convert("RGB")
        prompt = f"{row['category']} background, {row['prompt']}"

        return {
            "input_images": self.image_tf(input_img),
            "mask_images": (self.mask_tf(mask_img) > 0.5).float(),
            "output_images": self.image_tf(output_img),
            "instance_prompt": prompt,
        }
# ---------------------Wrapper--------------------
class InpaintUNetWrapper(nn.Module):
    def __init__(self, unet):
        super().__init__()
        self.unet = unet
        self.config = unet.base_model.model.config

    def forward(self, sample, timestep, encoder_hidden_states=None, added_cond_kwargs=None, **kwargs):
        if added_cond_kwargs is not None:
            mask = added_cond_kwargs.get("mask")
            masked_latents = added_cond_kwargs.get("masked_image_latents")
            sample = torch.cat([sample, mask, masked_latents], dim=1) 
        return self.unet(sample, timestep, encoder_hidden_states=encoder_hidden_states, **kwargs)
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
def main(outpaint:bool = True, debug:bool = True):
    # Load pipeline (float32 for stablize traini,g loss)
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
    lora_cfg = dict(r=4, lora_alpha=8, lora_dropout=0.1, bias="none", inference_mode=False)
    pipe.text_encoder = get_peft_model(pipe.text_encoder, LoraConfig(target_modules=["q_proj", "k_proj", "v_proj", "out_proj"], **lora_cfg))
    pipe.unet = get_peft_model(pipe.unet, LoraConfig(target_modules=["to_q", "to_k", "to_v", "to_out.0"], **lora_cfg))
    pipe.unet = InpaintUNetWrapper(pipe.unet)
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
    lr_scheduler = ReduceLROnPlateau(optimizer, mode='max', factor=0.5, patience=3, threshold=0.1)

    vae = pipe.vae.to(CFG["device"]).eval()
    unet.train()
    text_encoder.train()

    wandb.init(project="StableDiffusion", name="train_inpaint_lora", mode="online")
    wandb.config.update(CFG)

    best_psnr = 0
    best_step = 0
    save_dir = CFG["output_dir"]
    os.makedirs(save_dir, exist_ok=True)
    global_step = 0
    no_improve_counter = 0
    psnr = None
    epochs = CFG["num_epochs"]
    from torchvision.utils import save_image

    for epoch in range(epochs):
        pbar = tqdm(dataloader, desc=f"Epoch {epoch+1}/{epochs}")
        for batch in pbar:
            global_step += 1
            with accelerator.accumulate(unet):
                inputs = {k: v.to(accelerator.device, dtype=torch.float32) for k, v in batch.items() if torch.is_tensor(v)}
                tokens_pos  = pipe.tokenizer(batch["instance_prompt"], padding="max_length", truncation=True, return_tensors="pt").to(accelerator.device)

                negative_prompt = "logo, text, watermark, blurry, extra fingers, human"
                tokens_neg = pipe.tokenizer([negative_prompt] * len(batch["instance_prompt"]), padding="max_length", truncation=True, return_tensors="pt").to(accelerator.device)

                embeds_pos = text_encoder(input_ids=tokens_pos.input_ids, attention_mask=tokens_pos.attention_mask).last_hidden_state
                embeds_neg = text_encoder(input_ids=tokens_neg.input_ids, attention_mask=tokens_neg.attention_mask).last_hidden_state
                
                embeds = torch.cat([embeds_neg, embeds_pos], dim=0)

                with torch.no_grad():
                    gt_latents = vae.encode(inputs["output_images"]).latent_dist.sample() * scale

                mask = torch.nn.functional.interpolate(inputs["mask_images"], size=gt_latents.shape[-2:], mode="nearest")

                if outpaint:
                    mask = 1.0 - mask
                input_latents = gt_latents * (1 - mask)

                noise = torch.randn_like(input_latents)
                t = torch.randint(0, pipe.scheduler.config.num_train_timesteps, (input_latents.shape[0],), device=input_latents.device).long()

                noise_applied = pipe.scheduler.add_noise(gt_latents, noise, t)
                noisy_latents = input_latents * (1 - mask) + noise_applied * mask

                masked_latents = gt_latents * mask
                if debug:
                    debug_path = os.path.join(save_dir, 'debug')
                    os.makedirs(debug_path, exist_ok=True)
                    save_image(mask[:1], f"{debug_path}/mask_step_{global_step}.png")
                    save_image(pipe.vae.decode(noisy_latents[:1] / scale).sample.clamp(0, 1), f"{debug_path}/noisy_latents_step_{global_step}.png")
                    save_image(pipe.vae.decode(masked_latents[:1] / scale).sample.clamp(0, 1), f"{debug_path}/masked_latents_step_{global_step}.png")
                noisy_latents = torch.cat([noisy_latents] * 2, dim=0)
                t = torch.cat([t] * 2, dim=0)
                mask = torch.cat([mask] * 2, dim=0)
                masked_latents = torch.cat([masked_latents] * 2, dim=0)

                noise_pred = unet(
                    noisy_latents,
                    t,
                    encoder_hidden_states=embeds,
                    added_cond_kwargs={"mask": mask, "masked_image_latents": masked_latents},
                ).sample
                
                noise_pred_uncond, noise_pred_text = noise_pred.chunk(2, dim=0)
                noise_pred_final = noise_pred_uncond + 6 * (noise_pred_text - noise_pred_uncond)

                B = noise.shape[0]
                loss = mse_loss(noise_pred_final * mask[:B].detach(), noise * mask[:B].detach(), reduction="mean")
                if torch.isnan(loss):
                    print("NaN detected. Skipping step.")
                    continue

                accelerator.backward(loss)

                if global_step % CFG["grad_accum_steps"] == 0:
                    optimizer.step()
                    optimizer.zero_grad()

                if global_step % CFG["save_every"] == 0:
                    with torch.no_grad():
                        pred_latents = torch.cat([
                            pipe.scheduler.step(noise_pred_final[i:i+1], t[i:i+1], noisy_latents[i:i+1]).prev_sample
                            for i in range(noisy_latents.shape[0])
                        ])
                        pred_images = decode_latents(vae, pred_latents, scale)
                        if global_step == 1:
                            save_image(pred_images, f"debug/pred_image_step_{global_step}.png")
                        psnr = evaluate_and_log(pred_images, inputs["output_images"], global_step)

                        if psnr > best_psnr:
                            best_psnr = psnr
                            best_step = global_step
                            # Save only LoRA weights
                            # torch.save(unet.state_dict(), os.path.join(save_dir, f"best_unet.pt"))
                            # torch.save(text_encoder.state_dict(), os.path.join(save_dir, f"best_text_encoder.pt"))
                            unet.unet.save_pretrained(f'outputs/{category}/unet_step{best_step}', safe_serialization=True)
                            text_encoder.save_pretrained(f'outputs/{category}/text_encoder_step{best_step}', safe_serialization=True)
                            save_image(pred_images, os.path.join(save_dir, f"best_pred_{best_step}.png"))
                            print(f"✅ Best model saved at step {global_step} (PSNR: {psnr:.2f})")
                            no_improve_counter = 0
                        else:
                            no_improve_counter += 1

                        lr_scheduler.step(psnr)

                if accelerator.is_main_process:
                    wandb.log({
                        "loss": loss.item(),
                        "lr": optimizer.param_groups[0]['lr'],
                        "step": global_step,
                        "psnr": psnr if psnr is not None else 0,
                    })

                pbar.set_postfix({
                    "step": global_step,
                    "loss": f"{loss.item():.4f}" if not torch.isnan(loss) else "NaN ❌",
                    "lr": f"{optimizer.param_groups[0]['lr']:.2e}",
                    "best_psnr": f"{best_psnr:.2f}"
                })

                if no_improve_counter > 150:
                    print(f"Early stopping triggered at step {global_step}")
                    break

                if epoch == epochs:
                    unet.unet.save_pretrained(f'outputs/{category}/unet_step{global_step}', safe_serialization=True)
                    text_encoder.save_pretrained(f'outputs/{category}/text_encoder_step{global_step}', safe_serialization=True)
                    pipe.tokenizer.save_pretrained(f'outputs/{category}/tokenizer_step{global_step}')

if __name__ == "__main__":
    main()
