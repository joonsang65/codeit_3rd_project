# 🛍️ AI 광고 이미지 생성기

AI를 활용해 **소상공인을 위한 광고 이미지를 자동으로 생성**해주는 웹 서비스입니다.  
제품 이미지만 업로드하면, 매력적인 배경과 문구를 자동으로 생성하여 광고 이미지를 완성할 수 있습니다.


서비스와 관련된 자료는 아래 링크에서 확인하실 수 있습니다:
- 📄 [최종 프로젝트 보고서](https://www.notion.so/AI-23a8fc4dd92380e99a39c873a9ed342e?source=copy_link)
- 🖼️ [발표용 PPT 자료](https://drive.google.com/file/d/141hq0X4WL3qS-Nc5jcPIgxSSACKmJS3d/view?usp=drive_link)
- 🎥 [시연 영상]() - 넣어야 함
- 📝 [협업 일지 (Notion 정리)](https://www.notion.so/23f8fc4dd92380f5aaedf63d1775262b?source=copy_link)

---

## 주요 기능

### Step-by-Step 광고 생성 워크플로우

1. **Step 1: 제품 이미지 업로드 및 위치 조정**
2. **Step 2: AI 배경 이미지 생성 (inpaint / text2img)**
3. **Step 3: 제품 설명 입력 → 광고 문구 자동 생성 (GPT)**
4. **Step 4: 광고 문구를 이미지로 생성하고 배치**
5. **Step 5: 완성된 이미지 다운로드**

---

## 기술 스택

| 구분       | 기술                             |
|------------|----------------------------------|
| 프론트엔드 | React, Tailwind CSS, Zustand     |
| 백엔드     | FastAPI, Python                  |
| AI 모델    | Stable Diffusion, OpenAI GPT     |
| 기타       | PIL, rembg, Axios, GCP VM        |

---

## 프로젝트 구조

```bash
├── frontend/                # React 기반 프론트엔드
│   ├── public/              # 정적 파일 (HTML, 파비콘 등)
│   ├── src/
│   │   ├── api/             # 백엔드와 통신하는 API 함수 모음
│   │   ├── assets/          # 이미지 및 결과 이미지
│   │   ├── components/      # 재사용 가능한 UI 컴포넌트
│   │   ├── context/         # 글로벌 상태 관리 (예: 인증)
│   │   ├── pages/
│   │   │   ├── Editor/      # 광고 제작 에디터 페이지
│   │   │   │   ├── steps/   # 광고 제작 5단계 UI 컴포넌트
│   │   │   └── ...          # 홈, 로그인 등 기타 페이지
│   │   ├── App.jsx          # 루트 컴포넌트
│   │   └── index.js         # 진입점
│   └── package.json         # 프론트엔드 의존성

├── backend/                 # FastAPI 기반 백엔드
│   ├── app/
│   │   ├── routers/         # API 라우터 정의
│   │   ├── services/        # 비즈니스 로직 및 모델 호출
│   │   │   ├── image_modules/   # 이미지 생성 파이프라인
│   │   │   ├── text_modules/    # 텍스트 생성 및 폰트 처리
│   │   │   ├── TI_modules/      # 텍스트 이미지화(Text2Image) 모듈
│   │   ├── output/          # 이미지 생성 결과물
│   │   └── main.py          # FastAPI 진입점
│
│   ├── crud/                # DB 조작 함수 모음
│   ├── database/            # DB 연결 및 모델 정의
│   ├── schemas/             # Pydantic 기반 요청/응답 스키마
│   ├── utils/               # 보조 유틸 함수 (보안, 파일 저장 등)
│   ├── requirements.txt     # 백엔드 의존성
│   └── .env                 # 환경 변수 설정 파일

├── README.md
└── Dockerfile (선택적으로 사용 예정)
```

---

## 주요 기여자 (Core Contributors)

| 이름 | 역할 |
|------|------|
| 노준상 | 텍스트 생성 모델 개발 <br> 벡앤드 개발 <br> 프론트앤드 개발 <br> 화면 모드 구현 <br> 프로그레스 바 구현|
| 구극모 | 이미지 생성 모델 개발 <br> 이미지 전처리 <br>  학습 인프라 구축 <br>  ONNX 경량화 <br> 백앤드 개발 <br> 프론트앤드 개발 |
| 정재의 | 백엔드 개발 <br> 프론트엔드 개발 <br> UI 구성 <br> 캔버스 구현 <br> 시스템 설계 |
| 임성은 | 전반적인 프로젝트 기획 기여 <br> 문구 생성 기능 개발 (단계 4, 5) <br> 이미지 생성 모델(stable diffusion 등) 비교 및 적용|
| 배동우 | 데이터베이스 +  백엔드 + 프론트엔드  개발 및 연동 <br> 세션 개발 <br> 로그인, 회원 가입, 사용자 인증 개발 <br> 갤러리 사용자 광고 이미지 전시 개발 <br> 상품 이미지 생성(OmniGen2) 개발 |

---

## 💻 설치 및 실행 방법

### 1. 백엔드 실행

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

###  2. 프론트엔드 실행

🛠️ React 프로젝트 실행 가이드 (Node.js 설치부터)
사전 준비
이 프로젝트는 React 기반이며, 실행을 위해 Node.js가 필요합니다.

#### 1. Node.js 설치  
- Node.js 공식 웹사이트 에서 LTS(Long Term Support) 버전을 설치하세요.  
- 권장 버전: Node.js 18.x 이상  
- 설치하면 npm도 함께 설치됩니다.  
 
설치 확인:
```bash
node -v
npm -v
```

#### 2. 프로젝트 클론  
GitHub에서 프로젝트를 내려받고 폴더로 이동합니다:

```bash
git clone https://github.com/joonsang65/codeit_3rd_project.git
cd codeit_3rd_project
```

#### 3. 의존성 설치  
React 프로젝트에 필요한 라이브러리들을 설치합니다:

```bash
npm install # node_modules 폴더 생성
```

#### 4. 개발 서버 실행  
react 폴더 진입 후 npm start

```bash
cd frontend
npm start
```

### 3. 환경 변수 및 설정

* backend/에서 .env 생성한 후 `OPENAI_API_KEY=당신의_OpenAI_API_키` 입력합니다.
* backend/app/services/model_config.yaml 파일에 `openai > api_key_env`를 위와 동일하게 OpenAI API 키를 입력합니다.
* backend/app/routers/에서 .env 생성한 후 `JWT_SECRET_KEY=당신의_JWT_키` 입력합니다.

FastAPI의 URL은 프론트엔드에  
```bash
* frontend/src/api/imageAPI.js
* frontend/src/api/sessionAPI.js
* frontend/src/api/text_images_API.js
* frontend/src/api/textAPI.js
* frontend/src/api/userAPI.js
* frontend/src/pages/Gallery.jsx
* frontend/src/pages/LoginPage.jsx
* frontend/src/pages/RegisterPage.jsx
```

파일들에 설정할 수 있습니다. 반면으로, React의 URL은 backend/app/main.py에서 변경할 수 있습니다.

4. LoRA 파일 설정

   [LoRA 가중치는 여기서 내려받으면 됩니다](https://drive.google.com/file/d/10xvB24UQttPTlBe8tEh3y1GToxuQkc5b/view?usp=sharing)

   내려받아서 압축 풀은 후, backend/app/services에서 "lora"라는 폴더 만들어서(backend/app/services/lora/) LoRA 가중치 파일 6개 다 저장하기 
