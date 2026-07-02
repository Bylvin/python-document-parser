"""
Service untuk melakukan parsing content dari file dokumen.
Memiliki koneksi ke component DoclingParser & PyMuPdfParser.
"""
import logging
import time
from pathlib import Path

import anyio
from docling.exceptions import ConversionError
from fastapi import HTTPException, UploadFile, status

from dto.dto_parse_response import ParseResponse

from component.cmp_save_file import save_upload_file
from component.cmp_docling_parser import DoclingParser
from component.cmp_pymupdf_parser import PyMuPDFParser


logger = logging.getLogger(__name__)

# Inject class DoclingParser & PyMuPdfParser
docling_parser = DoclingParser()
pymupdf_parser = PyMuPDFParser()

async def parse_document(file: UploadFile) -> ParseResponse:
    """Function untuk melakukan parsing content dari file dokumen."""
    # Ukur durasi total (termasuk waktu simpan file upload).
    total_start = time.perf_counter()
    file_path: Path = await save_upload_file(file)

    # Ukur durasi parsing (dari awal proses parse hingga selesai).
    start_time = time.perf_counter()
    try:
        try:
            # Parsing bersifat CPU-bound & sinkron — jalankan di thread pool agar
            # event loop tidak ter-block dan server tetap melayani request lain.
            pages = await anyio.to_thread.run_sync(docling_parser.parse, file_path)
        except (ConversionError, ValueError) as e:
            # Docling gagal (mis. dokumen rusak / validasi) → fallback ke PyMuPDF.
            logger.warning(
                "Docling gagal (%s), fallback ke PyMuPDF: %s", type(e).__name__, e
            )
            pages = await anyio.to_thread.run_sync(pymupdf_parser.parse, file_path)
    except FileNotFoundError as e:
        logger.error("File upload tidak ditemukan saat parsing: %s", file_path)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File tidak ditemukan.",
        ) from e
    except Exception as e:
        # Kedua parser gagal — jangan biarkan variabel `pages` tak terdefinisi
        # (bug lama: UnboundLocalError). Kembalikan error eksplisit.
        logger.exception("Gagal memproses dokumen")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Gagal memproses dokumen.",
        ) from e
    finally:
        # Selalu bersihkan file upload agar disk tidak penuh.
        file_path.unlink(missing_ok=True)

    now = time.perf_counter()
    read_time = round(now - start_time, 3)
    total_time = round(now - total_start, 3)

    return ParseResponse(
        filename= file.filename,
        total_pages= len(pages),
        read_time= read_time,
        total_time= total_time,
        data= pages
    )
