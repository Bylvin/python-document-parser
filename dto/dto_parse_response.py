from pydantic import BaseModel

from dto.dto_page_content import PageContent

class ParseResponse(BaseModel):
    filename: str
    total_pages: int
    data: list[PageContent]
