from pathlib import Path
from docling.document_converter import DocumentConverter
from docling.datamodel.document import TableItem

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
        for page_no, page_obj in document.pages.items():
            page_texts = []
            
            # Iterasi semua elemen di dalam dokumen
            for element, _level in document.iterate_items():
                # Pastikan elemen berada di halaman yang sedang diproses
                if element.prov and element.prov[0].page_no == page_no:
                    
                    # KONDISI 1: Jika elemen adalah Tabel
                    if isinstance(element, TableItem):
                        table_markdown = element.export_to_markdown()
                        page_texts.append(table_markdown)
                    
                    # KONDISI 2: Jika elemen memiliki atribut 'text' (Paragraf, Judul, List, dll)
                    elif hasattr(element, "text") and element.text:
                        page_texts.append(element.text)
                    
                    # KONDISI 3: Jika elemen adalah Gambar (PictureItem)
                    else:
                        # Opsi A: Berikan penanda bahwa ada gambar di posisi ini (Bagus untuk RAG/LLM)
                        page_texts.append(f"\n*[Gambar: {element.label if hasattr(element, 'label') else 'Picture'} Sentil]*\n")
            
            # Gabungkan semua konten satu halaman
            text_content = "\n\n".join(page_texts)
            
            pages.append(
                PageContent(
                    page=page_no,
                    content=text_content.strip()
                )
            )

        return pages
