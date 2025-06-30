from typing import Any, Dict, List
import tiktoken
from langchain.callbacks.base import AsyncCallbackHandler
from langchain_community.callbacks.openai_info import (
    MODEL_COST_PER_1K_TOKENS,
    get_openai_token_cost_for_model,
)
from typing import Dict, List, Any
from langchain_core.messages import BaseMessage
from langchain.schema import LLMResult
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory

thread_repo=ThreadRepostiory()
DALLE_COST_PER_IMAGE  ={
    'dall-e-2': {
        'standard':{
        '1024x1024': 0.020,
        '512x512': 0.018,
        '256x256': 0.016,
        }
    },
    'dall-e-3': {
        'standard': {
            '1024x1024': 0.040,
            '1024x1792': 0.080,
            '1792x1024': 0.080,
        },
        'HD': {
            '1024x1024': 0.080,
            '1024x1792': 0.120,
            '1792x1024': 0.120,
        },
    }
}

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

class DalleCostcallback(AsyncCallbackHandler):
    def __init__(self, llm_model:str, dalle_model,cost:CostCalculator=CostCalculator(), thread_id:str=None, collection_name:str=None,*args, **kwargs):
        self.model_name = llm_model
        self.dalle_name = dalle_model
        self.encoding = tiktoken.encoding_for_model(llm_model)
        self.cost = cost
        self.thread_id=thread_id
        self.collection_name=collection_name
        self.isMedia=kwargs.get('isMedia',False)
        self.image_quality = kwargs.get('image_quality')
        self.image_size = kwargs.get('image_size')
        self.image_style = kwargs.get('image_style')
        self.imageT=0

    async def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        for prompt in prompts:
            encoded_prompt = self.encoding.encode(prompt)
            self.cost.add_prompt_tokens(len(encoded_prompt))

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
        
        
        if self.model_name in MODEL_COST_PER_1K_TOKENS:
            prompt_cost = get_openai_token_cost_for_model(
                self.model_name, self.cost.prompt_tokens
            )
            completion_cost = get_openai_token_cost_for_model(
                self.model_name, self.cost.completion_tokens, is_completion=True
            )
            self.cost.total_cost = prompt_cost + completion_cost
        

    async def on_tool_end(self, output: str, **kwargs: Any) -> Any:
        """Run when tool ends running."""
        self.cost.total_cost += DALLE_COST_PER_IMAGE[self.dalle_name][self.image_quality][self.image_size]
        # token_data = {
        #                 "$set": {
        #                     "tokens.totalUsed": self.cost.total_tokens,
        #                     "tokens.promptT": self.cost.prompt_tokens,
        #                     "tokens.completion": self.cost.completion_tokens,
        #                     "tokens.totalCost": f"${self.cost.total_cost}",
        #                     "tokens.imageT":self.imageT,
        #                     "isMedia":self.isMedia
        #                 }
        #             }
        token_data =  {
            "totalUsed":self.cost.total_tokens,
            "promptT": self.cost.prompt_tokens,
            "completion": self.cost.completion_tokens,
            "totalCost": self.cost.total_cost
        }
        additional_data = {"imageT":self.imageT,"isMedia":self.isMedia}
        thread_repo.initialization(self.thread_id, self.collection_name)
        thread_repo.update_tools_token_data(token_data,additional_data=additional_data)
        
    async def on_llm_error(self, error: Exception, **kwargs: Any) -> None:
        # Handle errors here if necessary
        pass

# Assuming the rest of your setup code is correct and remains unchanged
# cost = CostCalculator()