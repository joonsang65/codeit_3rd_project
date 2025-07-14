import os, time, asyncio, hashlib, json
from dotenv import load_dotenv
from openai import AsyncOpenAI
import logging
from typing import List, Optional, Tuple, Dict, Any
from config import DEFAULT_MODEL, DEFAULT_TEMPERATURES, DEFAULT_ENV_PATH, PROMPT_CONFIGS

class OpenAIClient:
    def __init__(self, env_path=DEFAULT_ENV_PATH):
        """
        Args:
            env_path (str): .env 파일 경로, 기본값은 DEFAULT_ENV_PATH

        Returns:
            None
        """
        load_dotenv(env_path)
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key is None:
            raise ValueError(" !!! need to check .env or path !!! ")
        self.client = AsyncOpenAI(api_key=api_key)
        self.response_cache = {}

    def make_cache_key(self, system_prompt, user_prompt, temperature, few_shot_examples):
        """
        Args:
            system_prompt (str): 시스템 프롬프트 텍스트
            user_prompt (str): 사용자 프롬프트 텍스트
            temperature (float): 온도값
            few_shot_examples (list or None): few-shot 예시 메시지 리스트

        Returns:
            str: 캐시 키로 사용할 SHA256 해시 문자열
        """
        payload = {
            "system": system_prompt,
            "user": user_prompt,
            "temp": temperature,
            "fewshot": few_shot_examples
        }
        raw = json.dumps(payload, sort_keys=True).encode()
        return hashlib.sha256(raw).hexdigest()


    async def fetch_response(
        self,
        system_prompt: str,
        user_prompt: str,
        temperature: float,
        model: str,
        few_shot_examples: Optional[List[Dict[str, str]]] = None
    ) -> Tuple[float, str, float]:
        """
        OpenAI API를 통해 응답을 가져오고, 캐시를 활용해 중복 요청을 방지함.

        Args:
            system_prompt (str): 시스템 프롬프트
            user_prompt (str): 유저 입력 프롬프트
            temperature (float): 생성 다양성 조절 파라미터
            model (str): 사용할 OpenAI 모델 이름
            few_shot_examples (list): few-shot 예제 메시지 (optional)

        Returns:
            tuple: (temperature, 생성된 텍스트, 응답 소요 시간)
        """
        try:
            cache_key = self.make_cache_key(system_prompt, user_prompt, temperature, few_shot_examples)
            if cache_key in self.response_cache:
                return (
                    temperature,
                    self.response_cache[cache_key]["content"],
                    self.response_cache[cache_key]["elapsed"],
                )

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

        except Exception as e:
            logging.error(f"[fetch_response] 오류 발생: {e}", exc_info=True)
            raise

    async def generate_texts(
        self,
        platforms: List[str],
        product_name: str,
        product_use: str,
        brand_name: str,
        extra_info: Optional[str],
        mode: str
    ) -> Dict[str, str]:
        """
        단일 temperature로 광고 문구를 생성하는 함수.

        Args:
            platforms (list): 생성 대상 플랫폼 리스트
            product_name (str): 상품 이름
            product_use (str): 상품 용도
            brand_name (str): 브랜드명
            extra_info (str): 추가 정보 (optional)
            mode (str): 생성 모드 ("광고 문구만 생성", ...)

        Returns:
            dict: {플랫폼: 생성된 광고 문구}
        """
        try:
            results = {}
            total_elapsed = []

            prompt_parts = [
                f"상품 이름: {product_name}",
                f"상품 용도: {product_use}",
                f"브랜드명: {brand_name}",
            ]
            if extra_info:
                prompt_parts.append(f"추가 정보: {extra_info}")
            user_prompt = "\n".join(prompt_parts)

            if mode == "광고 문구만 생성":
                for platform in platforms:
                    system_prompt, few_shot_examples = PROMPT_CONFIGS[platform]
                    _, content, elapsed = await self.fetch_response(
                        system_prompt, user_prompt, temperature=0.7, model=DEFAULT_MODEL["mini"], few_shot_examples=few_shot_examples
                    )
                    results[platform] = content
                    total_elapsed.append(elapsed)
            else:
                if any(p in ["인스타그램", "블로그"] for p in platforms):
                    for platform in platforms:
                        if platform in ["인스타그램", "블로그"]:
                            system_prompt, few_shot_examples = PROMPT_CONFIGS[platform]
                            _, content, elapsed = await self.fetch_response(
                                system_prompt, user_prompt, temperature=0.7, model=DEFAULT_MODEL["mini"], few_shot_examples=few_shot_examples
                            )
                            results[platform] = content
                            total_elapsed.append(elapsed)

                    # 포스터 추가 생성
                    system_prompt_포스터, few_shot_examples_포스터 = PROMPT_CONFIGS["포스터"]
                    _, content_포스터, elapsed_포스터 = await self.fetch_response(
                        system_prompt_포스터, user_prompt, temperature=0.7, model=DEFAULT_MODEL["mini"], few_shot_examples=few_shot_examples_포스터
                    )
                    results["포스터"] = content_포스터
                    total_elapsed.append(elapsed_포스터)
                else:
                    if "포스터" in platforms:
                        system_prompt, few_shot_examples = PROMPT_CONFIGS["포스터"]
                        _, content, elapsed = await self.fetch_response(
                            system_prompt, user_prompt, temperature=0.7, model=DEFAULT_MODEL["mini"], few_shot_examples=few_shot_examples
                        )
                        results["포스터"] = content
                        total_elapsed.append(elapsed)

            print(f"\n📊 전체 인퍼런스 시간: {max(total_elapsed):.2f}초")
            return results

        except Exception as e:
            logging.error(f"[generate_texts] 오류 발생: {e}", exc_info=True)
            raise

    async def generate_multiple_responses(
        self,
        platforms: List[str],
        product_name: str,
        product_use: str,
        brand_name: str,
        extra_info: Optional[str] = None,
        mode: str = "광고 문구만 생성",
        temperatures: Optional[List[float]] = None
    ) -> Dict[str, List[Tuple[float, str, float]]]:
        """
        여러 temperature 조합으로 광고 문구를 병렬로 생성하는 함수.

        Args:
            platforms (list): 대상 플랫폼 리스트
            product_name (str): 상품 이름
            product_use (str): 상품 용도
            brand_name (str): 브랜드명
            extra_info (str): 추가 정보 (optional)
            mode (str): 생성 모드
            temperatures (list): 사용할 temperature 값 리스트 (optional)

        Returns:
            dict: {플랫폼: [(temp, 생성된 문구, 응답 시간)]}
        """
        try:
            if temperatures is None:
                temperatures = DEFAULT_TEMPERATURES

            results = {}

            prompt_parts = [
                f"상품 이름: {product_name}",
                f"상품 용도: {product_use}",
                f"브랜드명: {brand_name}",
            ]
            if extra_info:
                prompt_parts.append(f"추가 정보: {extra_info}")
            user_prompt = "\n".join(prompt_parts)

            async def fetch_for_platform(system_prompt, few_shot_examples):
                tasks = [
                    self.fetch_response(system_prompt, user_prompt, temp, DEFAULT_MODEL["mini"], few_shot_examples)
                    for temp in temperatures
                ]
                return await asyncio.gather(*tasks)

            async def fetch_platform(platform: str):
                if platform == "포스터":
                    system_prompt, few_shot_examples = PROMPT_CONFIGS["포스터"]
                else:
                    system_prompt, few_shot_examples = PROMPT_CONFIGS.get(platform, ("", []))
                return platform, await fetch_for_platform(system_prompt, few_shot_examples)

            if mode == "광고 문구만 생성":
                platforms_to_fetch = platforms
            else:
                if any(p in ["인스타그램", "블로그"] for p in platforms):
                    platforms_to_fetch = [p for p in platforms if p in ["인스타그램", "블로그"]] + ["포스터"]
                else:
                    platforms_to_fetch = ["포스터"] if "포스터" in platforms else []

            start_time = time.time()
            fetch_tasks = [fetch_platform(p) for p in platforms_to_fetch]
            results_list = await asyncio.gather(*fetch_tasks)

            for platform, res in results_list:
                results[platform] = res

            print(f"\n📊 전체 인퍼런스 시간: {time.time() - start_time:.2f}초")
            return results

        except Exception as e:
            logging.error(f"[generate_multiple_responses] 오류 발생: {e}", exc_info=True)
            raise