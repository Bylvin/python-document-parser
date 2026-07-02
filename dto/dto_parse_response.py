from pydantic import BaseModel

from dto.dto_page_content import PageContent

class ParseResponse(BaseModel):
    filename: str
    total_pages: int
    read_time: float  # durasi parsing dokumen dalam detik
    total_time: float  # durasi total (simpan file + parsing) dalam detik
    data: list[PageContent]
