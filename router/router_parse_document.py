import json

from fastapi import APIRouter, File, UploadFile
from fastapi.responses import StreamingResponse

from service.service_parse_document import parse_document

router_parse_document = APIRouter(prefix="/api/v1")

@router_parse_document.post("/parse-document")
async def parse_document_content(file: UploadFile = File(...)):
    parse_response = await parse_document(file= file)

    async def stream_json():
        # Hasilkan SATU objek JSON valid secara bertahap:
        # {"filename": ..., "total_pages": N, "data": [ {..}, {..}, ... ]}
        # Tiap halaman diserialisasi lalu dilepas, jadi tidak ada satu string
        # JSON raksasa untuk seluruh dokumen sekaligus — dan tetap JSON valid
        # yang bisa di-parse Swagger UI / klien biasa.
        yield (
            '{"filename": ' + json.dumps(parse_response.filename)
            + ', "total_pages": ' + str(parse_response.total_pages)
            + ', "read_time": ' + json.dumps(parse_response.read_time)
            + ', "total_time": ' + json.dumps(parse_response.total_time)
            + ', "data": ['
        )
        for index, page in enumerate(parse_response.data):
            yield ('' if index == 0 else ',') + page.model_dump_json()
        yield "]}"

    return StreamingResponse(stream_json(), media_type="application/json")
