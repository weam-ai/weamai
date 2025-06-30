from fastapi import APIRouter, Request, HTTPException, Depends, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.chatflow_langchain.controller.sales_agent_hub import SalesAnalyzerAgentController
from src.gateway.jwt_decode import get_user_data
from src.logger.default_logger import logger
from src.gateway.schema.pro_agent import ProSalesCallAnalyzerSchema
import os
from src.gateway.custom_fastapi.streaming_response import StreamingResponseWithStatusCode
from dotenv import load_dotenv
from src.gateway.utils import log_api_call
import gc

load_dotenv()

router = APIRouter()

limiter = Limiter(key_func=get_remote_address)
limit_stream_chat = os.getenv("LIM_SCRAPE", "5/minute")

@router.post(
    "/pro-agent/sales-call-analyzer",
    summary="Sales Call anazlyzer",
    description="Endpoint to For analyzing Sales Call.",
    response_description="Response contains streaming from llm",
)
async def pro_agent(
    request: Request,
    agent_request: ProSalesCallAnalyzerSchema,
    current_user=Depends(get_user_data)
):

    # Log that the API endpoint is called using the helper function
    log_api_call("/pro-agent")
    try:
        # Initialize the LLM if needed

        agent_service = SalesAnalyzerAgentController()
        agent_service.initialization_service_code(pro_agent_code=agent_request.pro_agent_code)
        agent_response =  await agent_service.service_hub_handler(chat_input=agent_request, current_user=current_user)
        logger.info(
            "Successfully executed Sales Call Analyzer API",
            extra={"tags": {"endpoint": "/pro-agent/sales-call-analyzer"}}
        )
        return StreamingResponseWithStatusCode(agent_response, media_type="text/event-stream")

    except HTTPException as he:
        logger.error(
            "HTTP error executing Sales call analyzer API",
            extra={
                "tags": {
                    "endpoint": "/pro-agent/sales-call-analyzer",
                    "error": str(he)
                }
            }
        )
        raise he  # Re-raise the HTTPException to be handled by FastAPI

    except Exception as e:
        logger.error(
            "Error executing Sales call analyzer API",
            extra={
                "tags": {
                    "endpoint": "/pro-agent",
                    "error": str(e)
                }
            }
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Internal server error")
    
    finally:
        gc.collect()