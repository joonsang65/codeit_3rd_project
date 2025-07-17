import torch
import torch.nn.functional as F
from PIL import Image
from transformers import CLIPProcessor, CLIPModel, BlipProcessor, BlipForConditionalGeneration
from aesthetics_predictor import AestheticsPredictorV1
from image_modules.utils import logger, log_execution_time

class ImageEvaluator:
    def __init__(self, device='cuda'):
        logger.info("이미지 평가를 위한 모델을 로드합니다.")
        self.device = device
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14").eval().to(device)
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
        self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").eval().to(device)
        self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.aesthetic_model = AestheticsPredictorV1.from_pretrained("shunk031/aesthetics-predictor-v1-vit-large-patch14").eval().to(device)
        self.aesthetic_processor = CLIPProcessor.from_pretrained("shunk031/aesthetics-predictor-v1-vit-large-patch14")
    
    @log_execution_time(label="Aesthetic Score 채점 중...")
    def get_aesthetic_score(self, image: Image.Image):
        inputs = self.aesthetic_processor(images=image, return_tensors="pt").to(self.device)
        outputs = self.aesthetic_model(**inputs)
        logger.debug(f"Aesthtic Score: {round(outputs.logits.squeeze().item(), 2)}")
        return round(outputs.logits.squeeze().item(), 2)

    @log_execution_time(label="생성된 이미지 평가를 시작합니다...")
    @torch.no_grad()
    def evaluate_image(self, image: Image.Image, prompt: str):
        '''이미지에 대한 평가 함수'''
        logger.info("생성된 이미지를 평가합니다.")
        clip_inputs = self.clip_processor(text=prompt, images=image, return_tensors="pt", padding=True).to(self.device)
        clip_score = F.cosine_similarity(
            self.clip_model(**clip_inputs).image_embeds,
            self.clip_model(**clip_inputs).text_embeds
        ).item() * 100

        logger.debug(f"Clip Score: {round(clip_score, 2)}")
        blip_inputs = self.blip_processor(image, return_tensors="pt").to(self.device)
        caption_ids = self.blip_model.generate(**blip_inputs, max_new_tokens=30)
        caption = self.blip_processor.decode(caption_ids[0], skip_special_tokens=True)
        logger.debug(f"Caption 기록: {caption[:10]}...")

        return {
            "clip_score": round(clip_score, 2),
            "aesthetic_score": self.get_aesthetic_score(image),
            "blip_caption": caption
        }
