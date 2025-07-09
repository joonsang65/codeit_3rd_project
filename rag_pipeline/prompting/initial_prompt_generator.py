# /rag_pipeline/prompting/initial_prompt_generator.py.
from openai import OpenAI
# 호스트 경로.
from rag_pipeline.utils.timing_utils import timing_decorator

@timing_decorator
def generate_initial_prompt(llm: OpenAI, translated_prompt: str) -> str:
    """Generates an initial English prompt for image generation based on a translated prompt."""
    prompt_generator = llm.chat.completions.create(
        model = "gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """
                You are a prompt generator for image creation.
                Translate the user's request for an advertisement image background, originally translated from Korean, into a detailed English prompt.
                The prompt should describe the scene including setting, lighting, mood, objects, theme, angle, and art style.
                Follow this template: [Subject], [Environment], [Style/Lighting], [Camera/Details], [Artist or Art Style].
                If art style, lighting, or camera details are not specified, use clear lighting, photo-realistic style, and shallow depth of field.
                """
            },
            {
                "role": "user",
                "content": translated_prompt
            }
        ]
    )
    return prompt_generator.choices[0].message.content
