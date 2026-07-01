from fastapi import APIRouter

router_parse_document = APIRouter(prefix="/api/v1")

@router_parse_document.post("/parse-document")
def parse_document_content():
    return None