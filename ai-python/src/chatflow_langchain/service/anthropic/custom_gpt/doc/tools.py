from langchain_core.tools import tool
from langchain_community.tools.openai_dalle_image_generation import OpenAIDALLEImageGenerationTool
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from langchain.prompts import ChatPromptTemplate
from src.custom_lib.langchain.chat_models.openai.chatopenai_cache import MyChatOpenAI as ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate
from src.chatflow_langchain.utils.upload_image import upload_image_to_s3, generate_random_file_name
from src.chatflow_langchain.service.anthropic.tool_functions.config import ToolChatConfig, ImageGenerateConfig
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
from src.custom_lib.langchain.callbacks.openai.cost.cost_calc_handler import CostCalculator
from langchain_community.callbacks.manager import get_openai_callback
import json
from fastapi import status
from src.logger.default_logger import logger
from src.chatflow_langchain.service.anthropic.image.utils import extract_anthropic_error_message
from src.custom_lib.langchain.callbacks.anthropic.cost.context_manager import anthropic_async_callback
from src.custom_lib.langchain.callbacks.openai.cost.cost_calc_handler import CostCalculator
from src.custom_lib.langchain.callbacks.anthropic.mongodb.context_manager import get_mongodb_callback_handler
from src.custom_lib.langchain.callbacks.anthropic.streaming.context_manager import async_streaming_handler
from src.custom_lib.langchain.callbacks.anthropic.streaming.custom_stream_async_handler import CustomAsyncIteratorCallbackHandler
import asyncio
from src.chatflow_langchain.service.config.model_config_anthropic import ANTHROPICMODEL
from langchain.chains import LLMChain
from src.custom_lib.langchain.callbacks.openai.image_cost.context_manager import dalle_callback_handler
from src.chatflow_langchain.repositories.openai_error_messages_config import ANTHROPIC_ERROR_MESSAGES_CONFIG,DEV_MESSAGES_CONFIG
from src.crypto_hub.services.openai.llm_api_key_decryption import LLMAPIKeyDecryptionHandler
from src.custom_lib.langchain.chat_models.anthropic.chatanthropic_cache import MyChatAnthropic as ChatAnthropic
import base64
import requests
from anthropic._exceptions import (AnthropicError,APIError,APIStatusError,APIConnectionError,
    APITimeoutError, AuthenticationError, PermissionDeniedError,NotFoundError,RateLimitError)

thread_repo = ThreadRepostiory()
cost_callback = CostCalculator()
llm_apikey_decrypt_service = LLMAPIKeyDecryptionHandler()

async_handler = async_streaming_handler()

@tool
async def image_generate(image_query:bool=False, model_name=None, image_quality=None, n=1, image_size=None, image_style=None,
                         openai_api_key=None, thread_id=None, thread_model=None, memory=None, chat_repository_history=None, original_query=None,api_key_id=None,regenerated_flag=False):
    """An image generation and modification tool that enables users to create images from text descriptions and make various visual changes to the generated images. Users can remove objects, replace elements, insert new items,Edit Images and make other detailed modifications to the images directly using the tool."""
    try:
        prompt_list = chat_repository_history.messages
        if model_name == 'dall-e-2':
            prompt_list.insert(0, SystemMessagePromptTemplate.from_template(
            """Generate a detail words prompt that is helpful to generate an image exactly on the basis of the following user input And Previous image prompt. Note:-The Generated Response must be Strictly less than 125 words"""))
            max_tokens = 150
        else:
            prompt_list.insert(0, SystemMessagePromptTemplate.from_template(
            """Generate a detail words prompt that is helpful to generate an image exactly on the basis of the following user input And Previous image prompt. Note:-The Generated Response must be Strictly less than 500 words"""))
            max_tokens = 625
        prompt_list.append(HumanMessagePromptTemplate.from_template(template=[
            {"type": "text", "text": '{query}'}]))
        
        chat_prompt = ChatPromptTemplate.from_messages(prompt_list)
        cost=CostCalculator()
        async with dalle_callback_handler(llm_model=ImageGenerateConfig.GPT_4o_MINI, cost = cost,dalle_model=model_name,thread_id=thread_id,collection_name=thread_model,image_quality = image_quality,image_size=image_size,image_style=image_style) as asynchandler:
            llm = ChatOpenAI(temperature=ToolChatConfig.TEMPRATURE, api_key=openai_api_key,
                            model=ImageGenerateConfig.GPT_4o_MINI, streaming=False, stream_usage=True,max_tokens=max_tokens)
            llm_chain = LLMChain(llm=llm,prompt=chat_prompt)
            optimized_query = llm_chain.invoke(original_query,callbacks=[asynchandler])
            if model_name == 'dall-e-2' and len(optimized_query['text'])>625:
                optimized_query['text']=optimized_query['text'][:625]
            elif model_name=='dall-e-3' and len(optimized_query['text'])>2500:
                optimized_query['text']=optimized_query['text'][:2500]
                
            image_generation = OpenAIDALLEImageGenerationTool(api_wrapper=DallEAPIWrapper(
                model=model_name, n=1, quality=image_quality, size=image_size, style=image_style, api_key=openai_api_key), verbose=False)
            response = image_generation.run(optimized_query['text'],callbacks=[asynchandler])   
            # response=temp_link
            s3_file_name = generate_random_file_name()
            upload_image_to_s3(image_url=response, s3_file_name=s3_file_name)
            yield json.dumps({"status": status.HTTP_207_MULTI_STATUS, "message": s3_file_name}), status.HTTP_207_MULTI_STATUS
        # cost = CostCalculator(
        #     prompt_tokens=optimized_query.response_metadata['token_usage']['prompt_tokens'],
        #     completion_tokens=optimized_query.response_metadata['token_usage']['completion_tokens'],
        #     total_tokens=optimized_query.response_metadata['token_usage']['total_tokens'])
        # cost.calculate_total_cost(model_name=model_name)
        # token_data = {'input_tokens': cost.prompt_tokens, 'output_tokens': cost.completion_tokens, 'total_tokens': cost.total_tokens,
        #               'total_cost': DALLE_COST_PER_IMAGE[model_name][image_quality][image_size]+cost.total_cost}
        thread_repo.initialization(
            thread_id=thread_id, collection_name=thread_model)
        
        thread_repo.update_img_gen_prompt(gen_prompt=optimized_query['text'])
        
        # thread_repo.update_tools_token_data(token_data=token_data)
        chat_repository_history.add_ai_message(
            message=s3_file_name,
            thread_id=thread_id)
        if not regenerated_flag:
            with get_openai_callback() as summary_cb:
                memory.prune()

        
            thread_repo.update_token_usage_summary(summary_cb)
            chat_repository_history.add_message_system(
                message=memory.moving_summary_buffer,
                thread_id=thread_id
            )
        logger.info('Image Tool Function Completed', extra={
                    "tags": {"task_function": "image_generate"}})
        
    # Handle NotFoundError
    except NotFoundError as e:
        error_content, error_code = extract_anthropic_error_message(str(e))
        if error_code not in ANTHROPIC_ERROR_MESSAGES_CONFIG:
            logger.warning(
                f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                extra={"tags": {"method": "AnthropicToolService.image_generate.NotFoundError"}})
        else:
            logger.error(
                f"🚨 Model Not Found Error: {error_code}, Message: {error_content}",
                extra={"tags": {"method": "AnthropicToolService.image_generate.NotFoundError"}})
        thread_repo.initialization(thread_id, thread_model)
        thread_repo.add_message_openai(error_code)
        llm_apikey_decrypt_service.update_deprecated_status(True)
        content = ANTHROPIC_ERROR_MESSAGES_CONFIG.get(error_code, ANTHROPIC_ERROR_MESSAGES_CONFIG.get("common_response"))
        yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED
    
    # Handle specific errors like RateLimitError.
    except RateLimitError as e:
        error_content, error_code = extract_anthropic_error_message(str(e))
        if error_code not in ANTHROPIC_ERROR_MESSAGES_CONFIG:
            logger.warning(
                f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                extra={"tags": {"method": "AnthropicToolService.image_generate.RateLimitError"}})
        else:
            logger.error(
                f"🚨 Rate Limit Error: {error_code}, Message: {error_content}",
                extra={"tags": {"method": "AnthropicToolService.image_generate.RateLimitError"}})
        thread_repo.initialization(thread_id, thread_model)
        thread_repo.add_message_openai(error_code)
        llm_apikey_decrypt_service.initialization(api_key_id,"companymodel")
        llm_apikey_decrypt_service.update_deprecated_status(True)
        content = ANTHROPIC_ERROR_MESSAGES_CONFIG.get(error_code, ANTHROPIC_ERROR_MESSAGES_CONFIG.get("common_response"))
        yield json.dumps({"status": status.HTTP_429_TOO_MANY_REQUESTS, "message": error_content, "data": content}), status.HTTP_429_TOO_MANY_REQUESTS
    
    except APIStatusError as e:
        error_content,error_code = extract_anthropic_error_message(str(e))
        if not error_code or error_code not in ANTHROPIC_ERROR_MESSAGES_CONFIG:
            logger.warning(
                f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                extra={"tags": {"method": "AnthropicToolService.image_generate.APIStatusError"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_openai("common_response")
            content = ANTHROPIC_ERROR_MESSAGES_CONFIG.get("common_response")
            error_content = DEV_MESSAGES_CONFIG.get("unknown_message")
        else:
            logger.error(
                f"🚨 OpenAI Status Connection Error: {error_code}, Message: {error_content}",
                extra={"tags": {"method": "AnthropicToolService.image_generate.APIStatusError"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_openai(error_code)
            content = ANTHROPIC_ERROR_MESSAGES_CONFIG.get(error_code, ANTHROPIC_ERROR_MESSAGES_CONFIG.get("common_response"))
        yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED
    
    except AuthenticationError as e:
        logger.error(
            f"Anthropic Authentication Error: {e}",
            extra={"tags": {"method": "AnthropicToolService.image_generate.AuthenticationError"}})
        thread_repo.initialization(thread_id, thread_model)
        thread_repo.add_message_openai("authentication_error")
        content = ANTHROPIC_ERROR_MESSAGES_CONFIG.get("authentication_error", ANTHROPIC_ERROR_MESSAGES_CONFIG.get("common_response"))
        yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED
    
    except PermissionDeniedError as e:
        logger.error(
            f"Anthropic PermissionDenied Error: {e}",
            extra={"tags": {"method": "AnthropicToolService.image_generate.PermissionDeniedError"}})
        thread_repo.initialization(thread_id, thread_model)
        thread_repo.add_message_openai("permission_error")
        content = ANTHROPIC_ERROR_MESSAGES_CONFIG.get("permission_error", ANTHROPIC_ERROR_MESSAGES_CONFIG.get("common_response"))
        yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED
    
    except APIConnectionError as e:
        logger.error(
            f"Anthropic APIConnection Error: {e}",
            extra={"tags": {"method": "AnthropicToolService.image_generate.APIConnectionError"}})
        thread_repo.initialization(thread_id, thread_model)
        thread_repo.add_message_openai("api_connection_error")
        content = ANTHROPIC_ERROR_MESSAGES_CONFIG.get("api_connection_error", ANTHROPIC_ERROR_MESSAGES_CONFIG.get("common_response"))
        yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED
    
    except APITimeoutError as e:
        logger.error(
            f"Anthropic APITimeout Error: {e}",
            extra={"tags": {"method": "AnthropicToolService.image_generate.APITimeoutError"}})
        thread_repo.initialization(thread_id, thread_model)
        thread_repo.add_message_openai("api_timeout_error")
        content = ANTHROPIC_ERROR_MESSAGES_CONFIG.get("api_timeout_error", ANTHROPIC_ERROR_MESSAGES_CONFIG.get("common_response"))
        yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED
    
    except APIError as e:
        error_content,error_code = extract_anthropic_error_message(str(e))
        if not error_code or error_code not in ANTHROPIC_ERROR_MESSAGES_CONFIG:
            logger.warning(
                f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                extra={"tags": {"method": "AnthropicToolService.image_generate.APIError"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_openai("common_response")
            content = ANTHROPIC_ERROR_MESSAGES_CONFIG.get("common_response")
            error_content = DEV_MESSAGES_CONFIG.get("unknown_message")
        else:
            logger.error(
                f"🚨 Anthropic API Error: {error_code}, Message: {error_content}",
                extra={"tags": {"method": "AnthropicToolService.image_generate.APIError"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_openai(error_code)
            content = ANTHROPIC_ERROR_MESSAGES_CONFIG.get(error_code, ANTHROPIC_ERROR_MESSAGES_CONFIG.get("common_response"))
        yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED
    
    except AnthropicError as e:
        error_content,error_code = extract_anthropic_error_message(str(e))
        if not error_code or error_code not in ANTHROPIC_ERROR_MESSAGES_CONFIG:
            logger.warning(
                f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                extra={"tags": {"method": "AnthropicToolService.image_generate.AnthropicError"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_openai("common_response")
            content = ANTHROPIC_ERROR_MESSAGES_CONFIG.get("common_response")
            error_content = DEV_MESSAGES_CONFIG.get("unknown_message")
        else:
            logger.error(
                f"🚨 Anthropic General Error: {error_code}, Message: {error_content}",
                extra={"tags": {"method": "AnthropicToolService.image_generate.AnthropicError"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_openai(error_code)
            content = ANTHROPIC_ERROR_MESSAGES_CONFIG.get(error_code, ANTHROPIC_ERROR_MESSAGES_CONFIG.get("common_response"))
        yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED
    
    except Exception as e:
            try:
                error_content,error_code = extract_anthropic_error_message(str(e))
                if error_code not in ANTHROPIC_ERROR_MESSAGES_CONFIG:
                    logger.warning(
                        f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                        extra={"tags": {"method": "AnthropicToolService.image_generate.Exception_Try"}})
                else:
                    logger.error(
                        f"🚨 Failed to stream run conversation: {error_code}, Message: {error_content}",
                        extra={"tags": {"method": "AnthropicToolService.image_generate.Exception_Try"}})
                thread_repo.initialization(thread_id, thread_model)
                thread_repo.add_message_openai(error_code)
                content = ANTHROPIC_ERROR_MESSAGES_CONFIG.get(error_code, ANTHROPIC_ERROR_MESSAGES_CONFIG.get("common_response"))
                yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED,"message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED  
            except Exception as e:
                logger.error(
                    f"🚨 Failed to stream run conversation: {e}",
                    extra={"tags": {"method": "AnthropicToolService.image_generate.Exception_Except"}})
                thread_repo.initialization(thread_id, thread_model)
                thread_repo.add_message_openai("common_response")
                content = ANTHROPIC_ERROR_MESSAGES_CONFIG.get("common_response")
                yield json.dumps({"status": status.HTTP_400_BAD_REQUEST, "message": DEV_MESSAGES_CONFIG.get("dev_message"), "data": content}), status.HTTP_400_BAD_REQUEST

