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
thread_repo = ThreadRepostiory()
cost_callback = CostCalculator()
llm_apikey_decrypt_service = LLMAPIKeyDecryptionHandler()

async_handler = async_streaming_handler()

@tool(description=HfToolDescription.SIMPLE_CHAT_V2)
async def simple_chat_v2():
    
    pass
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
        cost=CostCalculator()
        list_of_endpoints = list_inference_endpoints(token=hf_token)

            # Loop through the endpoints
        for i in range(len(list_of_endpoints)):
            if list_of_endpoints[i].repository == repo:
                # Check for specific statuses
                if list_of_endpoints[i].status in ['scaledToZero', 'initializing']:
                    raise HfHubHTTPError(message=f"Endpoint is not ready: {list_of_endpoints[i].status}")
        with get_openai_callback() as cb:
            llm = ChatOpenAI(temperature=ToolChatConfig.TEMPRATURE, api_key=openai_key,use_responses_api=True,
                                model=ImageGenerateConfig.GPT_4o_MINI, streaming=False, stream_usage=True,max_tokens=max_tokens)
            llm_chain = LLMChain(llm=llm,prompt=chat_prompt)
            optimized_query = llm_chain.invoke(original_query)
        if len(optimized_query['text'])>625:
                optimized_query['text']=optimized_query['text'][:625]
        client = InferenceClient(token=hf_token,model=endpoint_url)
        response = client.text_to_image(prompt=optimized_query['text'],height=height,width=width,num_inference_steps=num_inference_steps,guidance_scale=guidance_scale)
        s3_file_name = generate_random_file_name()
        thread_repo_task =asyncio.to_thread(update_thread_repo_and_memory,thread_id, thread_model, optimized_query['text'], s3_file_name, regenerated_flag, chat_repository_history, memory, cb,msgCredit)
        
        logger.info(f"Image successfully generated Ready for Uploading S3 bucket with filename: {s3_file_name} ...")
        image_bytes=convert_image_to_bytes(image=response)
        
        result=task_upload_huggingfaceimage_to_s3.apply_async(kwargs={'image_bytes': image_bytes, 's3_file_name': s3_file_name}).get()
        delete_resources(response=response, image_bytes=image_bytes, client=client)

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
@tool
async def simple_chat_v2_real(query:bool=False, openai_api_key=None, temperature=None, endpoint_url=None,repetition_penalty=1.03,typical_p=0.95,streaming=False,stop_sequences=['<|eot_id|>'],top_k=10,top_p=0.95,hf_token=None,
                         image_url=None, thread_id=None, thread_model=None, imageT=0, memory=None, chat_repository_history=None, original_query=None,api_key_id=None,regenerated_flag=False,vision=False,model_name=None,msgCredit=0,is_paid_user=False):
    """A versatile conversation tool designed to generate responses for various user inputs, including code, text-related queries, and image descriptions.
        When to use this tool:

        Responding to general questions.
        Handling code or text-related queries.
        Providing descriptions for images based on user requests.

    """
    # Set model parameters here
    try:    
        kwargs = {"chat_imageT":imageT}
        custom_handler = CustomAsyncIteratorCallbackHandler()
        llm_huggingface = HuggingFaceEndpoint(
            endpoint_url= endpoint_url,
            top_k=top_k,
            top_p=top_p,
            typical_p=typical_p,
            temperature=temperature,
            repetition_penalty=repetition_penalty,
            streaming=streaming,
            do_sample=True,
            stop_sequences=stop_sequences,
            huggingfacehub_api_token=hf_token,
            max_new_tokens=ToolChatConfig.MAX_TOTAL_TOKENS
            )
        chat_model = ChatHuggingFace(llm=llm_huggingface,callbacks=[custom_handler])
        prompt_list = chat_repository_history.messages
        if image_url is not None and vision:
            # prompt_list.insert(0, SystemMessagePromptTemplate.from_template(
            # """You're a helpful assistant Use your knowledge to provide a clear, concise, and relevant response to the user's question. 
            #    """))
            prompt_list.append(HumanMessagePromptTemplate.from_template(template=[
                {"type": "text", "text": '{query}'},
                {"type": "image_url", "image_url": "{image_url}"}]))
            chat_prompt = ChatPromptTemplate.from_messages(prompt_list)
            # final_response = ''
            llm_chain = LLMChain(llm=chat_model, prompt=chat_prompt)
            cost = CostCalculator()
            async with get_custom_huggingface_callback(model_name, cost=cost, thread_id=thread_id, collection_name=thread_model,**kwargs), \
                    get_mongodb_callback_handler(thread_id=thread_id, chat_history=chat_repository_history, memory=memory,collection_name=thread_model,regenerated_flag=regenerated_flag,msgCredit=msgCredit,is_paid_user=is_paid_user) as mongo_handler:
                run = asyncio.create_task(llm_chain.arun(
                    {"query":original_query,"image_url":image_url},callbacks=[mongo_handler]))
            # async for chunk in llm_chain.astream({"query": original_query, "image_url": image_url}):
            #     final_response += chunk.content
            #     yield f"data: {chunk.content}\n\n", 200
            # chat_repository_history.add_ai_message(final_response, thread_id)
            # try: 
            async for token in custom_handler.aiter():
                yield f"data: {token.encode('utf-8')}\n\n", 200
            await run
            # except Exception as e:
            #         raise e
            # finally:
            #         custom_handler.queue.task_done()
            #         custom_handler.done.clear()

        else:
            # prompt_list.insert(0, SystemMessagePromptTemplate.from_template(
            # """You are a helpful assistant who can both describe images and answer general questions also user can ask modify or improved or optimize above repsonse.
            #    Adapt the conversation flow: Tailor your responses and interaction style according to past conversations,and the user’s preferences to ensure the conversation is smooth and relevant

            #    For general queries: if a user asks a question general queries, give accurate, concise, and informative answers based on your knowledge.
               
            #    For image descriptions: if a user asks for details about an image, provide a description based on the prompts previously generated for that image.

            #    Response optimization: If requested, modify, improve, or optimize your previous ai response.
               
            #    """))
            # prompt_list.insert(0, SystemMessagePromptTemplate.from_template(
            # """
            #    For image descriptions: if a user asks for details about an image, provide a description based on the prompts previously generated for that image.
            #    """))
            prompt_list.append(HumanMessagePromptTemplate.from_template("Text:{query}"))
            chat_prompt = ChatPromptTemplate.from_messages(prompt_list)
            # history_prompt = "Adapt the conversation flow: Use the prior messages in the current conversation to leverage the ongoing chat history, ensuring smooth, relevant, and cohesive interactions."
            # final_response = ''
            llm_chain = LLMChain(llm=chat_model, prompt=chat_prompt)
            cost = CostCalculator()
            async with get_custom_huggingface_callback(model_name, cost=cost, thread_id=thread_id, collection_name=thread_model,**kwargs),\
                    get_mongodb_callback_handler(thread_id=thread_id, chat_history=chat_repository_history, memory=memory,collection_name=thread_model,regenerated_flag=regenerated_flag,is_paid_user=is_paid_user) as mongo_handler:
                run = asyncio.create_task(llm_chain.arun(
                    original_query,callbacks=[mongo_handler]))
            # async for chunk in llm_chain.astream({"query": original_query}):
            #     final_response += chunk.content
            #     yield f"data: {chunk.content}\n\n", 200
            # chat_repository_history.add_ai_message(final_response, thread_id)
                # try:
                async for token in custom_handler.aiter():
                    yield f"data: {token.encode('utf-8')}\n\n", 200
                await run
                # except Exception as e:
                #     raise e
                # finally:
                #     custom_handler.queue.task_done()
                #     custom_handler.done.clear()
                    

    #     chunk.usage_metadata['input_tokens'] += imageT
    #     chunk.usage_metadata['total_tokens'] += imageT
    #     token_data = chunk.usage_metadata
    # # Calculate cost using updated usage metadata
    #     cost = CostCalculator(
    #         prompt_tokens=chunk.usage_metadata['input_tokens'],
    #         completion_tokens=chunk.usage_metadata['output_tokens'],
    #         total_tokens=chunk.usage_metadata['total_tokens']
    #     )
    #     cost.calculate_total_cost(model_name=model_name)
    #     token_data.update(total_cost=cost.total_cost)

    #     thread_repo.initialization(
    #         thread_id=thread_id, collection_name=thread_model)
    #     thread_repo.update_tools_token_data(token_data=token_data)
        # with get_openai_callback() as summary_cb:
        #     memory.prune()

        # thread_repo.update_token_usage_summary(cb=summary_cb)
        # chat_repository_history.add_message_system(
        #     message=memory.moving_summary_buffer,
        #     thread_id=thread_id
        # )
        logger.info('Simple chat Tool Function Completed', extra={
                    "tags": {"task_function": "simple_chat_v2"}})
        
    # Handling errors from Hugging Face libraries
    except ValueError as e:
        logger.error(f"Hugging Face Value Error: {e}", extra={"tags": {"method": "HFToolService.simple_chat_v2.ValueError"}})
        thread_repo.initialization(thread_id, thread_model)
        thread_repo.add_message_huggingface("value_error")
        content = HF_ERROR_MESSAGES_CONFIG.get("value_error", HF_ERROR_MESSAGES_CONFIG.get("common_response"))
        yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": str(e), "data": content}), status.HTTP_417_EXPECTATION_FAILED
    
    except RuntimeError as e:
        logger.error(f"Hugging Face Runtime Error: {e}", extra={"tags": {"method": "HFToolService.simple_chat_v2.RuntimeError"}})
        thread_repo.initialization(thread_id, thread_model)
        thread_repo.add_message_huggingface("runtime_error")
        content = HF_ERROR_MESSAGES_CONFIG.get("runtime_error", HF_ERROR_MESSAGES_CONFIG.get("common_response"))
        yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": str(e), "data": content}), status.HTTP_417_EXPECTATION_FAILED
    
    # Hugging Face Hub Exceptions
    except EntryNotFoundError as e:
        logger.error(f"Entry Not Found: {e}", extra={"tags": {"method": "HFToolService.simple_chat_v2.EntryNotFoundError"}})
        thread_repo.initialization(thread_id, thread_model)
        thread_repo.add_message_huggingface("entry_not_found")
        content = HF_ERROR_MESSAGES_CONFIG.get("entry_not_found", HF_ERROR_MESSAGES_CONFIG.get("common_response"))
        yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": str(e), "data": content}), status.HTTP_417_EXPECTATION_FAILED
    
    except BadRequestError as e:
        logger.error(f"Bad Request Error: {e}", extra={"tags": {"method": "HFToolService.simple_chat_v2.BadRequestError"}})
        thread_repo.initialization(thread_id, thread_model)
        thread_repo.add_message_huggingface("bad_request_error")
        content = HF_ERROR_MESSAGES_CONFIG.get("bad_request_error", HF_ERROR_MESSAGES_CONFIG.get("common_response"))
        yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": str(e), "data": content}), status.HTTP_417_EXPECTATION_FAILED
    
    except HfHubHTTPError as e:
        logger.error(f"Hugging Face Hub HTTP Error: {e}", extra={"tags": {"method": "HFToolService.simple_chat_v2.HfHubHTTPError"}})
        thread_repo.initialization(thread_id, thread_model)
        thread_repo.add_message_huggingface("hf_hub_http_error")
        content = HF_ERROR_MESSAGES_CONFIG.get("hf_hub_http_error", HF_ERROR_MESSAGES_CONFIG.get("common_response"))
        yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": DEV_MESSAGES_CONFIG.get('hugging_face_message'), "data": content}), status.HTTP_417_EXPECTATION_FAILED
    
    except HTTPError as e:
        logger.error(f"Hugging Face HTTP Error: {e}", extra={"tags": {"method": "HFToolService.simple_chat_v2.HTTPError"}})
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
                    extra={"tags": {"method": "HFToolService.simple_chat_v2.Exception_Except"}})
            else:
                logger.error(
                    f"🚨 Failed to stream run conversation: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "HFToolService.simple_chat_v2.Exception_Except"}})
            thread_repo.initialization(thread_id, thread_model)
            thread_repo.add_message_huggingface(error_code)
            content = HF_ERROR_MESSAGES_CONFIG.get(error_code, HF_ERROR_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED,"message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED  
        except Exception as e:
            logger.error(
                f"🚨 Failed to stream run conversation: {e}",
                extra={"tags": {"method": "HFToolService.simple_chat_v2.Exception_Except"}})
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