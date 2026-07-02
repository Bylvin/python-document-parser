"""
Component untuk parsing dokumen dengan PyMuPDF.
"""
from pathlib import Path

import fitz

from dto.dto_page_content import PageContent


class PyMuPDFParser:
    """Class component PyMuPDF Parser"""

    def parse(self, file_path: Path) -> list[PageContent]:
        """Function untuk parsing content menggunakan PyMuPDF.

        CPU-bound & sinkron — dipanggil lewat thread pool oleh service agar
        tidak memblok event loop.
        """
        document = fitz.open(file_path)
        pages: list[PageContent] = []

        for page_index in range(document.page_count):
            page = document.load_page(page_index)
            text = page.get_text("text")

            pages.append(
                PageContent(
                    page=page_index + 1,
                    content=text.strip()
                )
            )

        document.close()
        return pages
