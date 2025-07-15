# 텍스트 이미지 생성기

다양한 폰트와 색상을 사용하여 커스터마이징된 텍스트 이미지를 생성하는 웹 애플리케이션입니다

## 주요 기능

*   **다양한 폰트 지원**: 로컬 폰트 및 웹 폰트를 포함한 다양한 폰트를 사용할 수 있습니다
*   **텍스트 커스터마이징**: 텍스트 내용, 폰트 크기, 색상 등을 자유롭게 설정할 수 있습니다
*   **배경 및 테두리 설정**: 이미지의 배경색과 텍스트의 테두리(획) 두께 및 색상을 조절하여 개성 있는 이미지를 만들 수 있습니다
*   **단어별 색상 적용**: 각 단어마다 다른 텍스트 색상 및 테두리 색상을 적용하여 다채로운 표현이 가능합니다
*   **이미지 포맷 선택**: PNG, JPEG 등 다양한 이미지 포맷으로 결과물을 저장할 수 있습니다

## 프로젝트 구조

*   `app.py`: 웹 애플리케이션의 메인 파일 (Streamlit)
*   `downloader.py`: 웹 폰트를 다운로드하고 관리하는 스크립트
*   `fonts.py`: 사용 가능한 폰트 목록과 해당 폰트의 경로(URL 또는 로컬 경로)를 정의
*   `generate.py`: Pillow 라이브러리를 사용하여 텍스트 이미지를 실제로 생성하는 핵심 로직
*   `fonts/`: 로컬 폰트 파일들이 저장되는 디렉토리
*   `downloaded_fonts/`: 웹에서 다운로드된 폰트 파일들이 저장되는 디렉토리
*   `output.png`: 생성된 이미지가 저장되는 기본 경로


### 설치
```bash
pip install -r requirements.txt
```

### 실행 방법

```bash
streamlit run app.py
```

### 실행 예시
<img width="1207" height="537" alt="image" src="https://github.com/user-attachments/assets/5057abcd-c524-49cf-954f-11712610cd6d" />
<img width="946" height="976" alt="image" src="https://github.com/user-attachments/assets/f3567352-e363-48f5-8122-e8e538a3cdc5" />
<img width="960" height="160" alt="image" src="https://github.com/user-attachments/assets/df9ff136-7c8b-45a5-938b-4f0c39c453d4" />

