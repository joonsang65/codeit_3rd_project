# 실행 방법

```<code>
# 1번 실행 방법
gen_ad = create_ad_background(
    product_img_path='food1.jfif',                                   # 입력 이미지
    product_type='Korean Food',                                     # 제품 설명
    marketing_context = "김치찌개 홍보 배너",                 # 마케팅 문구
    reference_img_path = 'ad_image.jfif',                         # 참고 이미지 (선택)
    save_path = 'save_temp.png'                                     # 결과 이미지 저장 경로
) 
```
```<code
# 2번 실행방법 (미완성)
gen_ad = create_ad(
            user_img_path="food1.jfif",
            product_type="Korean food",
            marketing_context="한식 김치찌개 홍보 배너",
            mode="background"                                         # or "ip_adapter"
        )
```
