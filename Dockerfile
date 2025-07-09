FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 먼저 requirements.txt만 복사 (캐시 효율성을 위해)
COPY requirements.txt /app/

RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir -r requirements.txt

# 나머지 파일들 복사
COPY . /app

EXPOSE 8501

# 실시간 파일 감지를 위한 환경 변수 설정
ENV STREAMLIT_SERVER_FILE_WATCHER_TYPE=poll
ENV STREAMLIT_SERVER_RUN_ON_SAVE=true
ENV STREAMLIT_SERVER_HEADLESS=true

# 개선된 CMD (환경 변수 방식 사용)
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]