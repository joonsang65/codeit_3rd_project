# /rag_pipeline/advertisement/copy_generator.py.
from openai import OpenAI

def generate_ad_copy(llm: OpenAI, original_korean_prompt: str, korean_image_description: str) -> str:
    """Generates Korean advertisement copy based on the original prompt and image description."""
    ad_copy_generator = llm.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [
            {
                "role": "system",
                "content": f"""
                You are an advertisement copywriter.
                Your task is to generate compelling and creative advertisement copy in Korean for a small business.
                Use the original advertisement request and the description of the generated image to create the copy.
                Ensure the copy is engaging and encourages the target audience to take action (e.g., visit a place, try a product).
                Original Korean Prompt: {original_korean_prompt}
                Korean Image Description: {korean_image_description}
                """
            },
            {
                "role": "user",
                "content": "Generate advertisement copy in Korean based on the provided information."
            }
        ]
    )
    return ad_copy_generator.choices[0].message.content
