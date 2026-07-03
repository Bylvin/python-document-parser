FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y \
        tesseract-ocr \
        tesseract-ocr-ind \
        tesseract-ocr-eng \
        poppler-utils \
        libgl1 \
        libglib2.0-0 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Pakai Tesseract (CLI di atas) sebagai engine OCR Docling di dalam container.
# Di lokal (tanpa env ini) tetap default "auto" / EasyOCR.
ENV OCR_ENGINE=tesseract \
    OCR_LANG=ind,eng

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn","main:application","--host","0.0.0.0","--port","8000"]
