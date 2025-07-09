OmniGen2 설정은 다음과 같습니다:

# 깃허브 레포 클론.
```bash
git clone git@github.com:VectorSpaceLab/OmniGen2.git
cd OmniGen2
```

OmniGen2 복제한 후, 구조는 다음과 같아진다.

```
ad_project/
    ├── __init__.py
    ├── model_dev/
    ├── model_textGen/
    ├── utils/
    ├── main_pipeline.py
    ├── fastapi_main.py
    ├── OmniGen2/
    ├── rag_pipeline/
    ├── README.md
    └── requirements.txt
```

# 2. 파이쏜 가상 환경.
```bash
conda create -n omnigen2 python=3.11
conda activate omnigen2
```

# 의존성 설치.
# 반드시 OmniGen2/ 경로에 설치.
```bash
pip install torch==2.6.0 torchvision --extra-index-url https://download.pytorch.org/whl/cu124
pip install -r requirements.txt
pip install flash-attn==2.7.4.post1 --no-build-isolation
```

# 실행.
```bash
uvicorn fastapi_main:app --host 0.0.0.0 --port 8000
```
