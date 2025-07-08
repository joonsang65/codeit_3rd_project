# 폴더 구조
fastapi-backend/
├── main.py
├── routers/
│   ├── generate.py       # 생성 관련 API
│   ├── upload.py         # 업로드 처리
│   └── gallery.py        # 결과 이미지 제공
├── utils/
│   ├── generator.py      # 이미지 생성 로직
│   └── file_utils.py     # 파일 저장/로드 유틸
├── results/              # 생성된 이미지 저장 폴더
└── uploads/              # 업로드된 이미지 저장 폴더

# 핵심 기능
1. 이미지 생성 요청	
POST	
/generate	
AI 광고 이미지 생성

2. 생성된 이미지 목록 조회
GET	
/results	
result 폴더의 이미지 목록 반환

3. 이미지 다운로드
GET	
/results/{filename}	
생성된 이미지 반환

4. 업로드 이미지 저장
POST	
/upload	
사용자가 업로드한 이미지 저장