from pathlib import Path

from fastapi import UploadFile

from dto.dto_parse_response import ParseResponse

from component.cmp_save_file import save_upload_file
from component.cmp_docling_parser import DoclingParser
from component.cmp_pymupdf_parser import PyMuPDFParser


docling_parser = DoclingParser()
pymupdf_parser = PyMuPDFParser()

async def parse_document(file: UploadFile) -> ParseResponse:
    file_path: Path = await save_upload_file(file)

    try:
        pages = await docling_parser.parse(file_path= file_path)
    except Exception as ex:
        print(f"Docling failed: {ex}")
        pages = await pymupdf_parser.parse(file_path= file_path)
    
    return ParseResponse(
        filename= file.filename,
        total_pages= len(pages),
        pages= pages
    )
