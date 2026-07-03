from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Document Parser API"
    VERSION:str = "0.0.1"
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 104857600

    # OCR engine Docling: "auto" (EasyOCR, tanpa dependency eksternal) atau
    # "tesseract" (memakai Tesseract via container Docker lewat wrapper di bawah).
    OCR_ENGINE: str = "tesseract"
    # Bahasa OCR utk Tesseract, dipisah koma (mis. "eng" atau "ind,eng").
    OCR_LANG: str = "ind,eng"
    # Wrapper yang menjembatani Docling -> Tesseract di container (relatif ke root
    # project). Hanya dipakai saat OCR_ENGINE=tesseract.
    TESSERACT_CMD: str = "tesseract-docker.cmd"
    # Folder temp OCR yang di-mount ke container tesseract (lihat docker-compose).
    OCR_TMP_DIR: str = ".ocr_tmp"

    # Kendali paralelisme Docling untuk menekan memori puncak (hindari
    # std::bad_alloc saat me-render halaman besar). Set ke nilai kecil bila RAM
    # terbatas / dokumen punya halaman beresolusi tinggi.
    #   DOCLING_NUM_THREADS: 0 = otomatis (jumlah core CPU).
    #   DOCLING_BATCH_SIZE : 0 = pakai default Docling; >0 = batas halaman/region
    #                        yang diproses bersamaan (mis. 1 = paling hemat memori).
    DOCLING_NUM_THREADS: int = 0
    DOCLING_BATCH_SIZE: int = 0

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

Path(settings.UPLOAD_DIR).mkdir(
    parents=True,
    exist_ok=True
)
