# /rag_pipeline/web_tools/search.py.
from googlesearch import search
from typing import List
# 호스트 경로.
from rag_pipeline.utils.timing_utils import timing_decorator

@timing_decorator
def perform_web_search(query: str, num_results: int = 5) -> List[str]:
    """Performs a web search and returns a list of result URLs."""
    results = []
    # The 'search' function from googlesearch takes 'num' as the argument for the number of results.
    for url in search(query, num = num_results):
        results.append(url)
    return results
