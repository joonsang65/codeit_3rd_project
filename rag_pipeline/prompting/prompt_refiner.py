# /rag_pipeline/prompting/prompt_refiner.py.
from openai import OpenAI
from typing import List

def refine_prompt_with_content(llm: OpenAI, initial_prompt: str, extracted_info: str) -> str:
    """Refines an initial prompt using extracted information from web content."""
    prompt_refiner_with_content = llm.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [
            {
                "role": "system",
                "content": f"""
                You are a prompt refiner for image generation. You will be given an initial prompt translated from Korean and extracted relevant information about the subject from web searches.
                Your task is to refine the initial prompt by incorporating the extracted details to make the image generation prompt more accurate and detailed.
                Pay close attention to the presence or absence of specific elements mentioned in the extracted information.
                The refined prompt should follow the template: [Subject], [Environment], [Style/Lighting], [Camera/Details], [Artist or Art Style].
                Initial prompt: {initial_prompt}
                Extracted information about the subject: {extracted_info}
                """
            },
            {
                "role": "user",
                "content": "Refine the initial prompt based on the extracted information."
            }
        ]
    )
    return prompt_refiner_with_content.choices[0].message.content
