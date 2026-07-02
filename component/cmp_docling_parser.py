"""
Component untuk parsing dokumen dengan Docling.
"""
import os
import warnings
from collections import defaultdict
from pathlib import Path

# torch (dipakai model Docling) memunculkan UserWarning saat pin_memory=True
# tapi tidak ada GPU. Di lingkungan CPU-only ini tidak berpengaruh apa pun —
# bungkam noise-nya secara spesifik (bukan seluruh warning).
warnings.filterwarnings(
    "ignore",
    message="'pin_memory' argument is set as true but no accelerator is found",
    category=UserWarning,
)

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.document import TableItem
from docling.datamodel.pipeline_options import PdfPipelineOptions, AcceleratorOptions

from dto.dto_page_content import PageContent


class DoclingParser:
    """Class component Docling Parser"""
    def __init__(self):
        # Manfaatkan seluruh core CPU untuk model layout/OCR/tabel Docling.
        # Tanpa ini Docling default ke jumlah thread konservatif dan lambat
        # untuk dokumen besar.
        pipeline_options = PdfPipelineOptions()
        pipeline_options.accelerator_options = AcceleratorOptions(
            num_threads=os.cpu_count() or 4,
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
