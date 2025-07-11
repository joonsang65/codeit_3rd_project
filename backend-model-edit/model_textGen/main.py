import asyncio
from model_textGen.models import OpenAIClient
from model_textGen.prompts import PROMPT_CONFIGS
from typing import Literal, Annotated

def select_option(prompt_msg: str, valid_options: list):
    """입력 유효성 검사"""
    while True:
        user_input = input(prompt_msg).strip().lower()
        if user_input in valid_options:
            return user_input
        print("❌ 잘못된 입력입니다. 다시 선택해주세요.\n")


async def main(ad_type: Literal["instagram", "blog", "poster"] = "instagram",
               user_prompt: Annotated[str, "사용자 입력 프롬프트 문자열."] = ""):
    """메인 실행 함수"""
    try:
        # OpenAI 클라이언트 초기화
        openai_client = OpenAIClient()
        
        system_prompt, few_shot_examples = PROMPT_CONFIGS[ad_type]
        
        # 광고 생성 실행
        responses = await openai_client.run_generation(
            user_prompt, system_prompt, few_shot_examples
        )

        return responses
        
    except Exception as e:
        print(f"❌ 오류가 발생했습니다: {e}")


if __name__ == "__main__":
    asyncio.run(main())