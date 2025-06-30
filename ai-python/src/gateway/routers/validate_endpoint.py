from fastapi import APIRouter, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.logger.default_logger import logger
import os
from dotenv import load_dotenv
from src.gateway.utils import log_api_call
import gc
from huggingface_hub import get_inference_endpoint
from fastapi.responses import JSONResponse
from src.gateway.schema.endpoint_validation import EndpointValidationBase

load_dotenv()

router = APIRouter()

limiter = Limiter(key_func=get_remote_address)
limit_canvas = os.getenv("LIM_TITLE", "5/minute")


@router.post(
    "/validate-huggingface-endpoint",
    summary="Validate Huggingface endpoint",
    description="Endpoint to validate",
    response_description="Response whether the endpoint is validated or not.",
   
)
# @limiter.limit(limit_title)
async def validate_huggingface_endpoint(
    request: Request,
    huggingface_input: EndpointValidationBase,
):
    # Log that the API endpoint is called using the helper function
    log_api_call("/validate-huggingface-endpoint")
    try:
            model_name = huggingface_input.model_name    
            endpoint = get_inference_endpoint(model_name,token=huggingface_input.token)
            taskType = endpoint.raw['model']['task']
            model_image = endpoint.raw['model']['image']   
            if taskType == 'text-generation':

                if 'tgi' in model_image:
                    context = endpoint.raw['model']['image']['tgi']['maxInputLength']
                    total_tokens = endpoint.raw['model']['image']['tgi']['maxTotalTokens']
                    if context >= 8096:
                        if context >= huggingface_input.context_length:
                            if (total_tokens-context) >= 4096:
                                return JSONResponse(content={"message": f"Endpoint URL Is Validated for model: {model_name} with Task as:{taskType}.","data":True}, status_code=status.HTTP_200_OK)
                            else:
                                return JSONResponse(content={"message": f"Context Limit for Endpoint URl is not validated for model:{model_name}.Please ensure Difference between Max Number of Tokens: {total_tokens} and Max Input Length: {context} should be greater than 4096","data":False}, status_code=status.HTTP_200_OK)
                        else:
                            return JSONResponse(content={"message": f"Context Limit for Endpoint URl is not validated for model:{model_name}.Please ensure Selected Context Length should be within the Hosted Context Limit/Max Input Length:{context}","data":False}, status_code=status.HTTP_200_OK)
                    else:
                        return JSONResponse(content={"message": f"Endpoint URL Is Not Validated for model: {model_name} Token Limit should be greater than or equals to 8096","data":False}, status_code=status.HTTP_200_OK)
                    
                else:
                    return JSONResponse(content={"message": f"Endpoint URL Is Not Validated for model: {model_name}.Model Not hosted on TGI inference","data":False}, status_code=status.HTTP_200_OK)
                
            elif taskType == 'text-to-image':
                if 'huggingface' in endpoint.raw['model']['image'] and endpoint.raw['model']['image']['huggingface'] == {}:
                    return JSONResponse(content={"message": f"Endpoint URL Is Validated for model: {model_name} with Task as:{taskType}.","data":True}, status_code=status.HTTP_200_OK)
                else:
                    return JSONResponse(content={"message": f"Endpoint URL Is Not Validated for model: {model_name} with Task as:{taskType}.","data":False}, status_code=status.HTTP_200_OK)
                
            else:
                return JSONResponse(content={"message": f"Endpoint URL Is Not Validated for model: {model_name}.Model Task should be Text Generation or Text to image","data":False}, status_code=status.HTTP_200_OK)

    except Exception as e:
        logger.error(
            f"Failed to validate huggingface endpoint: {e}",
            extra={"tags": {"endpoint": "/validate-huggingface-endpoint"}}
        )
        return JSONResponse(content={"message": f"Validation Failed:{e}","data":False}, status_code=status.HTTP_200_OK)
    
    finally:
        gc.collect()