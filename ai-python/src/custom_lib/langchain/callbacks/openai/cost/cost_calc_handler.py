from typing import Any, Dict, List
from langchain.callbacks.base import AsyncCallbackHandler
from langchain_community.callbacks.openai_info import (
    MODEL_COST_PER_1K_TOKENS,
    get_openai_token_cost_for_model,
)
from typing import Dict, List, Any
from langchain_core.messages import BaseMessage, AIMessage
from langchain_core.outputs import ChatGeneration, LLMResult
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
from langchain_community.callbacks.openai_info import standardize_model_name
from src.custom_lib.langchain.callbacks.openai.cost.web_search_cost import cost_per_request
from src.logger.default_logger import logger
import threading
from src.round_robin.llm_key_manager import APIKeySelectorService,APIKeyUsageService
from src.chatflow_langchain.service.config.model_config_openai import Functionality

MODEL_COST_PER_1K_TOKENS['chatgpt-4o-latest']=0.005
MODEL_COST_PER_1K_TOKENS['chatgpt-4o-latest-completion']=0.015


thread_repo=ThreadRepostiory()

class CostCalculator():
    def __init__(self, total_cost=0, total_tokens=0, prompt_tokens=0, completion_tokens=0):
        self.total_cost = total_cost
        self.total_tokens = total_tokens
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens

    def __str__(self):
        return (
            f"Tokens Used: {self.total_tokens}\n"
            f"\tPrompt Tokens: {self.prompt_tokens}\n"
            f"\tCompletion Tokens: {self.completion_tokens}\n"
            f"Total Cost (USD): ${self.total_cost:.4f}"
        )

    def add_prompt_tokens(self, prompt_tokens):
        self.prompt_tokens += prompt_tokens
        self.total_tokens += prompt_tokens

    def add_completion_tokens(self, completion_tokens):
        self.completion_tokens += completion_tokens
        self.total_tokens += completion_tokens

    def calculate_total_cost(self, model_name):
        if model_name in MODEL_COST_PER_1K_TOKENS:
            prompt_cost = get_openai_token_cost_for_model(model_name, self.prompt_tokens)
            completion_cost = get_openai_token_cost_for_model(model_name, self.completion_tokens, is_completion=True)
            self.total_cost = prompt_cost + completion_cost

class CostCalcCallbackHandler(AsyncCallbackHandler):
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    successful_requests: int = 0
    total_cost: float = 0.0

    def __init__(self, model_name:str, cost:CostCalculator, thread_id:str, collection_name:str,*args, **kwargs):
        self.model_name = model_name
        # self.encoding = tiktoken.encoding_for_model(model_name)
        self.cost = cost
        self.thread_id=thread_id
        self.collection_name=collection_name
        self.imageT = kwargs.get('chat_imageT', 0)
        self.isMedia=kwargs.get('isMedia',False)
        self.search_context_size=kwargs.get('search_context_size',False)
        self.encrypted_key=kwargs.get('encrypted_key',None)
        self.companyRedis_id=kwargs.get('companyRedis_id','default')
        self._lock = threading.Lock()

    def __repr__(self) -> str:
        return (
            f"Tokens Used: {self.total_tokens}\n"
            f"\tPrompt Tokens: {self.prompt_tokens}\n"
            f"\tCompletion Tokens: {self.completion_tokens}\n"
            f"Successful Requests: {self.successful_requests}\n"
            f"Total Cost (USD): ${self.total_cost}"
        )
    async def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        for prompt in prompts:
            pass

            # encoded_prompt = self.encoding.encode(prompt)
            # self.cost.add_prompt_tokens(len(encoded_prompt))
        logger.info("Processed prompts in on_llm_start",
                    extra={"tags": {"method": "CostCalcCallbackHandler.on_llm_start"}})

    async def on_chat_model_start(self, serialized: Dict[str, Any], messages: List[List[Dict[str, Any]]], **kwargs: Any) -> None:
        for message_list in messages:
            for message in message_list:
                if isinstance(message,BaseMessage):
                    if isinstance(message.content, str):
                        pass
                        # encoded_message = self.encoding.encode(message.content)
                        # self.cost.add_prompt_tokens(len(encoded_message))
                    else:
                        pass
                    
            
    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        try:
            self.api_usage_service = APIKeyUsageService()
            generation = response.generations[0][0]
        except IndexError:
            generation = None
        if isinstance(generation, ChatGeneration):
            try:
                message = generation.message
                if isinstance(message, AIMessage):
                    usage_metadata = message.usage_metadata
                    response_metadata = message.response_metadata
                else:
                    usage_metadata = None
                    response_metadata = None
            except AttributeError:
                usage_metadata = None
                response_metadata = None
        else:
            usage_metadata = None
            response_metadata = None
        if usage_metadata:
            token_usage = {"total_tokens": usage_metadata["total_tokens"]}
            completion_tokens = usage_metadata["output_tokens"]
            prompt_tokens = usage_metadata["input_tokens"]
            if response_model_name := (response_metadata or {}).get("model_name"):
                model_name = standardize_model_name(response_model_name)
            elif response.llm_output is None:
                model_name = ""
            else:
                model_name = standardize_model_name(
                    response.llm_output.get("model_name", "")
                )

        else:
            if response.llm_output is None:
                return None

            if "token_usage" not in response.llm_output:
                with self._lock:
                    self.successful_requests += 1
                return None

            # compute tokens and cost for this request
            token_usage = response.llm_output["token_usage"]
            completion_tokens = token_usage.get("completion_tokens", 0)
            prompt_tokens = token_usage.get("prompt_tokens", 0)
            model_name = standardize_model_name(
                response.llm_output.get("model_name", "")
            )
        if model_name.startswith("chatgpt-4o-latest"):
            completion_cost =MODEL_COST_PER_1K_TOKENS[f"{model_name}-completion"] * (completion_tokens / 1000)
            prompt_cost = MODEL_COST_PER_1K_TOKENS[model_name] * (prompt_tokens / 1000)
        elif model_name in MODEL_COST_PER_1K_TOKENS:
            completion_cost = get_openai_token_cost_for_model(
                model_name, completion_tokens, is_completion=True
            )
            prompt_cost = get_openai_token_cost_for_model(model_name, prompt_tokens)
        else:
            completion_cost = 0
            prompt_cost = 0
        with self._lock:
            self.total_cost += prompt_cost + completion_cost
            self.total_tokens += token_usage.get("total_tokens", 0)
            self.prompt_tokens += prompt_tokens
            self.completion_tokens += completion_tokens
            self.successful_requests += 1

        token_data =  {
            "totalUsed":self.total_tokens,
            "promptT": self.prompt_tokens,
            "completion": self.completion_tokens,
            "totalCost": self.total_cost
        }
        
        additional_data = {"imageT":self.imageT,"isMedia":self.isMedia,"webCost":0}
 
        if self.search_context_size:
            additional_data['webCost'] =cost_per_request.get(self.model_name,{}).get(self.search_context_size,0)
        thread_repo.initialization(self.thread_id, self.collection_name)
        thread_repo.update_tools_token_data(token_data,additional_data=additional_data)
        logger.info("Updated token data in database in on_llm_end",
            extra={"tags": {"method": "CostCalcCallbackHandler.on_llm_end"}})

        # await self.api_usage_service.update_usage(provider='OPEN_AI',tokens_used= self.total_tokens, model=self.model_name, api_key=self.encrypted_key,functionality=Functionality.CHAT,company_id=self.companyRedis_id)

    async def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        logger.error(f"Error occurred in LLM processing: {error}",
                     extra={"tags": {"method": "CostCalcCallbackHandler.on_llm_error"}})
        # Handle errors here if necessary
        pass

# Assuming the rest of your setup code is correct and remains unchanged
# cost = CostCalculator()
