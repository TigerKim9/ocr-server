FROM python:3.11-slim

# Tesseract 및 주요 언어 팩 설치
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    # 동아시아
    tesseract-ocr-eng \
    tesseract-ocr-kor \
    tesseract-ocr-jpn \
    tesseract-ocr-chi-sim \
    tesseract-ocr-chi-tra \
    tesseract-ocr-tha \
    tesseract-ocr-vie \
    # 유럽
    tesseract-ocr-fra \
    tesseract-ocr-deu \
    tesseract-ocr-spa \
    tesseract-ocr-ita \
    tesseract-ocr-por \
    tesseract-ocr-rus \
    tesseract-ocr-pol \
    tesseract-ocr-nld \
    tesseract-ocr-swe \
    tesseract-ocr-nor \
    tesseract-ocr-dan \
    tesseract-ocr-fin \
    tesseract-ocr-ell \
    tesseract-ocr-tur \
    tesseract-ocr-ukr \
    tesseract-ocr-ces \
    tesseract-ocr-ron \
    tesseract-ocr-hun \
    tesseract-ocr-bul \
    tesseract-ocr-hrv \
    tesseract-ocr-slk \
    tesseract-ocr-slv \
    # 중동
    tesseract-ocr-ara \
    tesseract-ocr-heb \
    tesseract-ocr-fas \
    # 남아시아
    tesseract-ocr-hin \
    tesseract-ocr-ben \
    tesseract-ocr-tam \
    tesseract-ocr-tel \
    tesseract-ocr-mar \
    tesseract-ocr-kan \
    tesseract-ocr-mal \
    tesseract-ocr-guj \
    tesseract-ocr-pan \
    tesseract-ocr-urd \
    # 기타
    tesseract-ocr-ind \
    tesseract-ocr-msa \
    tesseract-ocr-fil \
    tesseract-ocr-afr \
    tesseract-ocr-swa \
    && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 파일 복사
COPY main.py .
COPY static/ ./static/

# 포트 노출
EXPOSE 8000

# 서버 실행
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
