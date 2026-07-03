"""
Component untuk parsing dokumen dengan Docling.
"""
import os
import tempfile
import warnings
from collections import defaultdict
from pathlib import Path

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import TableItem
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    AcceleratorOptions,
    TesseractCliOcrOptions,
)

from config.config import settings
from dto.dto_page_content import PageContent


# torch (dipakai model Docling) memunculkan UserWarning saat pin_memory=True
# tapi tidak ada GPU. Di lingkungan CPU-only ini tidak berpengaruh apa pun —
# bungkam noise-nya secara spesifik (bukan seluruh warning).
warnings.filterwarnings(
    "ignore",
    message="'pin_memory' argument is set as true but no accelerator is found",
    category=UserWarning,
)

class DoclingParser:
    """Class component Docling Parser"""
    def __init__(self):
        # Manfaatkan core CPU untuk model layout/OCR/tabel Docling. Bisa dibatasi
        # lewat DOCLING_NUM_THREADS bila RAM terbatas (0 = otomatis = cpu_count).
        pipeline_options = PdfPipelineOptions()
        num_threads = settings.DOCLING_NUM_THREADS or (os.cpu_count() or 4)
        pipeline_options.accelerator_options = AcceleratorOptions(
            num_threads=num_threads,
        )

        # Batasi jumlah halaman/region yang diproses bersamaan untuk menekan
        # memori puncak (mencegah std::bad_alloc saat render halaman besar).
        if settings.DOCLING_BATCH_SIZE > 0:
            bs = settings.DOCLING_BATCH_SIZE
            pipeline_options.ocr_batch_size = bs
            pipeline_options.layout_batch_size = bs
            pipeline_options.table_batch_size = bs
            # Backpressure antar-stage: tanpa ini Docling me-render s/d 100 halaman
            # lebih dulu (queue_max_size default) dan menumpuk bitmap-nya di memori
            # sementara OCR yang lambat baru mengonsumsinya satu per satu -> OOM.
            # Batasi antrean agar preprocess tidak balapan mendahului OCR.
            pipeline_options.queue_max_size = max(bs * 2, 2)

        # Pilih engine OCR dari konfigurasi.
        #  - "tesseract": pakai Tesseract yang berjalan di container Docker,
        #    dijembatani wrapper `tesseract-docker.cmd` (host tak perlu install
        #    tesseract). Docling menulis gambar halaman ke folder temp OCR yang
        #    di-mount ke container, lalu wrapper menjalankan `docker exec`.
        #  - selain itu: biarkan default Docling (auto: EasyOCR), sehingga lokal
        #    tetap jalan tanpa Docker sama sekali.
        if settings.OCR_ENGINE.lower() == "tesseract":
            # Paksa Docling menulis file temp OCR ke folder yang di-mount ke
            # container, dan beri tahu wrapper prefix folder yang sama (via env).
            ocr_tmp = os.path.abspath(settings.OCR_TMP_DIR)
            os.makedirs(ocr_tmp, exist_ok=True)
            tempfile.tempdir = ocr_tmp
            os.environ["OCR_TMP_DIR"] = ocr_tmp

            langs = [l.strip() for l in settings.OCR_LANG.split(",") if l.strip()]
            pipeline_options.ocr_options = TesseractCliOcrOptions(
                lang=langs,
                tesseract_cmd=os.path.abspath(settings.TESSERACT_CMD),
            )

        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
            }
        )

    def parse(self, file_path: Path) -> list[PageContent]:
        """Function untuk parsing content menggunakan Docling.

        CPU-bound & sinkron — dipanggil lewat thread pool oleh service agar
        tidak memblok event loop.
        """
        result = self.converter.convert(str(file_path))
        document = result.document

        texts_by_page: dict[int, list[str]] = defaultdict(list)
        # iterate_items() menghasilkan tuple (item, level), bukan item langsung.
        for element, _level in document.iterate_items():
            if not element.prov:
                continue
            page_no = element.prov[0].page_no

            # KONDISI 1: Jika elemen adalah Tabel
            if isinstance(element, TableItem):
                texts_by_page[page_no].append(element.export_to_markdown(doc=document))

            # KONDISI 2: Jika elemen memiliki atribut 'text' (Paragraf, Judul, List, dll)
            elif getattr(element, "text", None):
                texts_by_page[page_no].append(element.text)

            # KONDISI 3: Jika elemen adalah Gambar (PictureItem)
            else:
                label = getattr(element, "label", "Picture")
                texts_by_page[page_no].append(f"\n*[Gambar: {label}]*\n")

        return [
            PageContent(
                page=page_no,
                content="\n\n".join(page_texts).strip(),
            )
            for page_no, page_texts in sorted(texts_by_page.items())
        ]
