# RAG 이미지 생성 파이프라인

이 프로젝트는 RAG(Retrieval-Augmented Generation) 이미지 생성 파이프라인을 구현합니다. 한국어 텍스트 프롬프트를 입력받아 영어로 번역하고, 웹 검색을 수행하여 주제에 대한 관련 정보를 수집하며, 검색된 정보를 기반으로 이미지 생성 프롬프트를 개선합니다. 그 다음 OmniGen2 모델을 사용하여 이미지를 생성하고, 생성된 이미지를 분석하며, 분석된 설명을 다시 한국어로 번역합니다. 마지막으로 한국어 광고 문구를 생성합니다.

파이프라인은 더 나은 구성, 유지 관리 및 재사용성을 위해 여러 모듈로 모듈화되어 있습니다.

## 기능

*   한국어 프롬프트를 영어로 번역합니다.
*   관련 정보 수집을 위해 웹 검색을 수행합니다.
*   검색된 정보를 사용하여 이미지 생성 프롬프트를 개선합니다.
*   OmniGen2 모델을 사용하여 이미지를 생성합니다.
*   생성된 이미지를 분석하고 설명을 제공합니다.
*   이미지 설명을 한국어로 번역합니다.
*   한국어 광고 문구를 생성합니다.
*   더 나은 유지 관리를 위한 모듈화된 코드 구조.
*   `.env` 파일을 사용한 API 키 관리.

## 프로젝트 구조

권장되는 프로젝트 구조는 다음과 같습니다.

```bash 
git clone https://github.com/VectorSpaceLab/OmniGen2.git
```
깃허브 복제한 후 `.requirements.txt`에 필요한 라이브러리 설치합니다.
```bash
pip install -r requirements.txt
```

`.env` 파일에 Hugging Face 토큰과 OpenAI API 키를 입력합니다.
```env
HF_TOKEN=여러분의-huggingface-토큰 
OPENAI_API_KEY=여러분의-openai-api-키
```

실행하기:
```bash
python main_pipeline.py
```
## Citation
@article{wu2025omnigen2,
  title={OmniGen2: Exploration to Advanced Multimodal Generation},
  author={Chenyuan Wu and Pengfei Zheng and Ruiran Yan and Shitao Xiao and Xin Luo and Yueze Wang and Wanli Li and Xiyan Jiang and Yexin Liu and Junjie Zhou and Ze Liu and Ziyi Xia and Chaofan Li and Haoge Deng and Jiahao Wang and Kun Luo and Bo Zhang and Defu Lian and Xinlong Wang and Zhongyuan Wang and Tiejun Huang and Zheng Liu},
  journal={arXiv preprint arXiv:2506.18871},
  year={2025}
}