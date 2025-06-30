from typing import Any, Dict, List
import tiktoken
from langchain.callbacks.base import AsyncCallbackHandler
from langchain_community.callbacks.openai_info import (
    MODEL_COST_PER_1K_TOKENS,
    get_openai_token_cost_for_model,
)
from langchain_core.messages import BaseMessage
from langchain.schema import LLMResult
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
from src.logger.default_logger import logger

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
    def __init__(self, model_name:str, cost:CostCalculator, thread_id:str, collection_name:str,*args, **kwargs):
        self.model_name = model_name
        self.encoding = tiktoken.encoding_for_model(model_name)
        self.cost = cost
        self.thread_id=thread_id
        self.collection_name=collection_name
        self.imageT = kwargs.get('chat_imageT', 0)
        self.isMedia=kwargs.get('isMedia',False)

    async def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        for prompt in prompts:
            encoded_prompt = self.encoding.encode(prompt)
            self.cost.add_prompt_tokens(len(encoded_prompt))
        logger.info("Processed prompts in on_llm_start",
                    extra={"tags": {"method": "CostCalcCallbackHandler.on_llm_start"}})

    async def on_chat_model_start(self, serialized: Dict[str, Any], messages: List[List[Dict[str, Any]]], **kwargs: Any) -> None:
        for message_list in messages:
            for message in message_list:
                if isinstance(message,BaseMessage):
                    if isinstance(message.content, str):
                        encoded_message = self.encoding.encode(message.content)
                        self.cost.add_prompt_tokens(len(encoded_message))
                    else:
                        pass
                    
            
    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        for generation_list in response.generations:
            for generation in generation_list:
                encoded_completion = self.encoding.encode(generation.text)
                self.cost.add_completion_tokens(len(encoded_completion))
        
        total_tokens = self.cost.total_tokens  # Total count of tokens processed

        logger.info(f"Processed completions in on_llm_end. Total tokens processed: {total_tokens}",
            extra={"tags": {"method": "CostCalcCallbackHandler.on_llm_end"}})
        
        if self.model_name in MODEL_COST_PER_1K_TOKENS:
            prompt_cost = get_openai_token_cost_for_model(
                self.model_name, self.cost.prompt_tokens+self.imageT
            )
            completion_cost = get_openai_token_cost_for_model(
                self.model_name, self.cost.completion_tokens, is_completion=True
            )
            self.cost.total_cost = prompt_cost + completion_cost

        # token_data = {
        #             "$set": {
        #                 "tokens.totalUsed": self.cost.total_tokens,
        #                 "tokens.promptT": self.cost.prompt_tokens,
        #                 "tokens.completion": self.cost.completion_tokens,
        #                 "tokens.totalCost": f"${self.cost.total_cost}",
        #                 "tokens.imageT":self.imageT,
        #                 "isMedia":self.isMedia
        #             }
        #         }
        token_data =  {
            "totalUsed":self.cost.total_tokens,
            "promptT": self.cost.prompt_tokens,
            "completion": self.cost.completion_tokens,
            "totalCost": self.cost.total_cost
        }
        additional_data = {"imageT":self.imageT,"isMedia":self.isMedia}
        thread_repo.initialization(self.thread_id, self.collection_name)
        thread_repo.update_tools_token_data(token_data,additional_data=additional_data)
        logger.info("Updated token data in database in on_llm_end",
            extra={"tags": {"method": "CostCalcCallbackHandler.on_llm_end"}})


    async def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        logger.error(f"Error occurred in LLM processing: {error}",
                     extra={"tags": {"method": "CostCalcCallbackHandler.on_llm_error"}})
        # Handle errors here if necessary
        pass

# Assuming the rest of your setup code is correct and remains unchanged
# cost = CostCalculator()
