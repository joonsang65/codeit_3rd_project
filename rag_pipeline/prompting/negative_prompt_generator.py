# /rag_pipeline/prompting/negative_prompt_generator.py.
from openai import OpenAI

def generate_negative_prompt(llm: OpenAI, translated_prompt: str, general_negative_prompt: str) -> str:
    """Generates dynamic negative prompt terms based on a translated prompt and combines with a general negative prompt."""
    dynamic_negative_prompt_generator = llm.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [
            {
                "role": "system",
                "content": """
                You are a negative prompt generator for image creation.
                Based on the following positive prompt (a request for an advertisement image background), identify potential undesirable elements or qualities specific to the subject or scene that should be avoided in the generated image.
                Provide these as a comma-separated list of terms or phrases to be used in a negative prompt.
                Focus on aspects that could detract from a positive advertisement image, such as unnatural features, incorrect details for the subject, or poor visual representation.
                """
            },
            {
                "role": "user",
                "content": f"Positive prompt: {translated_prompt}"
            }
        ]
    )
    dynamic_negative_terms = dynamic_negative_prompt_generator.choices[0].message.content
    return general_negative_prompt + ", " + dynamic_negative_terms
