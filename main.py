from fastapi import FastAPI
from router.router_parse_document import router_parse_document

application = FastAPI(
    title="Document Parser API",
    version="0.0.1"
)

application.include_router(router_parse_document)