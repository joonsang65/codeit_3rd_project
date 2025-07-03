import asyncio
from models import OpenAIClient, PROMPT_CONFIGS


def select_option(prompt_msg: str, valid_options: list):
    """입력 유효성 검사"""
    while True:
        user_input = input(prompt_msg).strip().lower()
        if user_input in valid_options:
            return user_input
        print("❌ 잘못된 입력입니다. 다시 선택해주세요.\n")


async def main():
    """메인 실행 함수"""
    try:
        # OpenAI 클라이언트 초기화
        openai_client = OpenAIClient()
        
        # 사용자 입력 받기
        ad_type = select_option(
            "생성할 광고 유형 선택 (instagram / blog / poster): ", 
            ["instagram", "blog", "poster"]
        )
        
        system_prompt, few_shot_examples = PROMPT_CONFIGS[ad_type]
        
        model_type = select_option(
            "모델 유형 선택 (mini / nano): ", 
            ["mini", "nano"]
        )
        
        user_prompt = input(
            "\n🎯 생성할 광고와 제품에 대해 설명해주세요.\n"
            "요구사항이 자세할수록 좋은 결과를 얻을 수 있습니다:\n"
        )
        
        # 광고 생성 실행
        await openai_client.run_generation(
            model_type, user_prompt, system_prompt, few_shot_examples
        )
        
    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {e}")


if __name__ == "__main__":
    asyncio.run(main())