# 광고 배너 자동 생성 파이프라인

## 실행 방법
```<code>
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
│   └── style_ref.png
├── out/
│   └── final_square.png ...
└── ip-adapter_sd15.bin
```

1. `config.yaml` 기반 설정 통합
    - 경로, 모델명, 이미지 크기, LoRA 매핑 등 변수들을 설정 파일에 통합하여 유연성 증가.

2. 출력 이미지 비율 다양화
    - 정사각형, 가로형, 세로형 광고 이미지 모두 출력.
    - 현재는 resize() 방식으로 크기 변환하지만, 추후 Stable Diffusion 생성 시점부터 비율 조정(height/width) 하도록 변경 예정.

3. GPT 사용 방식 개선
    - 단일 프롬프트로 바로 SD 프롬프트를 생성하는 대신:
        1. GPT가 광고 기획을 먼저 분석하고,
        2. 해당 내용을 SD v1.5 전용 프롬프트로 압축 변환하는 2단계 방식 채택.

4. Stable Diffusion 파이프라인 구조 변경
    - 기존: StableDiffusionPipeline → 변경: AutoPipelineForText2Image
    - 이유:
        - StableDiffusionPipeline은 LoRA 가중치 통합이 불안정.
        - AutoPipelineForText2Image는 최신 diffusers에서 권장되는 방식이며, 다양한 커스텀 적용이 쉬움.

5. 배경과 제품 이미지의 합성 기능
    - 생성된 배경 이미지에 빈 그릇이 있는 경우 또는 음식이 없는 경우, 제품 이미지(배경 제거된)를 합성하는 기능 추가.
    - 단, 해당 기능은 아직 미완성이며 AutoPipelineForText2Image 전환 이후 정상 동작하지 않는 이슈 있음.

6. IP-Adapter 적용
    - 최종 단계에서 IP-Adapter를 활용하여 제품 이미지와 배경을 조화롭게 결합.
    - 위치 조정 등 세밀한 조정 가능 (추후 개선 예정).

7. 결과 이미지 저장
    - 결과물은 ./out/ 디렉토리에 비율별로 저장됨:
        - final_square.png
        - final_landscape.png
        - final_portrait.png
