# 광고 배너 자동 생성 파이프라인

## Refactoring 진행

## 실행 방법
```<code>
main.py 내부에서 mode 변경으로 'inpring', 'generate' 옵션으로 실행가능

python main.py
```
>전제 조건:
>- ./lora/ 폴더를 생성하고 필요한 .safetensors 파일을 넣어야 합니다.
>- ip_adapter_sd15.bin 파일도 프로젝트 루트에 존재해야 합니다.

## 설정 파일 (config.yaml)
프로젝트의 주요 변수들은 모두 config.yaml에서 관리합니다.
모델 설정, 이미지 크기, LoRA 경로, 프롬프트 설정 등 모든 환경을 설정 가능하게 통합했습니다.

## 주요 변경사항 및 구조 설명
### 프로젝트 디렉토리 구조 예시
```<code>
.
├── main.py
├── config.yaml
├── lora/
│   ├── foodplatters.safetensors
│   └── ...
├── images/
│   ├── food1.jfif
│   ├── style_ref.png
│   └── ...
├── output/
│   ├── debug_output{0}.png
│   ├── ip_gen{1}.png
│   └── ...
└── ip-adapter_sd15.bin
```

1. `config.yaml` 기반 설정 통합
    - 경로, 모델명, 이미지 크기, LoRA 매핑 등 변수들을 설정 파일에 통합하여 유연성 증가.

2. 출력 이미지 비율 다양화
    - 사용자 입력을 고려하여 반영, 추후 backend, frontend 연동 시 입력을 받아 처리하도록 변경 예정 현재는 고정 값 처리.

3. GPT 사용 방식 개선
    - 단일 프롬프트로 바로 SD 프롬프트를 생성하는 대신:
        1. GPT가 광고 기획을 먼저 분석하고,
        2. 해당 내용을 SD v1.5 전용 프롬프트로 압축 변환하는 2단계 방식 채택.
    - 생성형 일 경우:
        1. 예상 기획 준비
        2. 프롬프트로 압축 변환 진행

4. Stable Diffusion 파이프라인 구조 변경
    - 기존: StableDiffusionPipeline → 변경: AutoPipelineForText2Image
    - 이유:
        - StableDiffusionPipeline은 LoRA 가중치 통합이 불안정.
        - AutoPipelineForText2Image는 최신 diffusers에서 권장되는 방식이며, 다양한 커스텀 적용이 쉬움.
    - 추가 변경 사항: 'inprint'의 분기를 추가로 하여 StableDiffusionInpaintPipeline 모델 추가

5. 배경과 제품 이미지의 합성 기능
    - IP-Adapter 적용으로 생성된 배경과 배경을 제거한 제품 이미지의 합성이 가능해 졌다.
    - 단, 품질이 떨어지는 현상이 있어서 smoothing과정 혹은 denoise과정이 필요할 것으로 판단된다.

6. 결과 이미지 저장
    - 결과물은 ./output/ 디렉토리에 결과별로 저장됨:
        - debug_output.png
        - ip_gen.png
        - inprint_gen.png
