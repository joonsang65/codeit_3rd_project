# /rag_pipeline/main.py.
# This file will orchestrate the calls to the other modules.
import accelerate, os, time
from torchvision.transforms.functional import to_tensor
from openai import OpenAI
from dotenv import load_dotenv
from huggingface_hub import notebook_login
from omnigen2.utils.img_util import create_collage
from rag_pipeline.config import INSTAGRAM, POSTER, MODEL_PATH
from rag_pipeline.translation.prompt_translator import translate_korean_to_english
from rag_pipeline.prompting.initial_prompt_generator import generate_initial_prompt
from rag_pipeline.keyword_extraction.extractor import extract_keywords
from rag_pipeline.web_tools.search import perform_web_search
from rag_pipeline.web_tools.content_processor import fetch_and_process_content
from rag_pipeline.prompting.prompt_refiner import refine_prompt_with_content
from rag_pipeline.prompting.negative_prompt_generator import generate_negative_prompt
from rag_pipeline.core.models import initialize_pipelines
from rag_pipeline.image_generation.generator import generate_image
from rag_pipeline.image_generation.visual_analyzer import analyze_image
from rag_pipeline.translation.description_translator import translate_english_to_korean
from rag_pipeline.advertisement.copy_generator import generate_ad_copy

# 환경 변수 로드.
load_dotenv() # .env 파일에서 환경 변수 로드.
HF_TOKEN = os.getenv("HF_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

notebook_login() # Hugging Face 로그인.

llm = OpenAI(api_key = OPENAI_API_KEY)

# 한국어 프롬프트 입력.
korean_prompt = input("광고 이미지 생성을 위한 프롬프트를 한국어로 입력하시길 바랍니다: ")
poster_size = input("포스터 크기를 선택하시길 바랍니다(1: 인스타그램, 2: 포스터): ")
if poster_size == "1":
    poster_size = INSTAGRAM
elif poster_size == "2":
    poster_size = POSTER
else:
    print("잘못된 입력입니다. 기본 크기로 인스타그램 포스터를 선택합니다.")
    poster_size = INSTAGRAM

# 광고 이미지 생성 및 문구 작성 파이프라인.
print("\n광고 이미지 생성 및 문구 작성 파이프라인을 시작합니다....")

# 시간 측정을 위한 시작 시간 기록.
start_time = time.time()

# 1. 한국어 프롬프트를 영어로 번역.
print("한국어 프롬프트를 영어로 번역 중....")
start_translation_time = time.time()
translated_prompt = translate_korean_to_english(llm, korean_prompt)
end_translation_time = time.time()
print(f"번역 완료. 소요 시간: {end_translation_time - start_translation_time:.2f}초.\n번역된 프롬프트: {translated_prompt}")

# 2. 초기 프롬프트 생성.
print("초기 프롬프트 생성 중....")
start_initial_prompt_time = time.time()
initial_prompt = generate_initial_prompt(llm, translated_prompt)
end_initial_prompt_time = time.time()
print(f"초기 프롬프트 생성 완료. 소요 시간: {end_initial_prompt_time - start_initial_prompt_time:.2f}초.\n초기 프롬프트: {initial_prompt}")

# 3. 키워드 추출.
print("키워드 추출 중....")
start_keyword_extraction_time = time.time()
keywords = extract_keywords(llm, initial_prompt)
end_keyword_extraction_time = time.time()
print(f"키워드 추출 완료. 소요 시간: {end_keyword_extraction_time - start_keyword_extraction_time:.2f}초.\n추출된 키워드: {keywords}")

# 4. 웹 검색 수행.
print("웹 검색 수행 중....")
start_web_search_time = time.time()
search_results = perform_web_search(llm, keywords)
end_web_search_time = time.time()
print(f"웹 검색 완료. 소요 시간: {end_web_search_time - start_web_search_time:.2f}초.\n검색 결과: {search_results}")

# 5. 웹 콘텐츠 가져오기 및 처리.
print("웹 콘텐츠 가져오기 및 처리 중....")
start_content_processing_time = time.time()
processed_content = fetch_and_process_content(llm, search_results, keywords)
end_content_processing_time = time.time()
print(f"웹 콘텐츠 처리 완료. 소요 시간: {end_content_processing_time - start_content_processing_time:.2f}초.\n처리된 콘텐츠: {processed_content}")

# 6. 프롬프트 개선.
print("프롬프트 개선 중....")
start_prompt_refinement_time = time.time()
refined_prompt = refine_prompt_with_content(llm, initial_prompt, processed_content)
end_prompt_refinement_time = time.time()
print(f"프롬프트 개선 완료. 소요 시간: {end_prompt_refinement_time - start_prompt_refinement_time:.2f}초.\n개선된 프롬프트: {refined_prompt}")

# 7. 부정 프롬프트 생성.
print("부정 프롬프트 생성 중....")
start_negative_prompt_time = time.time()
negative_prompt = generate_negative_prompt(llm, refined_prompt)
end_negative_prompt_time = time.time()
print(f"부정 프롬프트 생성 완료. 소요 시간: {end_negative_prompt_time - start_negative_prompt_time:.2f}초.\n부정 프롬프트: {negative_prompt}")

# 8. 모델 파이프라인 초기화.
print("모델 파이프라인 초기화 중....")
accelerator = accelerate.Accelerator()
start_pipeline_initialization_time = time.time()
diffusion_pipeline, chat_pipeline = initialize_pipelines(model_path = MODEL_PATH, hf_token = HF_TOKEN, accelerator = accelerator)
end_pipeline_initialization_time = time.time()
print(f"모델 파이프라인 초기화 완료. 소요 시간: {end_pipeline_initialization_time - start_pipeline_initialization_time:.2f}초.")

# 9. 광고 이미지 생성.
print("광고 이미지 생성 중....")
start_image_generation_time = time.time()
image = generate_image(diffusion_pipeline, refined_prompt, negative_prompt, accelerator)
end_image_generation_time = time.time()
# 이미지가 생성되면, PyTorch 텐서로 변환하고, 이미지를 시각화하기 위해 collage를 생성합니다.
vis_images = [to_tensor(img) for img in image]
output_image = create_collage(vis_images) 
output_image.save("generated_ad_image.png")  # 이미지 저장하기.
print(f"광고 이미지 생성 완료. 소요 시간: {end_image_generation_time - start_image_generation_time:.2f}초.\n생성된 이미지: {image}")

# 10. 생성된 이미지 분석.
print("생성된 이미지 분석 중....")
start_image_analysis_time = time.time()
image_analysis = analyze_image(chat_pipeline, image, accelerator, poster_size[0], poster_size[[1]])
end_image_analysis_time = time.time()
print(f"이미지 분석 완료. 소요 시간: {end_image_analysis_time - start_image_analysis_time:.2f}초.\n이미지 분석 결과: {image_analysis}")

# 11. 광고 문구 생성.
print("광고 문구 생성 중....")
start_ad_copy_generation_time = time.time()
ad_copy = generate_ad_copy(llm, korean_prompt, image_analysis)
end_ad_copy_generation_time = time.time()
print(f"광고 문구 생성 완료. 소요 시간: {end_ad_copy_generation_time:.2f}초.\n생성된 광고 문구: {ad_copy}")

# 전체 소요 시간 계산.
end_time = time.time()
total_time = end_time - start_time
print(f"\n전체 광고 이미지 생성 및 문구 작성 파이프라인 완료. 총 소요 시간: {total_time:.2f}초.")
