from concurrent.futures import thread
from typing import Any, Dict, List
from langchain.callbacks.base import AsyncCallbackHandler
import msgpack
from src.logger.default_logger import logger
from langchain.schema import LLMResult
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
from src.custom_lib.langchain.callbacks.gemini.cost.context_manager import gemini_sync_cost_handler
from src.chatflow_langchain.repositories.company_repository import CompanyRepostiory
from src.round_robin.llm_key_manager import APIKeyUsageService
from src.chatflow_langchain.service.config.model_config_gemini import Functionality
from src.chatflow_langchain.repositories.brain_repository import BrainRepository
from langchain_core.messages import SystemMessage, HumanMessage
import re
company_repo=CompanyRepostiory()
thread_repo=ThreadRepostiory()
brain_repo = BrainRepository()

class MongoDBCallbackHandler(AsyncCallbackHandler):
    def __init__(self, thread_id: str = None, chat_history: str = None, memory=None,collection_name=None,regenerated_flag=False,model_name=None,msgCredit=0,is_paid_user=False,*args, **kwargs):
        self.thread_id = thread_id
        self.chat_history = chat_history
        self.memory = memory
        self.stream_flag = False
        self.collection_name=collection_name
        self.regenerated_flag = regenerated_flag
        self.model_name =model_name
        self.msgCredit=msgCredit
        self.is_paid_user=is_paid_user
        self.kwargs = kwargs
        self.encrypted_key= kwargs.get('encrypted_key',None)
        self.companyRedis_id=kwargs.get('companyRedis_id','default')
        self.brain_id = kwargs.get('brain_id',None)
        self.tool_service_llm = kwargs.get('tool_service_llm',None)
    async def on_chat_model_start(self, serialized: Dict[str, Any], messages: List[List[Dict[str, Any]]], **kwargs: Any) -> None:
        pass
    
    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        if token is not None and token != "":
            self.stream_flag = True

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        try:
            self.api_usage_service = APIKeyUsageService()
            self.messages = ''
            if self.stream_flag:
                for generation_list in response.generations:
                    for generation in generation_list:
                        self.messages += generation.text

                allowed_keys = {'video_context','audio_context','total_duration'}
                filtered_kwargs = {k: v for k, v in self.kwargs.items() if k in allowed_keys}

                if filtered_kwargs:
                    self.chat_history.add_ai_message_kwargs(
                        message=self.messages,
                        thread_id=self.thread_id,
                        **filtered_kwargs
                    )
                else:
                    self.chat_history.add_ai_message(
                        message=self.messages,
                        thread_id=self.thread_id
                    )
                thread_repo.initialization(thread_id=self.thread_id,collection_name=self.collection_name)
                
                # Check if we should revise customInstructions for this brain
                if self.brain_id and self.tool_service_llm:
                    # Initialize the brain repository
                    brain_repo.initialization(self.brain_id)
                    
                    # Check if we should revise instructions
                    should_revise = await brain_repo.should_revise_instructions()
                    
                    if should_revise:
                        logger.info(
                            f"Triggering customInstructions revision for brain {self.brain_id}",
                            extra={"tags": {"method": "MongoDBCallbackHandler.on_llm_end"}}
                        )
                        
                        # Get current instructions
                        current_instructions_msg = brain_repo.get_custom_instructions()
                        current_instructions = current_instructions_msg.content if current_instructions_msg else ""
                        
                        # Get recent messages for context
                        recent_messages = await brain_repo.get_recent_messages()
                        message_context = self._format_message_context(recent_messages)
                        
                        # Generate revised instructions
                        revised_instructions = await self._generate_revised_instructions(current_instructions, message_context)
                        
                        if revised_instructions:
                            # Update the brain with revised instructions
                            await brain_repo.update_custom_instructions(revised_instructions)
                
                if self.is_paid_user:
                    thread_repo.update_credits(msgCredit=self.msgCredit)
                else:
                    company_repo.initialization(company_id=str(thread_repo.result['companyId']),collection_name='company')
                    company_repo.update_free_messages(model_code='GEMINI')
                if not self.regenerated_flag:
                    with gemini_sync_cost_handler(model_name=self.model_name) as cb:
                        self.memory.prune()
                    match = re.search(r'(?<=\/)[^\/]+$', self.memory.llm.model)
                    # await self.api_usage_service.update_usage(provider='GEMINI',tokens_used= cb.total_tokens, model=match.group(), api_key=self.encrypted_key,functionality=Functionality.CHAT,company_id=self.companyRedis_id)

                    thread_repo.update_token_usage_summary(cb=cb)
                    self.chat_history.add_message_system(
                        message=self.memory.moving_summary_buffer,
                        thread_id=self.thread_id
                    )
                else: 
                        thread_repo.update_response_model(responseModel=self.model_name,model_code='GEMINI')
                logger.info(
                    "Successfully stored the response",
                    extra={"tags": {"method": "MongoDBCallbackHandler.on_llm_end"}}
                )
            else:
                logger.info(
                    "LLM response was condensed, no storage needed",
                    extra={"tags": {"method": "MongoDBCallbackHandler.on_llm_end"}}
                )
        except Exception as e:
            logger.error(
                "Error processing LLM response",
                exc_info=True,
                extra={"tags": {"method": "MongoDBCallbackHandler.on_llm_end", "exception": str(e)}}
            )
            raise e

    async def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        logger.error(
            "Error encountered during LLM execution",
            exc_info=True,
            extra={"tags": {"method": "MongoDBCallbackHandler.on_llm_error", "exception": str(error)}}
        )
        pass
        
    def _format_message_context(self, recent_messages):
        """
        Format recent messages for context.
        
        Args:
            recent_messages: List of recent messages (already decrypted).
            
        Returns:
            str: Formatted message context.
        """
        message_context = ""
        for msg in recent_messages:
            if 'message' in msg and msg['message']:
                message_context += f"User: {msg['message']}\n"
            if 'ai' in msg and msg['ai']:
                message_context += f"AI: {msg['ai']}\n"
        return message_context
    
    async def _generate_revised_instructions(self, current_instructions, message_context):
        """
        Generate revised customInstructions using the tool service's LLM.
        
        Args:
            current_instructions: Current custom instructions.
            message_context: Formatted message context.
            
        Returns:
            str: Revised custom instructions.
        """
        try:
            if not self.tool_service_llm:
                logger.warning(
                    "No tool service LLM available for generating revised instructions",
                    extra={"tags": {"method": "MongoDBCallbackHandler._generate_revised_instructions"}}
                )
                return None
                
            # Create messages for the LLM
            messages = [
                SystemMessage(content="You are an AI assistant that helps improve custom instructions based on conversation history. Your task is to analyze the current instructions and recent conversation, then suggest improvements to make the instructions more clear, effective, and tailored to the user's needs."),
                HumanMessage(content=f"Current instructions:\n{current_instructions}\n\nRecent conversation:\n{message_context}\n\nPlease provide revised instructions that incorporate insights from the recent conversation while maintaining the original intent. Focus on clarity, specificity, and addressing any recurring themes or needs shown in the conversation.")
            ]
            
            # Use the tool service's LLM to generate revised instructions
            response = await self.tool_service_llm.ainvoke(messages)
            logger.info(
                "Successfully generated revised instructions",
                extra={"tags": {"method": "MongoDBCallbackHandler._generate_revised_instructions"}}
            )
            
            return response.content
        except Exception as e:
            logger.error(
                "Error generating revised instructions",
                exc_info=True,
                extra={"tags": {"method": "MongoDBCallbackHandler._generate_revised_instructions", "exception": str(e)}}
            )
            return None
