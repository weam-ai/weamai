from fastapi.routing import APIRouter
from fastapi import HTTPException
from fastapi import APIRouter, Request, HTTPException, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi.responses import JSONResponse
from src.gateway.schema.qdrant import QdrantIndexBase
from src.logger.default_logger import logger
from src.db.qdrant_config import qdrant_client
from src.vector_store.qdrant.langchain_lib.qdrant_setup import QdrantSetup
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
qdrant_service=QdrantSetup(qdrant_client)

@router.post(
    "/create-qdrant-index",
    summary="create qdrant index ",
    description="for creation qdrant index for company",
    response_description="Response message containing the chat outcome.",
)
@limiter.limit("10/minute")
async def create_serverless_index(
    request: Request,
    qdrant_input: QdrantIndexBase,
    )->str:
    company_id=qdrant_input.company_id
    qdrant_service.initialization(company_id=qdrant_input.company_id)
    try:
        logger.info(
            f"Qdrant index {company_id} created successfully.",
            extra={"tags": {"endpoint": "/create-qdrant-index"}}
        )
        return JSONResponse(content={"result": f"Qdrant index {company_id} created successfully."}, status_code=status.HTTP_200_OK)
    except Exception as e:
        logger.error(
            f"Error executing api: {e}",
            extra={"tags": {"endpoint": "/create-qdrant-index"}}
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
