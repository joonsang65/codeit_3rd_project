# modules/gpt_module.py
from openai import OpenAI
from openai.types.chat import ChatCompletionMessage
from modules.logger import setup_logger
from typing import List, Dict, Optional

logger = setup_logger(__name__)


class GPTClient:
    """
    OpenAI GPT 모델을 활용한 광고 기획, 프롬프트 변환, 이미지 분석 기능을 제공합니다.
    """

    def __init__(self, api_key: str, model_name: str):
        logger.info(f"Initializing GPTClient with model: {model_name}")
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def chat(self, messages: List[Dict], max_tokens: int = 300) -> str:
        """
        OpenAI Chat API에 메시지를 전달하고 응답 텍스트를 반환합니다.
        """
        try:
            logger.debug("Sending message to OpenAI...")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens
            )
            content = response.choices[0].message.content.strip()
            logger.debug("Received response from OpenAI")
            return content
        except Exception as e:
            logger.error(f"Chat API request failed: {e}")
            raise RuntimeError("GPT 응답 실패") from e

    def analyze_ad_plan(
        self,
        product_b64: str,
        ref_b64: Optional[str] = None,
        product_type: str = "food",
        marketing_type: str = "홍보 배너 제작"
    ) -> str:
        """
        제품 이미지(및 참조 이미지)를 기반으로 한 광고 기획안을 생성합니다.
        """
        logger.info("Generating ad plan using GPT")

        system_prompt = (
            "You are an AI advertisement planner.\n"
            "Given a main product image and an optional reference image, write a Korean ad plan.\n"
            "Describe background design and suggest short copy for a banner."
        )

        user_prompt = [
            {"type": "text", "text": f"Product type: {product_type}. Context: {marketing_type}."},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{product_b64}"}},
        ]
        if ref_b64:
            user_prompt.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{ref_b64}"}})

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        return self.chat(messages)

    def convert_to_sd_prompt(self, ad_description: str) -> str:
        """
        한글 광고 기획서를 영어 이미지 프롬프트로 변환합니다.
        """
        logger.info("Converting ad plan to Stable Diffusion prompt")

        system_prompt = (
            "Convert the Korean ad description into a 1-line English prompt suitable for "
            "Stable Diffusion v1.5 background generation. "
            "Exclude product names, text, or brand mentions."
        )

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": ad_description}
        ]

        return self.chat(messages, max_tokens=77)

    def analyze_empty_bowl(self, image_b64: str) -> str:
        """
        이미지에 빈 그릇이 있는지 확인합니다.
        """
        logger.info("Analyzing image for empty bowl")

        system_prompt = "You are an AI image analyst."
        user_prompt = [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
            {"type": "text", "text": "Is there an empty bowl? Is it ready for food insertion?"}
        ]

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        return self.chat(messages, max_tokens=100)
