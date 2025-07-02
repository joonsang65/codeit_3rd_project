from prompts import PROMPT_CONFIGS
from models import run_generation

def select_option(prompt_msg: str, valid_options: list):
    while True:
        user_input = input(prompt_msg).strip().lower()
        if user_input in valid_options:
            return user_input
        print("❌ 잘못된 입력입니다. 다시 선택해주세요.\n")


def main():
    # 광고 유형 선택
    ad_type = select_option("생성할 광고 유형 선택 (instagram / blog / poster): ", ["instagram", "blog", "poster"])
    system_prompt, few_shot_examples = PROMPT_CONFIGS[ad_type]

    # 모델 선택
    model_type = select_option("모델 유형 선택 (mini / nano): ", ["mini", "nano"])

    # 사용자 프롬프트 입력
    user_prompt = input("\n🎯 생성할 광고와 제품에 대해 설명해주세요.\n요구사항이 자세할수록 좋은 결과를 얻을 수 있습니다:\n")

    run_generation(model_type, user_prompt, system_prompt, few_shot_examples)


if __name__ == "__main__":
    main()
