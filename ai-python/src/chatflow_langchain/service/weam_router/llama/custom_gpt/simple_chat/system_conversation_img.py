import asyncio
import json
from src.custom_lib.langchain.chat_models.openai.chatopenai_cache import MyChatOpenAI as ChatOpenAI
from langchain.memory import ConversationSummaryBufferMemory
from bson.objectid import ObjectId
from typing import AsyncGenerator
from src.logger.default_logger import logger
from src.chatflow_langchain.service.weam_router.llama.custom_gpt.config import ToolChatConfig
from src.chat.service.base.abstract_conversation_service import AbstractConversationService
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
from src.chatflow_langchain.repositories.langchain_mongo_chat_history import CustomAIMongoDBChatMessageHistory
from src.chatflow_langchain.repositories.additional_prompts import PromptRepository
from src.chatflow_langchain.service.weam_router.llama.custom_gpt.simple_chat.chat_prompt_factory import UserCustomGPTPrompt
from src.chatflow_langchain.repositories.custom_gpt_repository import CustomGPTRepository
from src.crypto_hub.services.openai.llm_api_key_decryption import LLMAPIKeyDecryptionHandler
from src.custom_lib.langchain.callbacks.openai.cost.context_manager import get_custom_openai_callback
from src.custom_lib.langchain.callbacks.openai.cost.cost_calc_handler import CostCalculator
from src.custom_lib.langchain.callbacks.weam_router.open_router.mongodb.context_manager import get_mongodb_callback_handler
from src.custom_lib.langchain.callbacks.weam_router.open_router.streaming.context_manager import async_streaming_handler
from src.custom_lib.langchain.chain.custom_conversation_chain import CustomConversationChain
from openai import RateLimitError,APIConnectionError,APITimeoutError,APIStatusError, NotFoundError
from fastapi import HTTPException, status
from src.chatflow_langchain.service.weam_router.llama.custom_gpt.config import CustomGptChatConfig,GetLLMkey,DEFAULTMODEL,ImageGenerateConfig
from src.chatflow_langchain.utils.fill_additional_prompt import fill_template, format_website_summary_pairs
import gc
from src.gateway.openai_exceptions import LengthFinishReasonError,ContentFilterFinishReasonError
from src.chatflow_langchain.repositories.openai_error_messages_config import DEV_MESSAGES_CONFIG, WEAM_ROUTER_MESSAGES_CONFIG
from src.chatflow_langchain.service.weam_router.llama.custom_gpt.simple_chat.utils import extract_error_message
from src.chatflow_langchain.service.openai.custom_gpt.simple_chat.tools import image_generate
from langchain_community.callbacks.manager import get_openai_callback
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage

llm_apikey_decrypt_service = LLMAPIKeyDecryptionHandler()
chat_repository_history = CustomAIMongoDBChatMessageHistory()
thread_repo = ThreadRepostiory()
prompt_repo = PromptRepository()
custom_gpt_repo = CustomGPTRepository()
user_custom_prompt = UserCustomGPTPrompt()

class OpenAICustomGPTStreamingSimpleChatServiceImg(AbstractConversationService):
    def Initilization_custom_gpt(self,custom_gpt_id:str=None,customgptmodel:str=None):
        """
        Initializes the Custom GPT with the specified API key and company model.

        Parameters
        ----------
        custom_gpt_id : str, optional
            The API key ID used for decryption and initialization.
        customgptmodel : str, optional
            The company model configuration for the LLM.

        Exceptions
        ----------
        Logs an error if the initialization fails.
        """
        try:
        
            custom_gpt_repo.initialization(custom_gpt_id=custom_gpt_id, collection_name=customgptmodel)
            
        except Exception as e:
            logger.error(
                f"Failed to initialize custom gpt: {e}",
                extra={"tags": {"method": "CustomGPTStreamingSimpleChatService.Initilization_custom_gpt"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initialize custom gpt: {e}")
        
  
    def initialize_repository(self, chat_session_id: str = None, collection_name: str = None,regenerated_flag:bool=False,thread_id:str=None):
        """
        Initializes the chat history repository for data storage.

        Parameters
        ----------
        chat_session_id : str, optional
            The chat session ID for the repository.
        collection_name : str, optional
            The collection name for the repository.

        Exceptions
        ----------
        Logs an error if the repository initialization fails.
        """
        try:
            self.chat_repository_history = CustomAIMongoDBChatMessageHistory()
            self.chat_repository_history.initialize(
                chat_session_id=chat_session_id,
                collection_name=collection_name,
                thread_id=thread_id,
                regenerated_flag=regenerated_flag
            )
            self.initialize_memory()
        except Exception as e:
            logger.error(
                f"Failed to initalize repository: {e}",
                extra={"tags": {"method": "CustomGPTStreamingSimpleChatService.initialize_repository"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initalize repository: {e}")

    def initialize_llm(self, company_id:str=None,companymodel: str = None,**kwargs):
        """
        Initializes the LLM with the specified API key and company model.

        Parameters
        ----------
        companymodel : str, optional
            The company model configuration for the LLM.

        Exceptions
        ----------
        Logs an error if the initialization fails.
        """
        try:

            if kwargs.get("regenerated_flag"):
                self.api_key_id=kwargs.get('llm_apikey')
            else:
                self.api_key_id=custom_gpt_repo.get_gpt_llm_key_id()
            if self.api_key_id is None:
                get_key=GetLLMkey()
                self.query = {
                    "name": DEFAULTMODEL.GPT_4o_MINI,
                    "company.id": ObjectId(company_id)
                    }
                self.projection = {
                        '_id': 1
                    }
                self.api_key_id = get_key.default_llm_key(company_id=company_id,query=self.query,projection= self.projection,companymodel=companymodel)

            llm_apikey_decrypt_service.initialization(self.api_key_id, companymodel)

            self.llm = ChatOpenAI(
                model_name=llm_apikey_decrypt_service.model_name,
                temperature=llm_apikey_decrypt_service.extra_config.get('temperature'),
                api_key=llm_apikey_decrypt_service.decrypt(),
                streaming=True,
                verbose=False
            )
            self.llm_non_stream = ChatOpenAI(
                model_name=llm_apikey_decrypt_service.model_name,
                temperature=llm_apikey_decrypt_service.extra_config.get('temperature'),
                api_key=llm_apikey_decrypt_service.decrypt(),
                streaming=False,
                verbose=False,
            )
                
            self.tools = [image_generate,self.simple_run_conversation]
            self.llm_with_tools = self.llm_non_stream.bind_tools(
            self.tools, tool_choice='any')
            self.query_arguments = {'simple_run_conversation':{},

                                'image_generate': {'model_name': ImageGenerateConfig.LLM_IMAGE_MODEL, 'n': ImageGenerateConfig.n, 'image_quality': ImageGenerateConfig.DALLE_WRAPPER_QUALITY, 'image_size': ImageGenerateConfig.DALLE_WRAPPER_SIZE, 'image_style': ImageGenerateConfig.DALLE_WRAPPER_STYLE, 'openai_api_key': llm_apikey_decrypt_service.decrypt(),'api_key_id': self.api_key_id}}
       
       
        except Exception as e:
            logger.error(
                f"Failed to initialize LLM: {e}",
                extra={"tags": {"method": "CustomGPTStreamingSimpleChatService.initialize_llm"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to initialize LLM: {e}")
    def initialize_memory(self):
        """
        Sets up the memory component using ConversationSummaryBufferMemory.

        Exceptions
        ----------
        Logs an error if the memory initialization fails.
        """
        try:
            self.memory = ConversationSummaryBufferMemory(
                memory_key="history",
                input_key="input",
                llm=self.llm_non_stream,
                max_token_limit=CustomGptChatConfig.MAX_TOKEN_LIMIT,
                return_messages=True,
                chat_memory=self.chat_repository_history
            )
            self.memory.moving_summary_buffer = self.chat_repository_history.memory_buffer
            self.query_arguments['image_generate'].update(
                {'memory': self.memory})
        except Exception as e:
            logger.error(
                f"Failed to initalize memory: {e}",
                extra={"tags": {"method": "CustomGPTStreamingSimpleChatService.initialize_memory"}}
            )
        
   
    def prompt_attach(self, additional_prompt_id: str = None, collection_name: str = None):
        """
        Attach additional prompt information to improve the quality and accuracy of the generated content.

        This method initializes and retrieves additional prompt content based on a given prompt ID and collection name.
        The retrieved content is then attached to the main prompt object for further use.

        Parameters
        ----------
        additional_prompt_id : str, optional
            The ID of the additional prompt content to be retrieved and attached. If None, no additional content is attached.
        collection_name : str, optional
            The name of the collection where the prompt content is stored. This is required if `additional_prompt_id` is provided.

        Raises
        ------
        ValueErrordoc
            If `additional_prompt_id` is provided but `collection_name` is not.
        Exception
            For any other errors encountered during the initialization or retrieval of the prompt content.
        """
        try:
            if additional_prompt_id:
                if not collection_name:
                    raise ValueError("Collection name must be provided when additional_prompt_id is specified.")

                prompt_repo.initialization(prompt_id=additional_prompt_id, collection_name=collection_name)
                resource_key,resource_value = prompt_repo.get_resource_info()
                if resource_key is not None and resource_value is not None:
                    self.additional_prompt = fill_template(resource_key,resource_value)
                    websites = prompt_repo.get_websites()    
                    summaries = prompt_repo.get_summaries()  
                    formatted_pairs = format_website_summary_pairs(websites,summaries)
                    self.additional_prompt += formatted_pairs
                    logger.info("Successfully attached additional prompt", extra={
                        "tags": {"method": "CustomGPTStreamingSimpleChatService.prompt_attach"},
                        "additional_prompt_id": additional_prompt_id,
                        "collection_name": collection_name})
                else:
                    self.additional_prompt = None
            else:
                self.additional_prompt = None
        except Exception as e:
            logger.error(
                f"Failed to prompt attach: {e}",
                extra={"tags": {"method": "CustomGPTStreamingSimpleChatService.prompt_attach"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to prompt attach: {e}")


    def create_conversation(self,input_text:str,**kwargs):
        """
        Creates a conversation chain with a custom tag.

        Parameters
        ----------
        input_text : str
            A user input query

        Exceptions
        ----------
        Logs an error if the conversation creation fails.
        """
        try:
            
            if kwargs.get("regenerated_flag"):
                input_text = " Regenerate the above response with improvements in clarity, relevance, and depth as needed. Adjust the level of detail based on the query's requirements—providing a concise response when appropriate and a more detailed, expanded answer when necessary." + input_text
            self.user_agent_name=custom_gpt_repo.get_name()
            self.user_system_prompt=custom_gpt_repo.get_gpt_system_prompt()
            self.user_goals=custom_gpt_repo.get_gpt_goals()
            self.user_instructions=custom_gpt_repo.get_gpt_instructions()
            user_custom_prompt.initialization(user_agent_name=self.user_agent_name, \
                                              user_system_prompt=self.user_system_prompt,user_goals=self.user_goals,user_instructions=self.user_instructions)
            
            if kwargs['image_url']:
                self.prompt=user_custom_prompt.create_chat_prompt_image(additional_prompt=self.additional_prompt,**kwargs)
                self.inputs={"input": input_text,"image_url":kwargs['image_url']}
            else:
                self.prompt = user_custom_prompt.create_chat_prompt(additional_prompt=self.additional_prompt)
                self.inputs={"input": input_text}
            self.conversation = CustomConversationChain(
                prompt=self.prompt,
                llm=self.llm,
                memory=self.memory,
                verbose=False,
                
            )
        except Exception as e:
            logger.error(
                f"Failed to create conversation: {e}",
                extra={"tags": {"method": "CustomGPTStreamingSimpleChatService.create_conversation"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to create conversation: {e}")
    def _get_inputs(self):
        return self.inputs
    

    async def tool_calls_run(self, thread_id: str, collection_name: str,regenerated_flag=False, **kwargs) -> AsyncGenerator[str, None]:
        """
        Executes a conversation and updates the token usage and conversation history.

        Parameters
        ----------
        thread_id : str
            The thread ID for the conversation.
        collection_name : str
            The collection name for storing conversation history.

        Returns
        -------
        AsyncGenerator[str, None]
            An asynchronous generator yielding response tokens.

        Exceptions
        ----------
        Logs an error if the conversation execution fails.
        """
        try:
            self.thread_id = thread_id
            self.collection_name = collection_name
            self.regenerated_flag = regenerated_flag
            self.kwargs = kwargs
      
            delay_chunk = kwargs.get("delay_chunk", 0.0)
            with get_openai_callback() as cb:
                tool_history=self.chat_repository_history.messages
                
                tool_history.insert(0,SystemMessage(user_custom_prompt.get_user_system_prompt()))
                tool_history.append(HumanMessage(self.inputs['input']))
                
                ai_msg = self.llm_with_tools.invoke(tool_history)
                if ai_msg.tool_calls[0]['name'] == 'image_generate':
                    image_size = ai_msg.tool_calls[0]['args']['image_size']
                    if image_size in ToolChatConfig.IMAGE_SIZE_LIST:
                        self.query_arguments['image_generate']['image_size']=image_size
            for tool_call in ai_msg.tool_calls:
                selected_tool = {tool.name.lower(): tool for tool in self.tools}[
                    tool_call['name'].lower()]
         
                
                logger.info(f"Invoking tool: {selected_tool.name}", extra={
                "tags": {"method": "ToolStreamingService.tool_calls_run"}
            }) 
                if selected_tool.name == 'image_generate':
                    self.query_arguments['image_generate']["chat_repository_history"]= self.chat_repository_history
                    self.query_arguments['image_generate']['regenerated_flag']=regenerated_flag
                    self.query_arguments['image_generate']['thread_id']=thread_id
                    self.query_arguments['image_generate']['thread_model']=collection_name
                    self.query_arguments['image_generate']['original_query']=self.inputs['input']
                    self.query_arguments['image_generate']['user_system_prompt']=user_custom_prompt.get_user_system_prompt()
                    async for tool_output in selected_tool(self.query_arguments[selected_tool.name]):
                        yield tool_output  # Process the streamed output here
                        await asyncio.sleep(delay_chunk)

                elif selected_tool.name == 'simple_run_conversation':
                    async for tool_output in self.simple_run_conversation_v1():
                        yield tool_output  # Process the streamed output here
                        await asyncio.sleep(delay_chunk)
                break
            thread_repo.initialization(
                thread_id=thread_id, collection_name=collection_name)
            thread_repo.update_token_usage(cb=cb)

        except NotFoundError as e:
            error_content,error_code = extract_error_message(str(e))
            if error_code not in WEAM_ROUTER_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "ToolStreamingService.tool_calls_run.NotFoundError"}})
            else:
                logger.error(
                    f"🚨 Model Not Found Error: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "ToolStreamingService.tool_calls_run.NotFoundError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_weam_router(error_code)

            llm_apikey_decrypt_service.update_deprecated_status(True)
            content = WEAM_ROUTER_MESSAGES_CONFIG.get(error_code, WEAM_ROUTER_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except RateLimitError as e:
            error_content,error_code = extract_error_message(str(e))
            if error_code not in WEAM_ROUTER_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "ToolStreamingService.tool_calls_run.RateLimitError"}})
            else:
                logger.error(
                    f"🚨 OpenAI Rate limit exceeded: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "ToolStreamingService.tool_calls_run.RateLimitError"}})
            thread_repo.initialization(self.thread_id, collection_name)
            thread_repo.add_message_weam_router(error_code)
            content = WEAM_ROUTER_MESSAGES_CONFIG.get(error_code, WEAM_ROUTER_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_429_TOO_MANY_REQUESTS, "message": error_content, "data": content}), status.HTTP_429_TOO_MANY_REQUESTS
   
        except APIStatusError as e:
            error_content,error_code = extract_error_message(str(e))
            if not error_code or error_code not in WEAM_ROUTER_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "ToolStreamingService.tool_calls_run.APIStatusError"}})
                thread_repo.initialization(thread_id, collection_name)
                thread_repo.add_message_weam_router("common_response")
                content = WEAM_ROUTER_MESSAGES_CONFIG.get("common_response")
                error_content = DEV_MESSAGES_CONFIG.get("unknown_message")
            else:
                logger.error(
                    f"🚨 OpenAI Status Connection Error: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "ToolStreamingService.tool_calls_run.APIStatusError"}})
                thread_repo.initialization(self.thread_id, collection_name)
                thread_repo.add_message_weam_router(error_code)
                content = WEAM_ROUTER_MESSAGES_CONFIG.get(error_code, WEAM_ROUTER_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED


    @tool(description="simple conversation for use this tool")
    async def simple_run_conversation(self) -> AsyncGenerator[str, None]:
        """
        simple conversation for use this tool
        
        """
        pass
            


    async def simple_run_conversation_v1(self) -> AsyncGenerator[str, None]:
        """
        simple conversation for use this tool
        
        """
        try:
            
            thread_id=self.thread_id
            collection_name=self.collection_name
            delay_chunk=self.kwargs.get("delay_chunk",0.0)
            cost = CostCalculator()

            

            async with async_streaming_handler() as async_handler, \
                    get_custom_openai_callback(llm_apikey_decrypt_service.model_name, cost=cost, thread_id=self.thread_id, collection_name=self.collection_name,**self.kwargs) as cb, \
                    get_mongodb_callback_handler(thread_id=self.thread_id, chat_history=self.chat_repository_history, memory=self.memory,collection_name=self.collection_name,regenerated_flag=self.regenerated_flag,model_name=llm_apikey_decrypt_service.model_name) as mongo_handler:

                    run = asyncio.create_task( self.conversation.arun(
                        self._get_inputs(),
                        callbacks=[cb, mongo_handler, async_handler]
                    ))

                    async for token in async_handler.aiter():
                         data = token.encode("utf-8")
                         yield f"data: {data}\n\n",200
                         await asyncio.sleep(delay_chunk)
                        #  yield f"data: {json.dumps(token)}\n\n",200
                    await run
                    # cleaned_token = token.replace('"', '')  
                    # yield f"data: {json.dumps(cleaned_token)}\n\n",200

        except NotFoundError as e:
            error_content,error_code = extract_error_message(str(e))
            if error_code not in WEAM_ROUTER_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "CustomGPTStreamingSimpleChatService.stream_run_conversation.NotFoundError"}})
            else:
                logger.error(
                    f"🚨 Model Not Found Error: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "CustomGPTStreamingSimpleChatService.stream_run_conversation.NotFoundError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_weam_router(error_code)

            llm_apikey_decrypt_service.update_deprecated_status(True)
            content = WEAM_ROUTER_MESSAGES_CONFIG.get(error_code, WEAM_ROUTER_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED
 
        except RateLimitError as e:
            error_content,error_code = extract_error_message(str(e))
            if error_code not in WEAM_ROUTER_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "CustomGPTStreamingSimpleChatService.stream_run_conversation.RateLimitError"}})
            else:
                logger.error(
                    f"🚨 OpenAI Rate limit exceeded: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "CustomGPTStreamingSimpleChatService.stream_run_conversation.RateLimitError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_weam_router(error_content)
            content = WEAM_ROUTER_MESSAGES_CONFIG.get(error_code, WEAM_ROUTER_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_429_TOO_MANY_REQUESTS, "message": error_content, "data": content}), status.HTTP_429_TOO_MANY_REQUESTS

        except APIStatusError as e:
            error_content,error_code = extract_error_message(str(e))
            if not error_code or error_code not in WEAM_ROUTER_MESSAGES_CONFIG:
                logger.warning(
                    f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "CustomGPTStreamingSimpleChatService.stream_run_conversation.APIStatusError"}})
                thread_repo.initialization(self.thread_id, self.collection_name)
                thread_repo.add_message_weam_router("common_response")
                content = WEAM_ROUTER_MESSAGES_CONFIG.get("common_response")
                error_content = DEV_MESSAGES_CONFIG.get("unknown_message")
            else:
                logger.error(
                    f"🚨 OpenAI Status Connection Error: {error_code}, Message: {error_content}",
                    extra={"tags": {"method": "CustomGPTStreamingSimpleChatService.stream_run_conversation.APIStatusError"}})
                thread_repo.initialization(thread_id, collection_name)
                thread_repo.add_message_weam_router(error_code)
                content = WEAM_ROUTER_MESSAGES_CONFIG.get(error_code, WEAM_ROUTER_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except LengthFinishReasonError as e:
            logger.error(
                f"OpenAI Length Finish Reason Error: {e}",
                extra={"tags": {"method": "CustomGPTStreamingSimpleChatService.stream_run_conversation.LengthFinishReasonError"}})
            thread_repo.initialization(self.thread_id, self.collection_name)
            thread_repo.add_message_weam_router("content_filter_issue")
            content = WEAM_ROUTER_MESSAGES_CONFIG.get("content_filter_issue", WEAM_ROUTER_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except ContentFilterFinishReasonError as e:
            logger.error(
                f"OpenAI Content Filter Error: {e}",
                extra={"tags": {"method": "CustomGPTStreamingSimpleChatService.stream_run_conversation.ContentFilterFinishReasonError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_weam_router("content_filter_issue")
            content = WEAM_ROUTER_MESSAGES_CONFIG.get("content_filter_issue", WEAM_ROUTER_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except APITimeoutError as e:
            logger.error(
                f"OpenAI Timeout Error: {e}",
                extra={"tags": {"method": "CustomGPTStreamingSimpleChatService.stream_run_conversation.APITimeoutError"}}
            )
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_weam_router("request_time_out")
            content = WEAM_ROUTER_MESSAGES_CONFIG.get("request_time_out", WEAM_ROUTER_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": e, "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except APIConnectionError as e:
            logger.error(
                f"OpenAI Connection Error: {e}",
                extra={"tags": {"method": "CustomGPTStreamingSimpleChatService.stream_run_conversation.APIConnectionError"}})
            thread_repo.initialization(thread_id, collection_name)
            thread_repo.add_message_weam_router("connection_error")
            content = WEAM_ROUTER_MESSAGES_CONFIG.get("connection_error", WEAM_ROUTER_MESSAGES_CONFIG.get("common_response"))
            yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED, "message": str(e), "data": content}), status.HTTP_417_EXPECTATION_FAILED

        except Exception as e:
            try:
                error_content,error_code = extract_error_message(str(e))
                if error_code not in WEAM_ROUTER_MESSAGES_CONFIG:
                    logger.warning(
                        f"👁️ NEW ERROR CODE FOUND: {error_code}, Message: {error_content}",
                        extra={"tags": {"method": "CustomGPTStreamingSimpleChatService.stream_run_conversation.Exception_Try"}})
                else:
                    logger.error(
                        f"🚨 Failed to stream run conversation: {error_code}, Message: {error_content}",
                        extra={"tags": {"method": "CustomGPTStreamingSimpleChatService.stream_run_conversation.Exception_Try"}})
                thread_repo.initialization(thread_id, collection_name)
                thread_repo.add_message_weam_router(error_code)
                content = WEAM_ROUTER_MESSAGES_CONFIG.get(error_code, WEAM_ROUTER_MESSAGES_CONFIG.get("common_response"))
                yield json.dumps({"status": status.HTTP_417_EXPECTATION_FAILED,"message": error_content, "data": content}), status.HTTP_417_EXPECTATION_FAILED  
            except Exception as e:
                logger.error(
                    f"🚨 Failed to stream run conversation: {e}",
                    extra={"tags": {"method": "CustomGPTStreamingSimpleChatService.stream_run_conversation_Exception_Except"}})
                thread_repo.initialization(thread_id, collection_name)
                thread_repo.add_message_weam_router("common_response")
                content = WEAM_ROUTER_MESSAGES_CONFIG.get("common_response")
                yield json.dumps({"status": status.HTTP_400_BAD_REQUEST, "message": DEV_MESSAGES_CONFIG.get("dev_message"), "data": content}), status.HTTP_400_BAD_REQUEST

        finally:
            self.cleanup()

    def cleanup(self):
        """
        Cleans up any resources or state associated with the service.
        """
        cleaned_up = []
        try:
            # List of attributes to clean up
            attributes = [
                'llm',
                'llm_non_stream',
                'memory',
                'conversation',
                'inputs',
                'additional_prompt',
                'chat_repository_history',
                'conversation_summary_buffer_memory',
                'cost_calculator',
                'async_handler',
                'mongodb_handler',
                'custom_openai_callback'
            ]

            for attr in attributes:
                if hasattr(self, attr):
                    delattr(self, attr)  # Deletes the attribute from the instance
                    cleaned_up.append(attr)  # Adds the attribute name to the cleaned_up list

            gc.collect()  # Force garbage collection to free memory

            # Log a single message with the list of cleaned-up attributes
            if cleaned_up:
                logger.info(
                    f"Successfully cleaned up resources: {', '.join(cleaned_up)}.",
                    extra={"tags": {"method": "CustomGPTStreamingSimpleChatService.cleanup"}}
                )

        except Exception as e:
            logger.error(
                f"Failed to cleanup resources: {e}",
                extra={"tags": {"method": "CustomGPTStreamingSimpleChatService.cleanup"}}
            )

    async def test(self):
        """
        A simple test method to yield test events.
        """
        yield "event: streaming\ndata: Initial connection established\n\n"
        await asyncio.sleep(0.2)
        
        for words in ['k', 'a', 'b', 'c', 'd']:
            yield f"event: streaming\ndata: {words}\n\n"
            await asyncio.sleep(0.2)
