from fastapi import APIRouter, Request, HTTPException, Depends, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from src.chatflow_langchain.service.pro_agent.seo_optimizer.business_summary import BusinessSummaryGenerator
from src.chatflow_langchain.service.pro_agent.seo_optimizer.keyword_research import KeywordResearchService
from src.chatflow_langchain.service.pro_agent.seo_optimizer.topic_generation import TopicGenerator
from src.chatflow_langchain.service.pro_agent.seo_optimizer.article_generator import ArticleGeneratorService
from src.gateway.jwt_decode import get_user_data
from src.logger.default_logger import logger
from src.gateway.schema.pro_agent import ProAgentRequestSchema,ProSEOSummaryRequestSchema, ProSEOTopicRequestSchema , ProSEOArticleRequestSchema, ProSEOKeywordRequestSchema
import os
from src.gateway.custom_fastapi.streaming_response import StreamingResponseWithStatusCode
from dotenv import load_dotenv
from src.gateway.utils import log_api_call
from src.chatflow_langchain.utils.url_validator import URLCheckerService
import gc

load_dotenv()

router = APIRouter()

limiter = Limiter(key_func=get_remote_address)
limit_stream_chat = os.getenv("LIM_SCRAPE", "5/minute")
@router.post(
    "/pro-agent/business-summary",
    summary="Generate a business summary and identify the target audience",
    description="This endpoint processes Pro Agent service requests to generate a comprehensive business summary and identify the target audience based on the provided input.",
    response_description="Response containing the task chain ID for the operation.",
)
async def summary_service(
    request: Request,
    agent_request: ProSEOSummaryRequestSchema,
    current_user=Depends(get_user_data)
):
    """
    Pro Agent Service.

    This endpoint allows users to interact with the Pro Agent service to generate a business summary and identify the target audience.

    Args:
        request (Request): The incoming HTTP request.
        agent_request (ProAgentRequestSchema): Input data for the Pro Agent request.
        current_user: The current user making the request.

    Returns:
        dict: A message containing the task chain ID for the operation.

    Raises:
        HTTPException: If there is an error processing the request.
    """
    # Log that the API endpoint is called using the helper function
    log_api_call("/business-summary")
    try:
        business_service = BusinessSummaryGenerator(current_user_data=current_user)
        checker = URLCheckerService(base_name=agent_request.agent_extra_info.get("website_url", "Not Specified"))
        reachable = await checker.check_urls_async_status()
        print(f"Reachable URLs: {reachable}")
        first_url = next(iter(reachable.keys()), None)
        first_reason = next(iter(reachable.values()), None)
        is_reachable = first_reason.get("status") if first_reason else True
        if not is_reachable:
            logger.warning("🌐❌ No reachable URLs found in the provided input.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No reachable URLs found.")

        agent_request.agent_extra_info['website_url']=first_url
        await business_service.initialize_chat_input(agent_request)
        await business_service.scrape_url_content()
        await business_service.initialize_llm()
        # await business_service.initialize_repository()
        await business_service.create_prompts()
        await business_service.create_chain()
        response=await business_service.run_chain()
        logger.info(
            "Successfully executed Scrape Webpage Content API",
            extra={"tags": {"endpoint": "/pro-agent"}}
        )
    
        return response

    except HTTPException as he:
        logger.error(
            "HTTP error executing Scrape Webpage Content API",
            extra={
                "tags": {
                    "endpoint": "/business-summary",
                    "error": str(he)
                }
            }
        )
        raise he  # Re-raise the HTTPException to be handled by FastAPI

    except Exception as e:
        logger.error(
            "Error executing Scrape Webpage Content API",
            extra={
                "tags": {
                    "endpoint": "/business-summary",
                    "error": str(e)
                }
            }
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to generate business summary")
    
    finally:
        gc.collect()



@router.post(
    "/pro-agent/keyword-research",
    summary="Keyword research generation",
    description="This endpoint processes Pro Agent service requests to generate keyword research from SEO data, including search volume and competition.",
    response_description="Target keywords and new recommended research keywords.",
)
async def keyword_research_service(
    request: Request,
    agent_request: ProSEOKeywordRequestSchema,
    current_user=Depends(get_user_data)
):
    """
    Pro Agent Service.

    This endpoint allows users to interact with the Pro Agent service to generate keyword research based on SEO data.

    Args:
        request (Request): The incoming HTTP request.
        agent_request (ProAgentRequestSchema): Input data for the Pro Agent request.
        current_user: The current user making the request.

    Returns:
        dict: A message containing the task chain ID for the operation.

    Raises:
        HTTPException: If there is an error processing the request.
    """
    # Log that the API endpoint is called using the helper function
    log_api_call("/keyword-research")
    try:
        # Initialize the LLM if needed
        keyword_research_service = KeywordResearchService()
        
        
        await keyword_research_service.initialize_chat_input(agent_request)
        response=await keyword_research_service.fetch_and_display_keywords()
        logger.info(
            "Successfully executed Scrape Webpage Content API",
            extra={"tags": {"endpoint": "/pro-agent"}}
        )
        return response

    except HTTPException as he:
        logger.error(
            "HTTP error executing Scrape Webpage Content API",
            extra={
                "tags": {
                    "endpoint": "/keyword-research",
                    "error": str(he)
                }
            }
        )
        raise he  # Re-raise the HTTPException to be handled by FastAPI

    except Exception as e:
        logger.error(
            "Error executing Scrape Webpage Content API",
            extra={
                "tags": {
                    "endpoint": "/keyword-research",
                    "error": str(e)
                }
            }
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to generate keyword research")
    
    finally:
        gc.collect()


@router.post(
    "/pro-agent/topic-generation",
    summary="Generate a content topic based on business information and keywords",
    description="This endpoint generates a highly relevant and engaging content topic based on the provided business summary, target audience, and keywords.",
    response_description="Generated content topic.",
)
async def topic_generation_service(
    request: Request,
    agent_request: ProSEOTopicRequestSchema,
    current_user=Depends(get_user_data)
):
    """
    Topic Generation Service.

    This endpoint generates a topic name using GPT-4 based on business information and SEO keywords.

    Args:
        request (Request): The incoming HTTP request.
        agent_request (ProAgentRequestSchema): Input data for the Pro Agent request.
        current_user: The current user making the request.

    Returns:
        dict: A generated topic name.

    Raises:
        HTTPException: If there is an error processing the request.
    """
    logger.info("API call: /topic-generation")
    try:
        topic_generator = TopicGenerator(current_user)
        await topic_generator.initialize_chat_input(agent_request)
        await topic_generator.initialize_llm()
        await topic_generator.create_prompt()
        await topic_generator.create_chain()

        response=await topic_generator.run_chain()
        logger.info(
            "Successfully executed Topic Generation API",
            extra={"tags": {"endpoint": "/pro-agent/topic-generation"}}
        )
        return response
    
    except HTTPException as he:
        logger.error("HTTP error in topic generation", extra={"tags": {"endpoint": "/topic-generation", "error": str(he)}})
        raise he

    except Exception as e:
        logger.error("Error in topic generation", extra={"tags": {"endpoint": "/topic-generation", "error": str(e)}})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to generate topic")

    finally:
        gc.collect()


@router.post(
    "/pro-agent/article-generation",
    summary="Generate a content topic based on business information and keywords",
    description="This endpoint generates a highly relevant and engaging content topic based on the provided business summary, target audience, and keywords.",
    response_description="Generated content topic.",
)
async def article_generation(
    request: Request,
    agent_request: ProSEOArticleRequestSchema,
    current_user=Depends(get_user_data)
):
    """
    Topic Generation Service.

    This endpoint generates a topic name using GPT-4 based on business information and SEO keywords.

    Args:
        request (Request): The incoming HTTP request.
        agent_request (ProAgentRequestSchema): Input data for the Pro Agent request.
        current_user: The current user making the request.

    Returns:
        dict: A generated topic name.

    Raises:
        HTTPException: If there is an error processing the request.
    """
    logger.info("API call: /topic-generation")
    try:
        article_generator = ArticleGeneratorService()
        await article_generator.initialize_chat_input(agent_request)
        await article_generator.fetch_articles()
        await article_generator.initialize_llm()
        await article_generator.initialize_repository()
        await article_generator.create_prompts()
        await article_generator.create_chain()

        response= article_generator.run_chain()
        
        logger.info(
            "Successfully executed Topic Generation API",
            extra={"tags": {"endpoint": "/pro-agent/topic-generation"}}
        )
        return StreamingResponseWithStatusCode(response, media_type="text/event-stream")
    
    except HTTPException as he:
        logger.error("HTTP error in topic generation", extra={"tags": {"endpoint": "/topic-generation", "error": str(he)}})
        raise he

    except Exception as e:
        logger.error("Error in topic generation", extra={"tags": {"endpoint": "/topic-generation", "error": str(e)}})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to generate article")
    
    finally:
        gc.collect()