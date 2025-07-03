# /rag_pipeline/keyword_extraction/extractor.py.
from openai import OpenAI

def extract_keywords(llm: OpenAI, translated_prompt: str) -> str:
    """Extracts keywords for web search from a translated prompt using an LLM."""
    keyword_extractor = llm.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [
            {
                "role": "system",
                "content": """
                You are a keyword extractor for image generation prompts.
                Analyze the user's prompt, which is a translated request for an advertisement image background, and identify the main subject or key keywords that would be most useful for a web search to gather specific details about the subject.
                The subject could be a location (like a beach, city, or landmark), a type of food or drink, or an object.
                Extract only the most relevant terms and present them as a comma-separated list.
                """
            },
            {
                "role": "user",
                "content": translated_prompt
            }
        ]
    )
    return keyword_extractor.choices[0].message.content
