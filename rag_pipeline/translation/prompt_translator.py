# /rag_pipeline/translation/prompt_translator.py.
import os
from openai import OpenAI

def translate_korean_to_english(llm: OpenAI, korean_prompt: str) -> str:
    """Translates a Korean prompt to English using an LLM."""
    try:
        translator_response = llm.chat.completions.create(
            model = "gpt-4o-mini",
            messages = [
                {
                    "role": "system",
                    "content": """
                    You are a Korean-to-English translator who will be translating a user-inputted prompt in Korean about an advertisement-creating request such as how the user wants the background advertisement image generated,
                    under what lighting, the ambiant, the mood, and the setting. Ensure that the user-inputted query is translated as accurately as possible into English and avoid typos at all costs.
                    """
                },
                {
                    "role": "user",
                    "content": korean_prompt
                }
            ]
        )
        return translator_response.choices[0].message.content

    except Exception as e:
        print(f"An error occurred during translation: {e}.")
        return None
