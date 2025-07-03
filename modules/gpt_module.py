from openai import OpenAI
from modules.logger import setup_logger

logger = setup_logger(__name__)

class GPTClient:
    """
    OpenAI GPT 모델을 활용한 광고 기획, 프롬프트 변환, 이미지 분석을 수행하는 클라이언트 클래스입니다.
    """

    def __init__(self, api_key, model_name):
        """
        GPTClient 초기화 함수.

        Args:
            api_key (str): OpenAI API 키.
            model_name (str): 사용할 GPT 모델 이름.
        """
        logger.info(f"Initializing GPTClient with model: {model_name}")
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def chat(self, messages, max_tokens=300):
        """
        주어진 메시지로 GPT 모델과 대화하고 응답을 반환합니다.

        Args:
            messages (list): 대화 메시지 목록 (system/user format).
            max_tokens (int): 최대 토큰 수.

        Returns:
            str: 모델의 응답 텍스트.
        """
        logger.debug("Sending chat message to OpenAI")
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=max_tokens
        )
        logger.debug("Received response from OpenAI")
        return response.choices[0].message.content.strip()

    def analyze_ad_plan(self, product_b64, ref_b64, product_type="food", marketing_type="홍보 배너 제작"):
        """
        제품 이미지와 참조 이미지(선택)에 기반해 한국어 광고 기획안을 생성합니다.

        Args:
            product_b64 (str): base64로 인코딩된 제품 이미지.
            ref_b64 (str): base64로 인코딩된 참조 이미지 (옵션).
            product_type (str): 제품 유형.
            marketing_type (str): 마케팅 목적.

        Returns:
            str: 광고 기획안 텍스트.
        """
        sys_prompt = (
            "You are an AI advertisement planner.\n"
            "Given a main product image and an optional reference image, write a Korean ad plan.\n"
            "Describe tone, background, layout, and suggest short copy for a banner."
        )
        user_prompt = [
            {"type": "text", "text": f"Product type: {product_type}. Context: {marketing_type}."},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{product_b64}"}},
        ]
        if ref_b64:
            user_prompt.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{ref_b64}"}})

        return self.chat([
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt}
        ])

    def convert_to_sd_prompt(self, ad_desc):
        """
        한국어 광고 설명을 Stable Diffusion v1.5용 영어 프롬프트로 변환합니다.

        Args:
            ad_desc (str): 한국어 광고 설명.

        Returns:
            str: Stable Diffusion에 적합한 영어 프롬프트.
        """
        style_prompt = (
            "Convert the Korean ad description into a 1-line English prompt suitable for Stable Diffusion v1.5 background generation, "
            "excluding product names, text, or brand mentions."
        )
        return self.chat([
            {"role": "system", "content": style_prompt},
            {"role": "user", "content": ad_desc}
        ], max_tokens=77)

    def analyze_empty_bowl(self, image_b64):
        """
        이미지에 빈 그릇이 있는지 분석하여 음식 삽입 가능 여부를 판단합니다.

        Args:
            image_b64 (str): base64로 인코딩된 이미지.

        Returns:
            str: 분석 결과 텍스트.
        """
        sys_prompt = "You are an AI image analyst."
        user_prompt = [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
            {"type": "text", "text": "Is there an empty bowl? Is it ready for food insertion?"}
        ]
        return self.chat([
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt}
        ], max_tokens=100)
