import requests
from fastapi import HTTPException,status
from src.celery_worker_hub.web_scraper.celery_app import celery_app
from src.celery_worker_hub.web_scraper.config import TaskConfig
from src.logger.default_logger import logger
from src.celery_worker_hub.web_scraper.utils.create_summary import chain_summary,chain_summary_HF,chain_summary_ANT
from langchain_community.callbacks import get_openai_callback
from langchain.docstore.document import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.celery_worker_hub.web_scraper.utils.hash_function import hash_website
from openai import RateLimitError
from src.celery_worker_hub.web_scraper.utils.prompt_notification import add_notification_data
from src.Firebase.firebase import firebase
from src.Emailsend.email_service import EmailService
from src.celery_worker_hub.web_scraper.config import SummaryConfig
from src.chatflow_langchain.repositories.openai_error_messages_config import OPENAI_MESSAGES_CONFIG,DEV_MESSAGES_CONFIG
from markdown import markdown
from huggingface_hub.utils import HfHubHTTPError
from src.custom_lib.langchain.callbacks.huggingface.cost.context_manager import get_huggingface_callback
from src.custom_lib.langchain.callbacks.anthropic.cost.context_manager import anthropic_sync_callback
from src.crypto_hub.utils.encode_decode import encode_object

from src.round_robin.llm_key_manager import APIKeySelectorService,APIKeyUsageService
from src.chatflow_langchain.service.config.model_config_openai import Functionality,OPENAIMODEL


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 0, 'countdown': 0},
    queue="scrapsite"
)
def generate_list_summaries(self,scraped_results:dict,api_key:str=None,notification_data:dict=None,companyRedis_id:str='default'):
    try:
        chain=chain_summary(api_key=api_key)
        api_usage_service = APIKeyUsageService()

        summaries = {}
        data={}
        total_tokens = 0
        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_cost = 0

        for key, list_content in scraped_results.items():
            list_summaries=''
            with get_openai_callback() as cb:
                for index, (web,website_content)in enumerate(list_content.items()):
                    if website_content == SummaryConfig.FORBIDDEN_CODE:
                        doc = [Document(page_content=SummaryConfig.FORBIDDEN_PROMPT)]
                        summary = chain.invoke(doc)
                    elif website_content == ' ':
                        doc = [Document(page_content=SummaryConfig.EMPTY_PROMPT)]
                        summary = chain.invoke(doc)
                    else:
                        text_splitter = RecursiveCharacterTextSplitter(chunk_size=TaskConfig.CHUNK_SIZE, chunk_overlap=TaskConfig.CHUNK_OVERLAP)
                        texts = text_splitter.split_text(website_content)
                        doc = [Document(page_content=chunk) for chunk in texts]
                        summary = chain.invoke(doc)
                    data[f"{key}.{hash_website(web)}"]={"website":web,"summary":summary['output_text']}
                # api_usage_service.update_usage_sync(provider='OPEN_AI', tokens_used=cb.total_tokens, model=OPENAIMODEL.GPT_4_1_MINI, api_key=api_key, functionality=Functionality.CHAT,company_id=companyRedis_id)
                total_tokens += cb.total_tokens
                total_prompt_tokens += cb.prompt_tokens
                total_completion_tokens += cb.completion_tokens
                total_cost += cb.total_cost

        cost_dict={
                    "tokens.totalUsed":  total_tokens,
                    "tokens.promptT": total_prompt_tokens,
                    "tokens.completion": total_completion_tokens,
                    "tokens.totalCost": total_cost,
                    "isCompleted": True
                    }
        logger.info("Summaries Cost: %s", cost_dict)     
        
        cost_dict.update(data)
        summaries['$set']=cost_dict

        return summaries
        
    except RateLimitError as e:
        firebase.send_push_notification(notification_data['token'],"Insufficient Quota Alert", DEV_MESSAGES_CONFIG.get("insufficient_quota_message"))
        add_notification_data(DEV_MESSAGES_CONFIG.get("insufficient_quota_message"),notification_data["user_data"],"notificationList")
        
        markdown_content = OPENAI_MESSAGES_CONFIG.get("insufficient_quota_mail", {}).get("content")
        email_service = EmailService()
        email_service.send_email(
            email=notification_data.get('user_data', {}).get('email'),
            subject="Insufficient Quota Alert",
            username=notification_data.get('user_data', {}).get('fname'),
            content_body=markdown(markdown_content),
            slug=encode_object(notification_data["brain_id"]),
            template_name="failure-mail",
            show_button=False,
            url_type="prompts"
        )
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}", extra={"tags": {"method": "ScrapUrlService.generate_list_summaries"}})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Request failed: {e}")
    except Exception as e:
        logger.error(f"An exception occurred: {e}", extra={"tags": {"method": "ScrapUrlService.generate_list_summaries"}})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"An exception occurred: {e}")
@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 0, 'countdown': 0},
    queue="scrapsite"
) 
def generate_list_summaries_ant(self,scraped_results:dict,api_key:str=None,notification_data:dict=None):
    try:
        chain=chain_summary_ANT(api_key=api_key)

        summaries = {}
        data={}
        total_tokens = 0
        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_cost = 0

        for key, list_content in scraped_results.items():
            list_summaries=''
            with anthropic_sync_callback() as cb:
                for index, (web,website_content)in enumerate(list_content.items()):
                    if website_content == SummaryConfig.FORBIDDEN_CODE:
                        doc = [Document(page_content=SummaryConfig.FORBIDDEN_PROMPT)]
                        summary = chain.invoke(doc)
                    elif website_content == ' ':
                        doc = [Document(page_content=SummaryConfig.EMPTY_PROMPT)]
                        summary = chain.invoke(doc)
                    else:
                        text_splitter = RecursiveCharacterTextSplitter(chunk_size=TaskConfig.CHUNK_SIZE, chunk_overlap=TaskConfig.CHUNK_OVERLAP)
                        texts = text_splitter.split_text(website_content)
                        doc = [Document(page_content=chunk) for chunk in texts]
                        summary = chain.invoke(doc)
                    data[f"{key}.{hash_website(web)}"]={"website":web,"summary":summary['output_text']}
                total_tokens += cb.total_tokens
                total_prompt_tokens += cb.prompt_tokens
                total_completion_tokens += cb.completion_tokens
                total_cost += cb.total_cost

        cost_dict={
                    "tokens.totalUsed":  total_tokens,
                    "tokens.promptT": total_prompt_tokens,
                    "tokens.completion": total_completion_tokens,
                    "tokens.totalCost": total_cost,
                    "isCompleted": True
                    }
        logger.info("Summaries Cost: %s", cost_dict)     
        
        cost_dict.update(data)
        summaries['$set']=cost_dict

        return summaries
        
    except RateLimitError as e:
        firebase.send_push_notification(notification_data['token'],"Insufficient Quota Alert", DEV_MESSAGES_CONFIG.get("insufficient_quota_message"))
        add_notification_data(DEV_MESSAGES_CONFIG.get("insufficient_quota_message"),notification_data["user_data"],"notificationList")
        
        markdown_content = OPENAI_MESSAGES_CONFIG.get("insufficient_quota_mail", {}).get("content")
        email_service.send_email(
            email=notification_data.get('user_data', {}).get('email'),
            subject="Insufficient Quota Alert",
            username=notification_data.get('user_data', {}).get('fname'),
            content_body=markdown(markdown_content),
            slug=encode_object(notification_data["brain_id"]),
            template_name="failure-mail",
            show_button=False,
            url_type="prompts"
        )
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}", extra={"tags": {"method": "ScrapUrlService.generate_list_summaries"}})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Request failed: {e}")
    except Exception as e:
        logger.error(f"An exception occurred: {e}", extra={"tags": {"method": "ScrapUrlService.generate_list_summaries"}})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"An exception occurred: {e}")
    
@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 0, 'countdown': 0},
    queue="scrapsite"
)  
def generate_list_summaries_HF(self,scraped_results,api_key:str=None,endpoint_url:str=None,notification_data:dict=None):
    try:
        chain=chain_summary_HF(api_key=api_key,endpoint_url=endpoint_url)

        summaries = {}
        data={}
        total_tokens = 0
        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_cost = 0

        for key, list_content in scraped_results.items():
            list_summaries=''
            with get_huggingface_callback() as cb:
                for index, (web,website_content)in enumerate(list_content.items()):
                    if website_content == SummaryConfig.FORBIDDEN_CODE:
                        doc = [Document(page_content=SummaryConfig.FORBIDDEN_PROMPT)]
                        summary = chain.invoke(doc)
                    elif website_content == ' ':
                        doc = [Document(page_content=SummaryConfig.EMPTY_PROMPT)]
                        summary = chain.invoke(doc)
                    else:
                        text_splitter = RecursiveCharacterTextSplitter(chunk_size=TaskConfig.CHUNK_SIZE, chunk_overlap=TaskConfig.CHUNK_OVERLAP)
                        texts = text_splitter.split_text(website_content)
                        doc = [Document(page_content=chunk) for chunk in texts]
                        summary = chain.invoke(doc)
                    data[f"{key}.{hash_website(web)}"]={"website":web,"summary":summary['output_text']}
                total_tokens += cb.total_tokens
                total_prompt_tokens += cb.prompt_tokens
                total_completion_tokens += cb.completion_tokens
                total_cost += cb.total_cost

        cost_dict={
                    "tokens.totalUsed":  total_tokens,
                    "tokens.promptT": total_prompt_tokens,
                    "tokens.completion": total_completion_tokens,
                    "tokens.totalCost": total_cost,
                    "isCompleted": True
                    }
        logger.info("Summaries Cost: %s", cost_dict)     
        
        cost_dict.update(data)
        summaries['$set']=cost_dict

        return summaries
        
    except HfHubHTTPError as e:
        firebase.send_push_notification(notification_data['token'],"Insufficient Quota Alert", DEV_MESSAGES_CONFIG.get("insufficient_quota_message"))
        add_notification_data(DEV_MESSAGES_CONFIG.get("insufficient_quota_message"),notification_data["user_data"],"notificationList")
        
        markdown_content = OPENAI_MESSAGES_CONFIG.get("insufficient_quota_mail", {}).get("content")
        email_service.send_email(
            email=notification_data.get('user_data', {}).get('email'),
            subject="Insufficient Quota Alert",
            username=notification_data.get('user_data', {}).get('fname'),
            content_body=markdown(markdown_content),
            slug=encode_object(notification_data["brain_id"]),
            template_name="failure-mail",
            show_button=False,
            url_type="prompts"
        )
    except requests.RequestException as e:
        logger.error(f"Request failed: {e}", extra={"tags": {"method": "ScrapUrlService.generate_list_summaries"}})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Request failed: {e}")
    except Exception as e:
        logger.error(f"An exception occurred: {e}", extra={"tags": {"method": "ScrapUrlService.generate_list_summaries"}})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"An exception occurred: {e}")