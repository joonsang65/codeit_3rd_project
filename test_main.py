import asyncio
import traceback
from main import generate_ad_texts  # FastAPI와 공유하는 core 함수

def get_user_input() -> tuple:
    """
    콘솔에서 사용자 입력을 받아 광고 생성 요청 파라미터로 반환하는 함수.

    Returns:
        tuple: (ad_type, mode_input, product_name, product_use, brand_name, extra_info)
    """
    ad_type = input("생성할 광고 유형 선택 (인스타그램, 블로그, 포스터): ").strip()
    
    if ad_type in ["인스타그램", "블로그"]:
        mode_input = input("모드 선택 (1: 광고 문구만 생성, 2: 광고 문구 + 텍스트 이미지용 문구 생성): ").strip()
    else:
        mode_input = None
    
    product_name = input("📦 상품 이름을 입력하세요: ").strip()
    product_use = input("🎯 상품 용도를 입력하세요: ").strip()
    brand_name = input("🏷️ 브랜드명을 입력하세요: ").strip()
    extra_info = input("✍️ 추가 정보가 있으면 입력하세요 (없으면 엔터): ").strip() or None

    return ad_type, mode_input, product_name, product_use, brand_name, extra_info


async def main():
    """
    콘솔 기반 광고 문구 생성 테스트 메인 루프.
    generate_ad_texts() 함수를 호출하여 결과를 출력함.
    """
    try:
        ad_type, mode_input, product_name, product_use, brand_name, extra_info = get_user_input()

        print("\n🔍 테스트 입력 요약:")
        print(f"- 광고 유형: {ad_type}")
        print(f"- 모드: {mode_input or '포스터 (기본 모드)'}")
        print(f"- 상품명: {product_name}")
        print(f"- 용도: {product_use}")
        print(f"- 브랜드: {brand_name}")
        print(f"- 추가 정보: {extra_info or '없음'}")

        results = await generate_ad_texts(
            ad_type=ad_type,
            mode_input=mode_input,
            product_name=product_name,
            product_use=product_use,
            brand_name=brand_name,
            extra_info=extra_info
        )

        print("\n📢 생성 결과")
        for temp in sorted({t for outputs in results.values() for t, _, _ in outputs}):
            print(f"\n[Temperature: {temp}]")
            for platform, outputs in results.items():
                for tp, content, elapsed in outputs:
                    if tp == temp:
                        print(f"\n📌 {platform}")
                        print(content)
                        print(f"⏱ 응답 시간: {elapsed:.2f}초\n")
            print("-" * 60)

    except Exception as e:
        print(f"\n❌ 테스트 중 오류 발생: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    if not asyncio.get_event_loop().is_running():
        asyncio.run(main())
    else:
        print("⚠️ asyncio 이벤트 루프가 이미 실행 중입니다. 주피터 등에서 main()을 직접 실행해주세요.")
