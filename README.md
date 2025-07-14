## 🔧 프로젝트 구조

```
codeit_3rd_project/
├── test_main.py         # 메인 실행 파일
├── requirements.txt     # 필요한 패키지 목록
├── .env                 # API 키 설정 파일 (생성 필요)
└── README.md           # 프로젝트 설명서
```

## 📋 사전 준비

### 1. OpenAI API 키 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 OpenAI API 키를 입력합니다:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

> ⚠️ **보안 주의사항**: API 키는 절대 공개 저장소에 업로드하지 마세요. `.gitignore`에 `.env` 파일을 추가하는 것을 권장합니다.

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

**필요한 패키지:**
- `openai`: OpenAI API 사용을 위한 필수 패키지
- `python-dotenv`: 환경 변수 관리를 위한 패키지

## 🎯 실행 방법

```bash
python test_main.py
```

## 💡 사용 흐름

1. **광고 유형 선택**
   - `instagram`: 인스타그램 광고 문구
   - `blog`: 블로그 광고 문구  
   - `poster`: 포스터 광고 문구

2. **모델 선택**
   - `mini`: GPT-4o-mini 모델
   - `nano`: GPT-4o-nano 모델

3. **제품/서비스 설명 입력**
   - 광고하고자 하는 제품이나 서비스에 대한 상세 설명

4. **결과 확인**
   - 다양한 Temperature 값에 따른 광고 문구가 자동으로 생성됩니다

## 📝 사용 예시

```
생성할 광고 유형 선택 (instagram / blog / poster) : instagram
모델 유형 선택 (mini / nano) : mini
생성할 광고와 제품에 대해 설명해주세요:
> 제주도 자연 속에서 여유를 즐길 수 있는 프라이빗 풀빌라

▶ 응답 결과:

🌡 Temperature 0.2 (⏱ 2.34초):
[정제된 광고 문구 출력]

🌡 Temperature 0.5 (⏱ 2.67초):
[균형잡힌 광고 문구 출력]

🌡 Temperature 0.8 (⏱ 3.12초):
[창의적인 광고 문구 출력]
```