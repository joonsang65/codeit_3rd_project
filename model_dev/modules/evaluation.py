import torch
import torch.nn.functional as F
from PIL import Image
from transformers import CLIPProcessor, CLIPModel, BlipProcessor, BlipForConditionalGeneration
from aesthetics_predictor import AestheticsPredictorV1

class ImageEvaluator:
    def __init__(self, device='cuda'):
        self.device = device
        self.clip_model = CLIPModel.from_pretrained("openai/clip-vit-large-patch14").eval().to(device)
        self.clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-large-patch14")
        self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base").eval().to(device)
        self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.aesthetic_model = AestheticsPredictorV1.from_pretrained("shunk031/aesthetics-predictor-v1-vit-large-patch14").eval().to(device)
        self.aesthetic_processor = CLIPProcessor.from_pretrained("shunk031/aesthetics-predictor-v1-vit-large-patch14")

    def get_aesthetic_score(self, image: Image.Image):
        inputs = self.aesthetic_processor(images=image, return_tensors="pt").to(self.device)
        outputs = self.aesthetic_model(**inputs)
        return round(outputs.logits.squeeze().item(), 2)

    @torch.no_grad()
    def evaluate_image(self, image: Image.Image, prompt: str):
        '''이미지에 대한 평가 함수'''
        clip_inputs = self.clip_processor(text=prompt, images=image, return_tensors="pt", padding=True).to(self.device)
        clip_score = F.cosine_similarity(
            self.clip_model(**clip_inputs).image_embeds,
            self.clip_model(**clip_inputs).text_embeds
        ).item() * 100

        blip_inputs = self.blip_processor(image, return_tensors="pt").to(self.device)
        caption_ids = self.blip_model.generate(**blip_inputs, max_new_tokens=30)
        caption = self.blip_processor.decode(caption_ids[0], skip_special_tokens=True)

        return {
            "clip_score": round(clip_score, 2),
            "aesthetic_score": self.get_aesthetic_score(image),
            "blip_caption": caption
        }
