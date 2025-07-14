from prompts import (
    system_prompt_insta,
    system_prompt_blog,
    system_prompt_TI,
    few_shot_examples_insta,
    few_shot_examples_blog,
    few_shot_examples_TI
)

# 광고 유형별 시스템 프롬프트 및 few-shot 구성
PROMPT_CONFIGS = {
    "인스타그램": (system_prompt_insta, few_shot_examples_insta),
    "블로그": (system_prompt_blog, few_shot_examples_blog),
    "포스터": (system_prompt_TI, few_shot_examples_TI),
}

# 기본 온도값 목록
DEFAULT_TEMPERATURES = [0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

# 모델 이름 매핑
DEFAULT_MODEL = {
    "mini": "gpt-4.1-mini",
}

# 기본 환경 변수 경로
DEFAULT_ENV_PATH = "./junsang.env"
