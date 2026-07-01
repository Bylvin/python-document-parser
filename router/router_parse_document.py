from fastapi import APIRouter, File, UploadFile

from dto.dto_parse_response import ParseResponse

from service.service_parse_document import parse_document

router_parse_document = APIRouter(prefix="/api/v1")

@router_parse_document.post("/parse-document", response_model= ParseResponse)
async def parse_document_content(file: UploadFile = File(...)):
    parse_response = await parse_document(file= file)
    return parse_response
