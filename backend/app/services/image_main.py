# backend/app/services/image_main.py

from dotenv import load_dotenv
load_dotenv()

import os
os.environ["HF_HOME"] = "D:/huggingface"

import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from typing import Literal, Union, List
from PIL import Image
import logging
import torch
from diffusers import StableDiffusionInpaintPipeline, StableDiffusionPipeline

from image_modules import utils, pipeline_utils, gpt_module, ad_generator

logger = utils.setup_logger(__name__, logging.DEBUG)
base_dir = os.path.dirname(os.path.abspath(__file__))
try:
    config_path = os.path.join(base_dir, "model_config.yaml")
    config = utils.load_config(config_path)
    logger.info(config)
except Exception as e:
    logger.warning(f"경로를 찾지 못했습니다: {e}")

# try:
#     if os.path.exists("./model_config.yaml"):
#         config = utils.load_config("model_config.yaml")
#     else:
#         config = utils.load_config("backend/services/model_config.yaml")

#     logger.info(config)
# except Exception as e:
#     logger.warning(f"경로를 찾지 못했습니다: {e}")
    
def resolve_path(path):
    if not os.path.isabs(path):
        return os.path.abspath(os.path.join(os.path.dirname(__file__), path))
    return path

for key in config['paths']:
    config['paths'][key] = resolve_path(config['paths'][key])

class ImageProcessor:
    def __init__(self):
        self.config = config
        self.inpaint_pipeline = None
        self.text2img_pipeline = None
        self.ip_adapter = None

    def load_pipelines(self, mode: str):
        try:
            if mode == "inpaint" and not self.inpaint_pipeline:
                self.inpaint_pipeline = StableDiffusionInpaintPipeline.from_pretrained(
                    self.config["sd_pipeline"]["inpaint"]["model_id"],
                    torch_dtype=self.config["sd_pipeline"]["torch_dtype"],
                ).to(self.config["sd_pipeline"]["device"])
                logger.info("Inpaint 파이프라인 로드 완료")
            elif mode == "text2img" and not self.text2img_pipeline:
                self.text2img_pipeline = StableDiffusionPipeline.from_pretrained(
                    self.config["sd_pipeline"]["text2img"]["model_id"],
                    torch_dtype=self.config["sd_pipeline"]["torch_dtype"],
                ).to(self.config["sd_pipeline"]["device"])
                logger.info("Text2Img 파이프라인 로드 완료")
        except Exception as e:
            logger.error(f"파이프라인 로드 실패: {str(e)}")
            raise

    def step1(self, img: Image.Image) -> tuple[Image.Image, Image.Image]:
        """
        Step 1: 이미지 전처리 및 배경 제거
        - 입력된 이미지의 배경을 제거하고, 지정된 크기로 리사이즈합니다.
        - 최종적으로 빈 캔버스에 리사이즈된 이미지를 오버레이합니다.

        input:
        - img_path (str): 배경 제거할 이미지의 경로
        output:
        - back_rm_canv (PIL.Image.Image): 배경이 제거된 캔버스 이미지
        """
        try:
            utils.ensure_dir(self.config['paths']['output_dir'])
            self.config['product_type'] = "food"
            self.config['canvas_size'] = (512, 512)

            logger.info("이미지 배경 제거 중...")
            orig_img, back_rm_img = utils.remove_background(img)

            logger.info("이미지 사이즈 변경 중...")
            resized_img = utils.resize_to_ratio(back_rm_img, (128, 128))

            canvas = Image.new("RGBA", self.config['canvas_size'], (255, 255, 255, 255))
            canvas = utils.overlay_product(canvas, resized_img, (300, 220))
            canv_img, back_rm_canv = utils.remove_background(canvas)

            return resized_img, back_rm_canv
        except Exception as e:
            logger.error(f"Step1 처리 실패: {str(e)}")
            raise

    def step2(self, mode: Literal['inpaint', 'text2img'], resized_img: Image.Image, back_rm_canv: Image.Image) -> Union[Image.Image, List[Image.Image]]:
        """
        Step 2: 광고 전략 생성 및 이미지 생성
        - OpenAI API를 사용하여 광고 전략을 생성합니다.
        - 생성된 광고 전략을 기반으로 Stable Diffusion 파이프라인을 통해 이미지를 생성합니다.
        - 생성된 PIL 이미지 객체 또는 이미지 리스트를 반환합니다.
        
        Args:
            mode (str): 'inpaint' 또는 'text2img' 생성 모드 선택
            resized_img (PIL.Image.Image): 리사이즈된 상품 이미지
            back_rm_canv (PIL.Image.Image): 배경 제거된 캔버스 이미지
        
        Returns:
            PIL.Image.Image 또는 리스트: 생성된 이미지 또는 이미지 리스트
        """
        try:
            self.load_pipelines(mode)
            api_key = os.getenv(self.config['openai']['api_key_env'])
            if not api_key:
                raise RuntimeError(f"{self.config['openai']['api_key_env']} 환경 변수가 설정되어 있지 않습니다.")
            client = gpt_module.GPTClient(
                api_key=api_key,
                model_name=self.config['openai']['gpt_model']
            )

            if mode == 'inpaint':
                logger.info(f"{mode.upper()} 설정 확인!")
                logger.info("이미지 마스킹 생성 중...")
                mask = utils.create_mask(back_rm_canv)

                logger.info("이미지 인코딩 -> base64...")
                img_base64 = utils.encode_image(back_rm_canv)
                ref_base64 = None

                logger.info("광고 전략 생성 중...")
                ad_plan = client.analyze_ad_plan(
                    product_b64=img_base64,
                    ref_b64=ref_base64,
                    product_type=self.config['product_type'],
                    marketing_type="인풋 이미지를 마스킹한 상태에서 배경 생성하기"
                )
                logger.debug(ad_plan)

                logger.info("광고 전략 -> 프롬프트 변경 진행 중...")
                prompt = client.convert_to_sd_prompt(ad_plan)
                logger.debug(prompt)

                logger.info("파이프라인 불러오기...")
                base_pipe = self.inpaint_pipeline
                pipe = pipeline_utils.apply_loras(base_pipe, self.config, category="cosmetics")

                logger.info("Inference 진행 중...")
                images = ad_generator.run_inpainting(pipe, back_rm_canv, mask, prompt, self.config)
                return images

            else:  # mode == 'text2img'
                logger.info(f"{mode.upper()} 설정 확인!")
                message = [
                    {
                        "role": "system",
                        "content": (
                            "You are an advertisement planner, How would you plan given the advertisement with for the product? "
                            "You are only allow to describe background which fits to the product.\n"
                            "Do NOT mention about product, human, or text in the background, only the mood, color, design."
                        )
                    },
                    {
                        "role": "user",
                        "content": "화장품 광고에 맞는 배경"
                    }
                ]
                logger.info("광고 전략 생성 중...")
                ad_plan = client.chat(messages=message, max_tokens=200)
                logger.debug(ad_plan)

                logger.info("광고 전략 -> 프롬프트 변경 진행 중...")
                prompt = client.convert_to_sd_prompt(ad_plan)
                logger.debug(prompt)

                logger.info("파이프라인 불러오기...")
                base_pipe = self.text2img_pipeline
                pipe_t2i = pipeline_utils.apply_loras(base_pipe, self.config, category='cosmetics')

                logger.info("배경 이미지 생성 중...")
                gen_backs = ad_generator.generate_background(pipe_t2i, prompt, self.config)

                logger.info("IP-Adapter 설정하기...")
                self.ip_adapter = pipeline_utils.load_ip_adapter(base_pipe, self.config)

                logger.info("IP-Adapter Inference 진행 중...")
                ip_gen = ad_generator.ip_adapter_inference(self.ip_adapter, self.config, prompt, gen_backs, resized_img)
                return ip_gen

        except Exception as e:
            logger.error(f"Step2 처리 실패: {str(e)}")
            raise

    def cleanup(self):
        try:
            if self.inpaint_pipeline:
                self.inpaint_pipeline.to("cpu")
                del self.inpaint_pipeline
                self.inpaint_pipeline = None
            if self.text2img_pipeline:
                self.text2img_pipeline.to("cpu")
                del self.text2img_pipeline
                self.text2img_pipeline = None
            if self.ip_adapter:
                del self.ip_adapter
                self.ip_adapter = None
            torch.cuda.empty_cache()
            logger.info("ImageProcessor 리소스 정리 완료")
        except Exception as e:
            logger.error(f"리소스 정리 실패: {str(e)}")

image_processor = ImageProcessor()

def step1(img: Image.Image):
    return image_processor.step1(img)

def step2(mode: str, resized_img: Image.Image, back_rm_canv: Image.Image):
    return image_processor.step2(mode, resized_img, back_rm_canv)

