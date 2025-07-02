import os
from dotenv import load_dotenv
from openai import OpenAI
import time

# .env에서 api 키 가져오기  -> 경로 수정 필수
load_dotenv("/path/to/your/name.env")
api_key = os.getenv("OPENAI_API_KEY")
if api_key is None:
    raise ValueError(" !!! need to check .env or path !!! ")

client = OpenAI(api_key=api_key)


# 임베딩 함수 정의
def get_embedding(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

# 임베딩 길이 확인
text_for_embedding = "FastAPI는 Python 기반 웹 프레임워크입니다."
embedding_vector = get_embedding(text_for_embedding)
print("\n✅ 임베딩 벡터 길이:", len(embedding_vector))


# 생성 모델 정의 (base : gpt-4.1-mini)
def generate_multiple_responses(system_prompt: str, user_prompt: str, model = "gpt-4.1-mini", few_shot_examples=None, temperatures=None):
    if temperatures is None:
        temperatures = [0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]

    results = []
    for temp in temperatures:
        messages = [{"role": "system", "content": system_prompt}]
        if few_shot_examples:
            messages.extend(few_shot_examples)
        messages.append({"role": "user", "content": user_prompt})

        start_time = time.time()  # 시작

        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temp,
        )  # 응답 생성

        end_time = time.time()  # 종료
        elapsed = end_time - start_time  # 소요 시간 (초)
        content = response.choices[0].message.content.strip()
        results.append((temp, content, elapsed))

    return results


# 실행 함수
def run_generation(model_type: str, user_prompt: str, system_prompt: str, few_shot_examples=None):
    model_name = "gpt-4.1-mini" if model_type == "mini" else "gpt-4.1-nano"
    outputs = generate_multiple_responses(system_prompt, user_prompt, model=model_name, few_shot_examples=few_shot_examples)

    total_time = 0
    print("▶ 응답 결과:")
    for temp, output, elapsed in outputs:
        print(f"\n🌡 Temperature {temp} (⏱ {elapsed:.2f}초):\n{output}")
        print("-" * 50)
        total_time += elapsed
    print(f"average elapsed time : {total_time/len(outputs):.2f} sec")
