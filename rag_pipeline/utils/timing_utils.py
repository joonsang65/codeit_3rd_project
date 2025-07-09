# /rag_pipeline/utils/timing_utils.py
import functools, time

def timing_decorator(func):
    """함수 실행 시간을 측정하는 데코레이터입니다."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        # 로그 출력.
        print()
        print("***" * 20, f"실행하는 함수: {func.__name__}. 소요 시간: {elapsed_time:.4f}초.", "***" * 20)
        return result
    return wrapper