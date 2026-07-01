from pydantic import BaseModel
from dataclasses import dataclass

@dataclass(slots= True)
class PageContent(BaseModel):
    page: int
    content: str
