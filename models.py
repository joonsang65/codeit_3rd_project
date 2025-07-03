import os
import time
import asyncio
import hashlib
import json
from dotenv import load_dotenv
from openai import AsyncOpenAI
from prompts import PROMPT_CONFIGS

class OpenAIClient:
    def __init__(self, env_path="/path/to/your/name.env"):
        """OpenAI 클라이언트 초기화"""
        load_dotenv(env_path)
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError(" !!! need to check .env or path !!! ")
        self.client = AsyncOpenAI(api_key=api_key)
        self.response_cache = {}
    
    def make_cache_key(self, system_prompt, user_prompt, temperature, few_shot_examples):
        """캐시 키 생성"""
        payload = {
            "system": system_prompt,
            "user": user_prompt,
            "temp": temperature,
            "fewshot": few_shot_examples
        }
        raw = json.dumps(payload, sort_keys=True).encode()
        return hashlib.sha256(raw).hexdigest()
    
    async def fetch_response(self, system_prompt, user_prompt, temperature, model="gpt-4.1-mini", few_shot_examples=None):
        """단일 응답 생성"""
        cache_key = self.make_cache_key(system_prompt, user_prompt, temperature, few_shot_examples)
        
        if cache_key in self.response_cache:
            return temperature, self.response_cache[cache_key]["content"], self.response_cache[cache_key]["elapsed"]
        
        messages = [{"role": "system", "content": system_prompt}]
        if few_shot_examples:
            messages.extend(few_shot_examples)
        messages.append({"role": "user", "content": user_prompt})
        
        start = time.time()
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature
        )
        elapsed = time.time() - start
        
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
        results = await asyncio.gather(*tasks)
        return results
    
    async def run_generation(self, model_type: str, user_prompt: str, system_prompt: str, few_shot_examples=None):
        """전체 생성 과정 실행"""
        zero_set = time.time()
        model_name = "gpt-4.1-mini" if model_type == "mini" else "gpt-4.1-nano"
        
        results = await self.generate_multiple_responses(
            system_prompt, user_prompt, model=model_name, few_shot_examples=few_shot_examples
        )
        
        print("\n▶ 응답 결과:")
        for temp, output, elapsed in results:
            print(f"\n🌡 Temperature {temp} (⏱ {elapsed:.2f}초):\n{output}")
            print("-" * 50)
        
        last_time = time.time()
        print(f"\n📊 전체 인퍼런스 시간: {(last_time - zero_set):.2f}초")


# --- 프롬프트 설정 ---
system_prompt_insta, few_shot_examples_insta = PROMPT_CONFIGS['instagram']
system_prompt_blog, few_shot_examples_blsystem_prompt_blog = PROMPT_CONFIGS['blog']
system_prompt_poster, few_shot_examples_blsystem_prompt_poster = PROMPT_CONFIGS['poster']
