from openai import OpenAI
from typing import List, Dict, Optional, Any
from image_modules.utils import log_execution_time, logger

class GPTClient:
    """
    OpenAI GPT 모델을 활용한 광고 기획, 프롬프트 변환, 이미지 분석 기능을 제공합니다.
    """

    def __init__(self, api_key: str, model_name: str):
        logger.info(f"Initializing GPTClient with model: {model_name}")
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def chat(self, messages: List[Dict[str, Any]], max_tokens: int = 300) -> str:
        """
        OpenAI Chat API에 메시지를 전달하고 응답 텍스트를 반환합니다.

        Args:
            messages: 명령이 담긴 Dict를 List로 감싼형태
                [
                    {
                        "role": "system",
                        "content": "You are an advertisement planner..."
                    },
                    {
                        "role": "user",
                        "content": USER INPUT
                    }
                ]
            max_tokens: 토큰 한계

        Returns:
            str: GPT 응답 텍스트
        """
        try:
            logger.info("Sending message to OpenAI...")
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens
            )
            choice = response.choices[0]
            if not hasattr(choice, "message") or not choice.message.content:
                raise RuntimeError("GPT 응답이 비어 있습니다.")
            content = choice.message.content.strip()
            logger.info("Received response from OpenAI")
            return content
        except Exception as e:
            logger.error(f"Chat API request failed: {e}")
            raise RuntimeError("GPT 응답 실패") from e

    @log_execution_time(label="Generating Ad Plan...")
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

        system_prompt = """
            당신은 창의적인 AI 광고 기획자입니다. 주어진 제품 이미지를 보고 제품의 종류, 특징, 색감, 구성요소를 요약하고, 해당 제품이 돋보일 수 있도록 배경 디자인과 분위기를 제안하세요.

            배경은 Stable Diffusion을 통해 생성될 예정이며, 제품은 이미지에서 보이는 위치에 고정되어 있으므로 배경은 해당 위치를 고려한 구성으로 디자인되어야 합니다.

            선택적으로 참고 이미지가 있을 경우 광고 스타일이나 분위기를 참고하여 유사한 톤이나 무드를 제안할 수 있습니다.

            📌 출력 구성 예시:
            - 제품 요약:
            - 배경 디자인 제안: 최대한 직관적이고 간결하게
            - 광고 분위기 키워드: 
            - 짧은 카피 제안:

            예시는 제공하지 마세요.
            """

        user_prompt: List[Dict[str, Any]] = [
            {"type": "text", "text": f"Product type: {product_type}. Context: {marketing_type}."},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{product_b64}"}},
        ]
        # 간단한 base64 유효성 검사 (PNG 시작 부분 체크)
        if ref_b64 and isinstance(ref_b64, str) and ref_b64.startswith(("iVBOR", "/9j/")):
            user_prompt.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{ref_b64}"}})

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]

        return self.chat(messages)

    @log_execution_time(label="Converting to Prompt...")
    def convert_to_sd_prompt(self, ad_description: str) -> str:
        """
        한글 광고 기획서를 영어 이미지 프롬프트로 변환합니다.
        """
        logger.info("Converting ad plan to Stable Diffusion prompt")

        system_prompt = """
        You are a prompt generator for Stable Diffusion v1.5 inpainting.

        Convert the following Korean advertisement background description into a single, natural English sentence describing only the background scene.

        Exclude product names, brand names, or overlay text. Emphasize product location, mood, lighting, depth, texture, and style to guide realistic image generation.

        Format: [Style or Mood], [Background elements], [Lighting or Material], [Camera angle], [Focus information]

        Output only keywords in a comma-separated list.

        Do not include the information of product, only the background.
        """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": ad_description}
        ]

        result = self.chat(messages, max_tokens=77)

        # 간단한 검증
        if result.count(",") < 2:
            logger.warning("Output prompt seems too short or malformed")

        return result