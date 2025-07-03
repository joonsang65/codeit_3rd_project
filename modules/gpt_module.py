from openai import OpenAI
from modules.logger import setup_logger

logger = setup_logger(__name__)

class GPTClient:
    def __init__(self, api_key, model_name):
        logger.info(f"Initializing GPTClient with model: {model_name}")
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def chat(self, messages, max_tokens=300):
        logger.debug("Sending chat message to OpenAI")
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=max_tokens
        )
        logger.debug("Received response from OpenAI")
        return response.choices[0].message.content.strip()

    def analyze_ad_plan(self, product_b64, ref_b64):
        sys_prompt = (
            "You are an AI advertisement planner.\n"
            "Given a main product image and an optional reference image, write a Korean ad plan.\n"
            "Describe tone, background, layout, and suggest short copy for a banner."
        )
        user_prompt = [
            {"type": "text", "text": "Product type: Korean food. Context: 광고 배너."},
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{product_b64}"}},
        ]
        if ref_b64:
            user_prompt.append({"type": "image_url", "image_url": {"url": f"data:image/png;base64,{ref_b64}"}})

        return self.chat([
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt}
        ])

    def convert_to_sd_prompt(self, ad_desc):
        style_prompt = (
            "Convert the Korean ad description into a 1-line English prompt suitable for Stable Diffusion v1.5 background generation, "
            "excluding product names, text, or brand mentions."
        )
        return self.chat([
            {"role": "system", "content": style_prompt},
            {"role": "user", "content": ad_desc}
        ], max_tokens=77)

    def analyze_empty_bowl(self, image_b64):
        sys_prompt = "You are an AI image analyst."
        user_prompt = [
            {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
            {"type": "text", "text": "Is there an empty bowl? Is it ready for food insertion?"}
        ]
        return self.chat([
            {"role": "system", "content": sys_prompt},
            {"role": "user", "content": user_prompt}
        ], max_tokens=100)
