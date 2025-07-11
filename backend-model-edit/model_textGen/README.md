## ✅ 실행 방법

### 1. OpenAI API 키 설정
`.env` 파일 또는 직접 지정된 경로에 OpenAI API 키를 등록해야 합니다.

예시 (`/content/drive/MyDrive/junsang.env`):

---
### 2. Python 패키지 설치
```bash
pip install -r requirements.txt

openai : 필수 패키지
python-dotenv : api 키 관리 위함 -> .env 만들어서 openai api 키 관리 추천
```

---
## 🪄 실행
```bash
python main.py
```

실행 후, 다음과 같은 흐름으로 진행됩니다:

생성할 광고 유형 선택 (instagram / blog / poster)
사용할 모델 선택 (mini / nano)
제품/서비스 설명 입력

-> 다양한 temperature 값에 따른 광고 문구 자동 출력

---
## 💬 예시 출력
```
생성할 광고 유형 선택 (instagram / blog / poster) : instagram
모델 유형 선택 (mini / nano) : mini
생성할 광고와 제품에 대해 설명해주세요:
> 제주도 자연 속에서 여유를 즐길 수 있는 프라이빗 풀빌라

▶ 응답 결과:

🌡 Temperature 0.2 (⏱ 2.34초):
[정제된 광고 문구 출력]
```
