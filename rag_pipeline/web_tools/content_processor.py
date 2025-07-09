# /rag_pipeline/web_tools/content_processor.py.
import requests
from bs4 import BeautifulSoup
from typing import List
from openai import OpenAI
# 호스트 경로.
from rag_pipeline.utils.timing_utils import timing_decorator

@timing_decorator
def fetch_and_process_content(llm: OpenAI, urls: List[str], extracted_keywords: str, max_text_length: int = 2000, num_urls_to_process: int = 5) -> str:
    """Fetches and processes text content from URLs and extracts relevant information using an LLM."""
    keyword_text_content = []
    processed_count = 0
    for url in urls:
        if processed_count >= num_urls_to_process:
            break
        try:
            response = requests.get(url, timeout = 10)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx).
            soup = BeautifulSoup(response.content, "html.parser")

            # Extract text from common tags that might contain main content.
            text = " ".join([p.get_text() for p in soup.find_all(["p", "div"])]).replace("\n", " ").replace("\t", " ").strip()
            # Truncate the text content to a manageable size.
            keyword_text_content.append(text[:max_text_length]) # Adjust truncation length as needed.
            processed_count += 1

        except requests.exceptions.RequestException as e:
            print(f"Could not retrieve content from {url}: {e}.")
        except Exception as e:
            print(f"An error occurred while processing {url}: {e}.")

    if not keyword_text_content:
        return "No relevant content could be extracted from the provided URLs."

    # Use LLM to extract relevant information.
    extracted_keyword_info = llm.chat.completions.create(
        model = "gpt-4o-mini",
        messages = [
            {
                "role": "system",
                "content": f"""
                You are an information extractor for image generation prompts.
                You will receive raw text content from web searches about a subject.
                Your task is to identify and extract key details relevant to generating an image of that subject.
                Focus on aspects such as landmarks, atmosphere, typical activities, and the presence or absence of specific natural elements.
                Present the extracted information in a clear and concise manner.
                The subject is: {extracted_keywords}
                """
            },
            {
                "role": "user",
                "content": f"Extract relevant information about {extracted_keywords} from the following text content: {keyword_text_content}"
            }
        ]
    )

    return extracted_keyword_info.choices[0].message.content

