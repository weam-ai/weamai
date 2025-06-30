from langchain_core.tools import tool
from langchain.prompts import ChatPromptTemplate
from src.custom_lib.langchain.chat_models.openai.chatopenai_cache import MyChatOpenAI as ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from src.chatflow_langchain.utils.upload_image import generate_random_file_name
from src.celery_worker_hub.web_scraper.tasks.upload_file_s3 import task_upload_huggingfaceimage_to_s3
from src.chatflow_langchain.service.huggingface.tool_functions.config import ToolChatConfig, ImageGenerateConfig
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
from src.custom_lib.langchain.callbacks.openai.cost.cost_calc_handler import CostCalculator
from langchain_community.callbacks.manager import get_openai_callback
import json
from fastapi import status
from src.logger.default_logger import logger
from src.chatflow_langchain.service.huggingface.image.utils import extract_error_message
from src.custom_lib.langchain.callbacks.huggingface.cost.context_manager import get_custom_huggingface_callback
from src.custom_lib.langchain.callbacks.huggingface.cost.cost_calc_handler import CostCalculator
from src.custom_lib.langchain.callbacks.huggingface.mongodb.context_manager import get_mongodb_callback_handler
from src.custom_lib.langchain.callbacks.huggingface.streaming.context_manager import async_streaming_handler
from src.custom_lib.langchain.callbacks.huggingface.streaming.custom_stream_async_handler import CustomAsyncIteratorCallbackHandler
import asyncio
from langchain.chains import LLMChain
from src.chatflow_langchain.repositories.openai_error_messages_config import DEV_MESSAGES_CONFIG, HF_ERROR_MESSAGES_CONFIG,OPENAI_MESSAGES_CONFIG
from src.crypto_hub.services.huggingface.llm_api_key_decryption import LLMAPIKeyDecryptionHandler
from langchain_huggingface import HuggingFaceEndpoint,ChatHuggingFace
from requests.exceptions import HTTPError
from huggingface_hub.utils import HfHubHTTPError, EntryNotFoundError, BadRequestError
from huggingface_hub import get_inference_endpoint,list_inference_endpoints
from huggingface_hub import InferenceClient
from openai import RateLimitError,APIConnectionError,APITimeoutError,APIStatusError, NotFoundError
from src.gateway.openai_exceptions import LengthFinishReasonError,ContentFilterFinishReasonError
from src.chatflow_langchain.service.huggingface.tool_functions.utils import delete_resources, convert_image_to_bytes
from src.chatflow_langchain.service.huggingface.config.hf_tool_description import HfToolDescription
import requests

thread_repo = ThreadRepostiory()
cost_callback = CostCalculator()
llm_apikey_decrypt_service = LLMAPIKeyDecryptionHandler()

async_handler = async_streaming_handler()

    # Set model parameters here
@tool(description=HfToolDescription.HUGGINGFACE_IMAGE_GEN)
async def huggingface_image_generation(original_query,hf_token,height,width,num_inference_steps,guidance_scale,endpoint_url,thread_id=None, thread_model=None, memory=None, chat_repository_history=None,regenerated_flag=False,openai_key=None,repo=None,msgCredit=0):
    """An image generation and modification tool that enables users to create images from text descriptions and make various visual changes to the generated images. Users can remove objects, replace elements, insert new items,Edit Images and make other detailed modifications to the images directly using the tool."""
    try:
        prompt_list = chat_repository_history.messages
        prompt_list.insert(0, SystemMessagePromptTemplate.from_template(
            """Focus on User Query: Base the generated image Request primarily on the user's current query, ensuring the description aligns with their request and remains the main focus.

Optional Integration of Previous Request: If relevant, incorporate elements from previous image request as secondary considerations, but only if they enhance the current query's intent.

Exclude Filenames and File References: Completely ignore filenames, file extensions, file paths, or any related identifiers. Do not include them in the output under any circumstances.

Descriptive Clarity and Word Limit: Ensure the final output text is clear, specific, and actionable, strictly within 125 words, and entirely focused on the descriptive content provided by the user.

Ensure Logical Coherence: Align the new text request logically with the user's current query and, if applicable, the previous request, ensuring a seamless and relevant connection.
"""))
        max_tokens = 150
        prompt_list.append(HumanMessagePromptTemplate.from_template(template=[
            {"type": "text", "text": '{query}'}]))
        
        chat_prompt = ChatPromptTemplate.from_messages(prompt_list)

            # Loop through the endpoints

        with get_openai_callback() as cb:
            llm = ChatOpenAI(temperature=ToolChatConfig.TEMPRATURE, api_key=openai_key,
                                model=ImageGenerateConfig.GPT_4o_MINI, streaming=False, stream_usage=True,max_tokens=max_tokens)
            llm_chain = LLMChain(llm=llm,prompt=chat_prompt)
            optimized_query = llm_chain.invoke(original_query)
        if len(optimized_query['text'])>625:
                optimized_query['text']=optimized_query['text'][:625]

        payload = {
            "prompt": optimized_query['text'],
        }
        response = requests.post(endpoint_url, json=payload)
        response.raise_for_status()
        s3_file_name = generate_random_file_name()
        thread_repo_task =asyncio.to_thread(update_thread_repo_and_memory,thread_id, thread_model, optimized_query['text'], s3_file_name, regenerated_flag, chat_repository_history, memory, cb,msgCredit)
        
        logger.info(f"Image successfully generated Ready for Uploading S3 bucket with filename: {s3_file_name} ...")
        
        result=task_upload_huggingfaceimage_to_s3.apply_async(kwargs={'image_bytes': response.content, 's3_file_name': s3_file_name}).get()
        delete_resources(response=response, image_bytes=response)

        # upload_huggingfaceimage_to_s3(image=response, s3_file_name=s3_file_name)
        yield json.dumps({"status": status.HTTP_207_MULTI_STATUS, "message": s3_file_name}), status.HTTP_207_MULTI_STATUS
        await thread_repo_task
    except NotFoundError as e:
        error_content,error_code = extract_error_message(str(e))
        if error_code not in OPENAI_MESSAGES_CONFIG:
            logger.warning(
                f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                extra={"tags": {"method": "HFToolService.huggingface_image_generation.NotFoundError"}})
        else:
            logger.error(
                f"🚨 Model Not Found Error: {error_code}, Message: {error_content}",
                extra={"tags": {"method": "HFToolService.huggingface_image_generation.NotFoundError"}})
        thread_repo.initialization(thread_id, thread_model)
        thread_repo.add_message_openai(error_code)

        llm_apikey_decrypt_service.update_deprecated_status(True)
        content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
        yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED

    except RateLimitError as e:
        error_content,error_code = extract_error_message(str(e))
        if error_code not in OPENAI_MESSAGES_CONFIG:
            logger.warning(
                f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                extra={"tags": {"method": "HFToolService.huggingface_image_generation.RateLimitError"}})
        else:
            logger.error(
                f"🚨 OpenAI Rate limit exceeded: {error_code}, Message: {error_content}",
                extra={"tags": {"method": "HFToolService.huggingface_image_generation.RateLimitError"}})
        thread_repo.initialization(thread_id, thread_model)
        thread_repo.add_message_openai(error_code)
        content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
        yield json.dumps({"status": status.HTTP_429_TOO_MANY_REQUESTS, "message": error_content, "data": content}), status.HTTP_429_TOO_MANY_REQUESTS

    except APIStatusError as e:
        error_content,error_code = extract_error_message(str(e))
        if not error_code or error_code not in OPENAI_MESSAGES_CONFIG:
            logger.warning(
                f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                extra={"tags": {"method": "HFToolService.huggingface_image_generation.APIStatusError"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_openai("common_response")
            content = OPENAI_MESSAGES_CONFIG.get("common_response")
            error_content = DEV_MESSAGES_CONFIG.get("unknown_message")
        else:
            logger.error(
                f"🚨 OpenAI Status Connection Error: {error_code}, Message: {error_content}",
                extra={"tags": {"method": "HFToolService.huggingface_image_generation.APIStatusError"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_openai(error_code)
            content = OPENAI_MESSAGES_CONFIG.get(error_code, OPENAI_MESSAGES_CONFIG.get("common_response"))
        yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED

    except LengthFinishReasonError as e:
        logger.error(
            f"OpenAI Length Finish Reason Error: {e}",
            extra={"tags": {"method": "HFToolService.huggingface_image_generation.LengthFinishReasonError"}})
        thread_repo.initialization(thread_id, thread_model)
        thread_repo.add_message_openai("content_filter_issue")
        content = OPENAI_MESSAGES_CONFIG.get("content_filter_issue", OPENAI_MESSAGES_CONFIG.get("common_response"))
        yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

    except ContentFilterFinishReasonError as e:
        logger.error(
            f"OpenAI Content Filter Error: {e}",
            extra={"tags": {"method": "HFToolService.huggingface_image_generation.ContentFilterFinishReasonError"}})
        thread_repo.initialization(thread_id, thread_model)
        thread_repo.add_message_openai("content_filter_issue")
        content = OPENAI_MESSAGES_CONFIG.get("content_filter_issue", OPENAI_MESSAGES_CONFIG.get("common_response"))
        yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

    except APITimeoutError as e:
            logger.error(
                f"OpenAI Timeout Error: {e}",
                extra={"tags": {"method": "HFToolService.huggingface_image_generation.APITimeoutError"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_openai("request_time_out")
            content = OPENAI_MESSAGES_CONFIG.get("request_time_out", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

    except APIConnectionError as e:
            logger.error(
                f"OpenAI Connection Error: {e}",
                extra={"tags": {"method": "ToolStreamingService.huggingface_image_generation.APIConnectionError"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_openai("connection_error")
            content = OPENAI_MESSAGES_CONFIG.get("connection_error", OPENAI_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": str(e), "data": content}), status.HTTP_417_EXPECTATION_FAILED
        
    except EntryNotFoundError as e:
        logger.error(f"Entry Not Found: {e}", extra={"tags": {"method": "HFToolService.huggingface_image_generation.EntryNotFoundError"}})
        thread_repo.initialization(thread_id, thread_model)
        thread_repo.add_message_huggingface("entry_not_found")
        content = HF_ERROR_MESSAGES_CONFIG.get("entry_not_found", HF_ERROR_MESSAGES_CONFIG.get("common_response"))
        yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": str(e), "data": content}), status.HTTP_417_EXPECTATION_FAILED
    
    except BadRequestError as e:
        logger.error(f"Bad Request Error: {e}", extra={"tags": {"method": "HFToolService.huggingface_image_generation.BadRequestError"}})
        thread_repo.initialization(thread_id, thread_model)
        thread_repo.add_message_huggingface("bad_request_error")
        content = HF_ERROR_MESSAGES_CONFIG.get("bad_request_error", HF_ERROR_MESSAGES_CONFIG.get("common_response"))
        yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": str(e), "data": content}), status.HTTP_417_EXPECTATION_FAILED
    
    except HfHubHTTPError as e:
        logger.error(f"Hugging Face Hub HTTP Error: {e}", extra={"tags": {"method": "HFToolService.huggingface_image_generation.HfHubHTTPError"}})
        thread_repo.initialization(thread_id, thread_model)
        thread_repo.add_message_huggingface("hf_hub_http_error")
        content = HF_ERROR_MESSAGES_CONFIG.get("hf_hub_http_error", HF_ERROR_MESSAGES_CONFIG.get("common_response"))
        yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": DEV_MESSAGES_CONFIG.get('hugging_face_message'), "data": content}), status.HTTP_417_EXPECTATION_FAILED
    
    except HTTPError as e:
        logger.error(f"Hugging Face HTTP Error: {e}", extra={"tags": {"method": "HFToolService.huggingface_image_generation.HTTPError"}})
        thread_repo.initialization(thread_id, thread_model)
        thread_repo.add_message_huggingface("http_error")
        content = HF_ERROR_MESSAGES_CONFIG.get("http_error", HF_ERROR_MESSAGES_CONFIG.get("common_response"))
        yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": DEV_MESSAGES_CONFIG.get('hugging_face_message'), "data": content}), status.HTTP_417_EXPECTATION_FAILED
    
    except Exception as e:
        try:
            error_content,error_code = extract_error_message(str(e))
            if error_code not in HF_ERROR_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "HFToolService.huggingface_image_generation.Exception_Except"}})
            else:
                logger.error(
                    f"🚨 Failed to stream run conversation: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "HFToolService.huggingface_image_generation.Exception_Except"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_huggingface(error_code)
            content = HF_ERROR_MESSAGES_CONFIG.get(error_code, HF_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED,"message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED  
        except Exception as e:
            logger.error(
                f"🚨 Failed to stream run conversation: {e}",
                extra={"tags": {"method": "HFToolService.huggingface_image_generation.Exception_Except"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_huggingface("common_response")
            content = HF_ERROR_MESSAGES_CONFIG.get("common_response")
            yield json.dumps({"status": status.HTTP_400_BAD_REQUEST, "message": DEV_MESSAGES_CONFIG.get("dev_message"), "data": content}), status.HTTP_400_BAD_REQUEST

def update_thread_repo_and_memory(thread_id, thread_model, optimized_query_text, s3_file_name, regenerated_flag,chat_repository_history,memory,cb,msgCredit):
    """Helper function to handle thread and memory updates concurrently."""
    thread_repo.initialization(thread_id=thread_id, collection_name=thread_model)
    thread_repo.update_token_usage(cb=cb)
    thread_repo.update_img_gen_prompt(gen_prompt=optimized_query_text)
        
    chat_repository_history.add_ai_message(message=s3_file_name, thread_id=thread_id)
    
    if not regenerated_flag:
        with get_openai_callback() as summary_cb:
            memory.prune()
            thread_repo.update_token_usage_summary(summary_cb)
            chat_repository_history.add_message_system(
                message=memory.moving_summary_buffer, thread_id=thread_id
            )