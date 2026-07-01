from pydantic import BaseModel

class PageContent(BaseModel):
    page: int
    content: str
