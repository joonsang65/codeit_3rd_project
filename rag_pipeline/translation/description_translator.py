# /rag_pipeline/translation/description_translator.py.
from openai import OpenAI

def translate_english_to_korean(llm: OpenAI, english_description: str) -> str:
    """Translates an English description to Korean using an LLM."""
    translator_response_kr = llm.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [
            {
                "role": "system",
                "content": "You are an English-to-Korean translator. Translate the following English text accurately into natural-sounding Korean."
            },
            {
                "role": "user",
                "content": english_description
            }
        ]
    )
    return translator_response_kr.choices[0].message.content
