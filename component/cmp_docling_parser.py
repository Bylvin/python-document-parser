from pathlib import Path
from docling.document_converter import DocumentConverter

from dto.dto_page_content import PageContent


class DoclingParser:

    def __init__(self):
        self.converter = DocumentConverter()

    async def parse(self, file_path: Path) -> list[PageContent]:
        result = self.converter.convert(str(file_path))
        document = result.document
        pages: list[PageContent] = []

        #
        # Docling mengembalikan document yang dapat diekspor ke markdown.
        # Untuk sementara kita mengambil konten per halaman.
        #
        for page_no, page in enumerate(document.pages, start=1):
            text = page.export_to_markdown()
            pages.append(
                PageContent(
                    page=page_no,
                    content=text.strip()
                )
            )

        return pages
