import os, sys
import torch
import torch.nn as nn
import torch.onnx
model_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
print(model_path)
if model_path not in sys.path:
    sys.path.append(model_path)

from modules import utils, pipeline_utils

# -----------------------------
# 설정 및 초기화
# -----------------------------
CATEGORY = "furniture"
config = utils.load_config('model_config.yaml')
output_base = os.path.join(CATEGORY, "ONNX_model")
os.makedirs(output_base, exist_ok=True)

# -----------------------------
# 파이프라인 로드 및 LoRA 적용
# -----------------------------
def load_and_merge_lora(category):
    pipe = pipeline_utils.load_pipeline_by_type(config=config, pipeline_type='inpaint', controlnet_types=None)
    pipe = pipeline_utils.apply_loras(pipe, config, category)
    return pipe

pipe = load_and_merge_lora(CATEGORY)

# -----------------------------
# UNet Export
# -----------------------------
print("Exporting UNet...")
unet_path = os.path.join(output_base, "unet_merged")
os.makedirs(unet_path, exist_ok=True)

pipe.to("cpu")
sample = torch.randn(2, 9, 64, 64).half()
timestep = torch.tensor([1, 1], dtype=torch.int64)
encoder_hidden_states = torch.randn(2, 77, 768).half()

torch.onnx.export(
    pipe.unet,
    (sample, timestep, encoder_hidden_states),
    f=os.path.join(unet_path, "unet_merged.onnx"),
    input_names=["sample", "timestep", "encoder_hidden_states"],
    output_names=["noise_pred"],
    dynamic_shapes={
        "sample": {0: "batch", 2: "height", 3: "width"},
        "timestep": {0: "batch"},
        "encoder_hidden_states": {0: "batch"},
    },
    opset_version=18,
    do_constant_folding=True,
    export_params=True,
    dynamo=True  # optional
)

# # -----------------------------
# # Text Encoder Export
# # -----------------------------
# print("Exporting Text Encoder...")
# prompt = f"A photo of a {CATEGORY} product on a table"
# inputs = pipe.tokenizer(prompt, return_tensors="pt", padding="max_length", truncation=True, max_length=77)

# text_encoder_path = os.path.join(output_base, "text_encoder")
# os.makedirs(text_encoder_path, exist_ok=True)

# torch.onnx.export(
#     pipe.text_encoder,
#     (inputs["input_ids"].int(),),
#     f=os.path.join(text_encoder_path, "text_encoder.onnx"),
#     input_names=["input_ids"],
#     output_names=["last_hidden_state"],
#     dynamic_shapes={"input_ids": {0: "batch_size"}},
#     export_params=True,
#     do_constant_folding=True,
#     opset_version=18,
#     dynamo=True
# )

# # -----------------------------
# # VAE Decoder Export
# # -----------------------------
# print("Exporting VAE Decoder...")
# class VAEDecoderWrapper(nn.Module):
#     def __init__(self, vae):
#         super().__init__()
#         self.vae = vae
#     def forward(self, latents):
#         return self.vae.decode(latents.half())

# vae_decoder = VAEDecoderWrapper(pipe.vae).cpu().eval()
# latent_input = torch.randn(1, 4, 64, 64).half()
# vae_decoder_path = os.path.join(output_base, "vae_decoder")
# os.makedirs(vae_decoder_path, exist_ok=True)

# torch.onnx.export(
#     vae_decoder, (latent_input,),
#     f=os.path.join(vae_decoder_path, "vae_decoder.onnx"),
#     input_names=["latent_sample"],
#     output_names=["image"],
#     export_params=True,
#     do_constant_folding=True,
#     opset_version=20,
#     dynamo=True
# )

# # -----------------------------
# # VAE Encoder Export
# # -----------------------------
# print("Exporting VAE Encoder...")
# class VAEEncoderWrapper(nn.Module):
#     def __init__(self, vae):
#         super().__init__()
#         self.vae = vae
#     def forward(self, x):
#         return self.vae.encode(x.half()).latent_dist.mean

# vae_encoder = VAEEncoderWrapper(pipe.vae).cpu().eval()
# image_input = torch.randn(1, 3, 512, 512).half()
# vae_encoder_path = os.path.join(output_base, "vae_encoder")
# os.makedirs(vae_encoder_path, exist_ok=True)

# torch.onnx.export(
#     vae_encoder, (image_input,),
#     f=os.path.join(vae_encoder_path, "vae_encoder.onnx"),
#     input_names=["sample"],
#     output_names=["latent"],
#     export_params=True,
#     do_constant_folding=True,
#     opset_version=20,
#     dynamo=True
# )

# # -----------------------------
# # Scheduler, Tokenizer 저장
# # -----------------------------
# print("Saving scheduler and tokenizer...")
# pipe.scheduler.save_pretrained(os.path.join(output_base, "scheduler"))
# pipe.tokenizer.save_pretrained(os.path.join(output_base, "tokenizer"))

# print(f"[DONE] All components exported to {output_base}")
