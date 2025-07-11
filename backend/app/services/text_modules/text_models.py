import os
import time
import asyncio
import hashlib
import json
from openai import AsyncOpenAI

class OpenAIClient:
    def __init__(self):  # .env 파일로 api key 관리해서 유포되지 않게 하기
        # main.py에서 한번만 로드되도록 수정됨
        # base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
        # env_path = os.path.join(base_dir, ".env")
        # load_dotenv(env_path)

        api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError(" !!! need to check .env or path !!! ")  # key가 없거나 파일이 누락된 경우 에러 반환
        
        self.client = AsyncOpenAI(api_key=api_key)  # 비동기 처리 가능한 openai 모델 사용
        self.response_cache = {}  # 캐싱 딕셔너리
    
    def make_cache_key(self, system_prompt, user_prompt, temperature, few_shot_examples):
        payload = {  # 비슷한 입력 들어왔을 때 캐싱된 값을 통해서 자원 절약을 위함
            "system": system_prompt,
            "user": user_prompt,
            "temp": temperature,
            "fewshot": few_shot_examples
        }
        raw = json.dumps(payload, sort_keys=True).encode()
        return hashlib.sha256(raw).hexdigest()  # 각 결과에 대해 hash 키 값으로 저장해둠
    
    async def fetch_response(self, system_prompt, user_prompt, temperature, model="gpt-4.1-mini", few_shot_examples=None):
        """단일 응답 생성"""
        cache_key = self.make_cache_key(system_prompt, user_prompt, temperature, few_shot_examples)
        
        if cache_key in self.response_cache:
            return temperature, self.response_cache[cache_key]["content"], self.response_cache[cache_key]["elapsed"]
        
        messages = [{"role": "system", "content": system_prompt}]
        if few_shot_examples:  # few-shot 예시가 있으면  -> 추후 기능 확장 시에 few-shot 데이터가 없는 경우도 고려함
            messages.extend(few_shot_examples)
        messages.append({"role": "user", "content": user_prompt})
        
        start = time.time()  # 응답시간 로깅용  -> 추후에는 삭제 가능
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )  # 비동기 처리
        elapsed = time.time() - start  # 응답 소요시간 계산  -> 이것도 삭제 가능
        
        content = response.choices[0].message.content.strip()
        self.response_cache[cache_key] = {"content": content, "elapsed": elapsed}
        
        return temperature, content, elapsed
    
    async def generate_multiple_responses(self, system_prompt, user_prompt, model="gpt-4.1-mini", few_shot_examples=None, temperatures=None):
        """여러 온도 설정으로 응답 생성"""
        if temperatures is None:
            temperatures = [0.2, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
        
        tasks = [
            self.fetch_response(system_prompt, user_prompt, temp, model, few_shot_examples)
            for temp in temperatures
        ]
        results = await asyncio.gather(*tasks)  # 비동기 처리
        return results
    
    async def run_generation(self, model_type: str, user_prompt: str, system_prompt: str, few_shot_examples=None):
        """전체 생성 과정 실행"""
        zero_set = time.time()  # 사용자 입력 완료 시간
        model_name = "gpt-4.1-mini" if model_type == "mini" else "gpt-4.1-nano"
        
        results = await self.generate_multiple_responses(
            system_prompt, user_prompt, model=model_name, few_shot_examples=few_shot_examples
        )
        
        print("\n▶ 응답 결과:")
        return results
        # for temp, output, elapsed in results:
        #     print(f"\n🌡 Temperature {temp} (⏱ {elapsed:.2f}초):\n{output}")
        #     print("-" * 50)
        #     return f"\n🌡 Temperature {temp} (⏱ {elapsed:.2f}초):\n{output}"
        
        # last_time = time.time()  # 결과 출력 완료 시간
        # print(f"\n📊 전체 인퍼런스 시간: {(last_time - zero_set):.2f}초")