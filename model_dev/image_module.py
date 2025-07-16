import os
import csv
from PIL import Image
from modules import utils, pipeline_utils, gpt_module, ad_generator, evaluation
from diffusers import StableDiffusionInpaintPipeline, StableDiffusionPipeline

class AdImageGenerator:
    def __init__(self, config: dict, category: str = "cosmetics"):
        self.cfg = config
        self.category = category
        self.canvas_size = config.get('canvas_size', (512, 512))
        self.api_key = os.getenv(config['openai']['api_key_env'])
        self.client = gpt_module.GPTClient(
            api_key=self.api_key,
            model_name=config['openai']['gpt_model']
        )
        self.pipe = None

    def generate_prompt(self, pipe, canvas:Image.Image=None, ref_image:Image.Image=None) -> str:
        if isinstance(pipe, StableDiffusionPipeline):
            messages = [
                {"role": "system", "content": (
                    "You are an advertisement planner. Plan the advertisement background for a product. "
                    "Do NOT mention the product, human, or text. Only describe mood, color, and background design."
                )},
                {"role": "user", "content": f"{self.category} 광고에 맞는 배경"}
            ]
            ad_plan = self.client.chat(messages, max_tokens=200)
            return self.client.convert_to_sd_prompt(ad_plan)
        elif isinstance(pipe, StableDiffusionInpaintPipeline):
            if canvas is None:
                raise ValueError("base64로 변환할 이미지를 입력하지 않았습니다.")
            prompt = self.client.convert_to_sd_prompt(
                self.client.analyze_ad_plan(
                    product_b64=utils.encode_image(canvas),
                    ref_b64=utils.encode_image(ref_image) if ref_image is not None else None,
                    product_type=self.category,
                    marketing_type=f"{self.category}에 맞는 배경 생성"
                )
            )
            return prompt
        else:
            raise TypeError(f"지원하지 않는 파이프라인 입니다. TYPE: {type(pipe)}")

    def prepare_pipeline(self, mode: str):
        pipe = pipeline_utils.load_pipeline_by_type(self.cfg, mode)
        if hasattr(pipe, "unload_lora_weights"):
            pipe.unload_lora_weights()
        pipeline_utils.apply_loras(pipe, self.cfg, category=self.category)
        return pipe

    def image_process(self, canvas_input:Image.Image=None):
        self.img = self.cfg['paths']['product_image']
        _, back_rm = utils.remove_background(self.img)
        resized = utils.resize_to_ratio(back_rm, self.cfg['image_config']['resize_info'])
        canvas = Image.new("RGBA", self.canvas_size, (255, 255, 255, 255)) if canvas_input is None else canvas_input
        canvas = utils.overlay_product(canvas, resized, self.cfg['image_config']['position'])
        canvas, back_rm_canv = utils.remove_background(canvas)
        mask = utils.create_mask(back_rm_canv)
        return canvas, back_rm_canv, mask

    def run_text2img(self):
        pipe = self.prepare_pipeline("text2img")
        prompt = self.generate_prompt(pipe)
        images = ad_generator.generate_background(pipe, prompt, self.cfg)
        top_image = self.evaluate_and_save(images, prompt)
        return top_image

    def run_inpaint(self, canvas:Image.Image, mask:Image.Image, ref_image:Image.Image=None):
        pipe = self.prepare_pipeline("inpaint")
        prompt = self.generate_prompt(pipe, canvas, ref_image)
        images = ad_generator.run_inpainting(pipe, canvas, mask, prompt, self.cfg)
        top_image = self.evaluate_and_save(images, prompt)
        return top_image

    def evaluate_and_save(self, images, prompt):
        evaluator = evaluation.ImageEvaluator()
        eval_logs = [evaluator.evaluate_image(img, prompt) for img in images]

        # 저장 경로 설정
        # save_dir = "outputs/eval_results"
        # utils.ensure_dir(save_dir)
        # csv_path = os.path.join(save_dir, "evaluation_results.csv")
        # prefix = "bg" if mode == 'text2img' else "inp"

        # with open(csv_path, "w", newline="", encoding="utf-8") as f:
        #     writer = None
        #     for idx, (img, log) in enumerate(zip(images, eval_logs)):
        #         filename = f"{prefix}_{idx:02d}.png"
        #         img.save(os.path.join(save_dir, filename))
        #         row = {"index": idx, "filename": filename, **log}
        #         if writer is None:
        #             writer = csv.DictWriter(f, fieldnames=row.keys())
        #             writer.writeheader()
        #         writer.writerow(row)

        # 상위 1장 선별 (aesthetic 기준 or clip 기준)
        # 예: clip 기준으로 정렬
        clip_sorted = sorted(
            zip(images, eval_logs),
            key=lambda x: x[1].get("clip_score", 0),
            reverse=True
        )

        # aesthetic_sorted = sorted(
        #     zip(images, eval_logs),
        #     key=lambda x: x[1].get("aesthetic_score", 0),
        #     reverse=True
        # )

        clip_top_img, clip_top_log = clip_sorted[0]
        # aesthetic_top_img, aesthetic_top_log = aesthetic_sorted[0]

        return clip_top_img
    
    def update_config(self, new_cfg: dict):
        self.cfg.update(new_cfg)


# if __name__ == "__main__":
#     base_dir = os.path.dirname(os.path.abspath(__file__))
#     try:
#         config_path = os.path.join(base_dir, "model_config.yaml")
#         cfg = utils.load_config(config_path)
#     except Exception as e:
#         print(f"경로를 찾지 못했습니다: {e}")
#     cfg.update({'canvas_size': CANVAS_SIZE})
#     generator = AdImageGenerator(cfg, category=CATEGORY)

#     # 텍스트 기반 생성
#     clip_top_img = generator.run_text2img()
#     clip_top_img.save("example1.png")
#     # aesthetic_top_img.save("example2.png")

#     # 인페인팅 생성
#     clip_top_img = generator.run_inpaint()
#     clip_top_img.save("inp_example1.png")
#     # aesthetic_top_img.save("inp_examples2.png")

CANVAS_SIZE = (512, 512) # 사용자 설정 반영
CATEGORY = "cosmetics"   # 사용자 설정 반영
SIZE_INFO = (128, 128)   # 사용자 설정 반영
POSITION = (300, 220)    # 사용자 설정 반영
base_dir = os.path.dirname(os.path.abspath(__file__))
try:
    config_path = os.path.join(base_dir, "model_config.yaml")
    cfg = utils.load_config(config_path)
except Exception as e:
    print(f"경로를 찾지 못했습니다: {e}")

IMAGE = Image.open(os.path.join(base_dir,cfg['paths']['product_image']))

generator = AdImageGenerator(cfg, CATEGORY)

config_update = {
    'canvas_size': CANVAS_SIZE,
    'product_type': CATEGORY,
    'image_config': {
            'resize_info': SIZE_INFO,
            'position': POSITION
        },
    }
generator.cfg['paths']['product_image'] = IMAGE
generator.update_config(config_update)

if not os.path.exists(cfg['paths']['lora_dir']):
    print(os.path.abspath('./'))
    lora_dir = os.path.join(os.path.abspath('../'), cfg['paths']['lora_dir'])
    cfg['paths']['lora_dir'] = lora_dir

def step1():
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
    if mode == 'text2img':
        return generator.run_text2img()
    elif mode == 'inpaint':
        if canvas is None and mask is None:
            raise ValueError(f"입력 정보가 잘못되었습니다. canvas: {type(canvas)}, mask: {type(mask)} 필수 정보를 확인하고 다시 입력해 주세요.")
        return generator.run_inpaint(canvas, mask, ref_image)
    else:
        raise TypeError(f"{mode} is not supported")