# backend/app/services/image_main.py

from dotenv import load_dotenv
load_dotenv()

import os
# os.environ["HF_HOME"] = "D:/huggingface"

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from typing import Literal, Union, List
from PIL import Image
import logging
import torch
from diffusers import StableDiffusionInpaintPipeline, StableDiffusionPipeline

from image_modules import utils, pipeline_utils, gpt_module, ad_generator, evaluation
from image_modules.utils import logger

class AdImageGenerator:
    def __init__(self, config: dict, category: str = "cosmetics"):
        '''
        설정값을 입력으로 받아 generator를 초기화 합니다.

        note: 
            - client: OpenAI GPT 4.1 mini
            - evaluator: 생성 이미지 평가 모듈 (Clip, Aesthetic, Caption -> 현재는 CLIP score만 고려합니다.)
        '''
        self.cfg = config
        self._category = category
        self.canvas_size = config.get('canvas_size', (512, 512))
        self.api_key = os.getenv(config['openai']['api_key_env'])
        self.client = gpt_module.GPTClient(
            api_key=self.api_key,
            model_name=config['openai']['gpt_model']
        )
        self.pipe = None
        self.evaluator = evaluation.ImageEvaluator()
        self.current_mode = None
        self.current_category = None
        self.marketing_type = None

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        '''카테고리 변경 감지 및 적용 setter'''
        if self._category != value:
            logger.info(f"카테고리를 '{value}'로 변경합니다.")
            self._category = value
            if self.pipe:
                # 동일한 mode로 pipeline 재적용
                self.prepare_pipeline(self.current_mode) 

    def update_config(self, new_cfg: dict):
        '''Canvas_size 및 포지션 정보를 반영하기 위해 설정값을 업데이트'''
        self.cfg.update(new_cfg)

    def generate_prompt(self, pipe, canvas:Image.Image=None, ref_image:Image.Image=None) -> str:
        '''
        프롬프트 생성 모듈
        모드에 따라 자동 생성된 파이프라인을 기준으로 배경을 생성하기 위한 프롬프트 제작 방식이 나뉜다.
            1. 텍스트 기반 프롬프트 생성 (text2img)
            2. 이미지 기반 프롬프트 생성 (text2img, inpaint) + input_image
            3. Controlnet 구도조정 (Backend 미구현)
            4. IP-Adapter 스타일 반영 (Backend 미구현)
        우선적으로 광고전략을 생성 후 prompt로 convert한다.

        input:
            - pipe: 파이프라인
            - canvas: 전처리 과정에서 사이즈, 위치정보가 반영된 canvas
            - ref_image: 참조할 배경 이미지 (있다면)
        
        return:
            - prompt: 이미지 생성에 사용할 프롬프트
        '''
        if isinstance(pipe, StableDiffusionPipeline) and canvas is None:
            logger.info("홍보 전략을 구성합니다. (텍스트 기반)")
            messages = [
                {"role": "system", "content": (
                    "You are an advertisement planner. Plan the advertisement background for a product. "
                    "Do NOT mention the product, human, or text. Only describe mood, color, and background design."
                )},
                {"role": "user", "content": f"{self._category} 광고에 맞는 배경 생성"}
            ]
            ad_plan = self.client.chat(messages, max_tokens=200)
    
        elif (
        (isinstance(pipe, StableDiffusionPipeline) or isinstance(pipe, StableDiffusionInpaintPipeline))
        and canvas is not None
    ):
            logger.info("이미지를 정보로 홍보 전략을 구성합니다.")
            if canvas is None:
                raise ValueError("base64로 변환할 이미지를 입력하지 않았습니다.")
            ad_plan = self.client.analyze_ad_plan(
                    product_b64=utils.encode_image(canvas),
                    ref_b64=utils.encode_image(ref_image) if ref_image is not None else None,
                    product_type=self._category,
                    marketing_type=f"{self.marketing_type}의 분위기에 맞는 배경 생성"
                )
        else:
            raise TypeError(f"지원하지 않는 파이프라인 입니다. TYPE: {type(pipe)}")
        logger.debug(f"광고 전략: {ad_plan}")
        prompt = self.client.convert_to_sd_prompt(ad_plan)
        logger.debug(f"생성된 프롬프트: {prompt}")
        return prompt
        
    def prepare_pipeline(self, mode: str):
        '''
        모드 입력에 맞게 파이프라인을 설정합니다.
        예: ['text2img', 'inpaint'] +  ['controlnet', 'controlnet_inpaint'] (현재 서버에 기능 반영은 안된 상태, 추후 업데이트)
        또한, 내부적으로 모드 변경을 감지하여 필요한 경우 원래있던 파이프라인을 내리고 다시 로드합니다.
        '''
        if self.current_mode != mode:
            self._unload_pipeline()
            logger.info(f"{mode} 파이프라인을 새로 로드합니다.")
            self.pipe = pipeline_utils.load_pipeline_by_type(self.cfg, mode)
            self.current_mode = mode

        if self.current_category != self._category:
            if hasattr(self.pipe, "unload_lora_weights"):
                self.pipe.unload_lora_weights()
            self.pipe = pipeline_utils.apply_loras(self.pipe, self.cfg, category=self._category)
            self.current_category = self._category
            logger.debug(f"LoRA 적용 상태: {self.pipe.get_active_adapters()}")

        return self.pipe
    def image_append(self):
        self.img = self.cfg['paths']['product_image']
        _, self.back_rm = utils.remove_background(self.img)
        return self.back_rm

    def image_process(self, canvas_input:Image.Image=None):
        '''
        이미지 전처리 단계.
        입력이미지의 배경을 제거하고 사용자 설정을 반영하여 크기를 변경하고 위치를 조정하여 캔버스에 붙이는 작업.
        이후 작업을 위해 추가적으로 만들어진 canvas의 배경을 제거한 이미지와 마스킹 이미지를 만들어 반환합니다.
        '''
        logger.debug(f"  - 이미지 사이즈: {self.cfg['image_config']['resize_info']}")
        logger.debug(f"  - 포지션 사이즈: {self.cfg['image_config']['position']}")
        resized = utils.resize_to_ratio(self.back_rm, self.cfg['image_config']['resize_info'])
        canvas = Image.new("RGBA", self.canvas_size, (0, 0, 0, 0)) if canvas_input is None else canvas_input
        canvas = utils.overlay_product(canvas, resized, self.cfg['image_config']['position'])
        canvas, back_rm_canv = utils.remove_background(canvas)
        mask = utils.create_mask(back_rm_canv, 10, 10)
        return canvas, back_rm_canv, mask

    def run_text2img(self, canvas:Image.Image=None, ref_image:Image.Image=None):
        '''
        텍스트 기반 이미지 생성.
        - 입력 이미지를 감지 하여, 프롬프트를 생성할때 이미지정보를 고려하는 기능.
        - 입력 이미지가 없을 경우, category를 기반으로 자동 프롬프트 생성.
        이후 생성된 프롬프트를 기반으로 배경이미지를 생성합니다.
        '''
        logger.debug(f"  - 캔버스 타입: {self.cfg['canvas_type']}")
        if self.pipe is None or not isinstance(self.pipe, StableDiffusionPipeline):
            self._unload_pipeline()
            self.pipe = self.prepare_pipeline("text2img")
        prompt = self.generate_prompt(self.pipe, canvas, ref_image)
        images = ad_generator.generate_background(self.pipe, prompt, self.cfg)
        top_image = self.evaluate_and_save(images, prompt)
        return top_image

    def run_inpaint(self, canvas:Image.Image, mask:Image.Image, ref_image:Image.Image=None):
        '''
        Inpaint를 진행.
        모드는 inpaint이나, 사실은 outpaint를 진행.
        mask 이미지를 invert 시켜 제품이미지를 제외한 배경을 프롬프트 기반으로 재생성한다.
        '''
        logger.debug(f"  - 캔버스 타입: {self.cfg['canvas_type']}")
        if self.pipe is None or not isinstance(self.pipe, StableDiffusionInpaintPipeline):
            self._unload_pipeline()
            self.pipe = self.prepare_pipeline("inpaint")
        prompt = self.generate_prompt(self.pipe, canvas, ref_image)
        images = ad_generator.run_inpainting(self.pipe, canvas, mask, prompt, self.cfg)
        top_image = self.evaluate_and_save(images, prompt)
        return top_image

    def evaluate_and_save(self, images: List[Image.Image], prompt: str):
        '''
        여러개의 생성된 이미지 중 Clip score 기반으로 정렬 후 최상위(top_1) 이미지를 선택 후 반환
        '''
        
        eval_logs = [self.evaluator.evaluate_image(img, prompt) for img in images]

        clip_sorted = sorted(
            zip(images, eval_logs),
            key=lambda x: x[1].get("clip_score", 0),
            reverse=True
        )

        return clip_sorted[0][0]

    def cleanup(self):
        '''파이프라인 정리'''
        self._unload_pipeline()
    
    def _unload_pipeline(self):
        '''파이프라인을 정리 내부 호출 함수'''
        try:
            if self.pipe:
                self.pipe.to("cpu")
                del self.pipe
                self.pipe = None
        except Exception as e:
            logger.error(f"리소스 정리 실패: {str(e)}")


CANVAS_SIZE = {
        "instagram": (512, 512),
        "poster": (512, 768),
        "blog": (768, 470),
    } # 사용자 설정 반영
CATEGORY = "cosmetics"   # 사용자 설정 반영
SIZE_INFO = (128, 128)   # 사용자 설정 반영
POSITION = (300, 220)    # 사용자 설정 반영
base_dir = os.path.abspath("./app/services")
print(base_dir)
# base_dir = os.path.join(base_dir, 'model_dev')
try:
    config_path = os.path.join(base_dir, "model_config.yaml")
    cfg = utils.load_config(config_path)
except Exception as e:
    print(f"경로를 찾지 못했습니다: {e}")

# IMAGE = Image.open(cfg['paths']['product_image'])

generator = AdImageGenerator(cfg, CATEGORY)

config_update = {
    'canvas_size': CANVAS_SIZE,
    'product_type': CATEGORY,
    'image_config': {
            'resize_info': SIZE_INFO,
            'position': POSITION
        },
    }
# generator.cfg['paths']['product_image'] = IMAGE
generator.update_config(config_update)

if not os.path.exists(cfg['paths']['lora_dir']):
    print(os.path.abspath('./'))
    lora_dir = os.path.join(os.path.abspath('../'), cfg['paths']['lora_dir'])
    cfg['paths']['lora_dir'] = lora_dir

def step1():
    return generator.image_append()

def step1_5():
    '''
    Step1: 입력 이미지를 전처리 및 배경제거
    최종 목적은 크기와 위치정보를 반영한 이미지를 만드는 것을 목적으로 하며,
    다음 단계를 위해, 배경제거한 최종 이미지와 마스킹이미지를 같이 반환합니다.

    input:
        - image (Image.Image): 제품 원본 이미지 혹은 경로

    output:
        - canvas (Image.Image): 크기와 위치정보를 반영하여 빈 캔버스에 제품을 붙여넣은 이미지
        - back_rm_canv (Image.Image): 캔버스 배경이 제거된 이미지
        - mask (Image.Image): back_rm_canv의 제품 마스킹
    
    '''
    return generator.image_process()

def step2(mode: str, canvas:Image.Image=None, mask:Image.Image=None, ref_image:Image.Image=None):
    '''
    step2: 입력 정보를 기반으로 프롬프트 생성 + 이미지 생성을 진행합니다.
    내부적으로 평가 함수가 존재하며, 평가를 기반으로 top_1 이미지를 반환합니다.

    input:
        - mode: 생성 모드
        - canvas: 전처리된 전체 이미지 (배경 + 제품)
        - mask: 제품부분이 마스킹된 이미지 (invert 됩니다.)
    
    output:
        - result: 내부 평가 함수를 통과한 top_1 이미지
    '''
    if mode == 'text2img':
        return generator.run_text2img(canvas, ref_image)
    elif mode == 'inpaint':
        if canvas is None and mask is None:
            raise ValueError(f"입력 정보가 잘못되었습니다. canvas: {type(canvas)}, mask: {type(mask)} 필수 정보를 확인하고 다시 입력해 주세요.")
        return generator.run_inpaint(canvas, mask, ref_image)
    else:
        raise TypeError(f"{mode} is not supported")