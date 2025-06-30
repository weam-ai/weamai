from typing import Any, Dict, List
import tiktoken
from langchain.callbacks.base import AsyncCallbackHandler
from typing import Dict, List, Any, Generator
from langchain_core.messages import BaseMessage
from langchain.schema import LLMResult
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
from src.logger.default_logger import logger
import threading
from typing import Any, Dict, List, Union
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, LLMResult
thread_repo=ThreadRepostiory()

MODEL_COST_PER_1K_INPUT_TOKENS = {
    "deepseek/deepseek-r1":0.00055,
    "deepseek/deepseek-r1-distill-llama-70b": 0.00023,
    "deepseek/deepseek-r1-distill-qwen-32b":0.0007,
    "deepseek/deepseek-r1:free":0
}   

MODEL_COST_PER_1K_OUTPUT_TOKENS = {
    "deepseek/deepseek-r1":0.00219,
    "deepseek/deepseek-r1-distill-llama-70b": 0.00069,
    "deepseek/deepseek-r1-distill-qwen-32b":0.0007,
    "deepseek/deepseek-r1:free":0
}


def _get_deepseek_token_cost(
    prompt_tokens: int, completion_tokens: int, model_id: Union[str, None]
) -> float:
    """Get the cost of tokens for the Claude model."""

    return (prompt_tokens / 1000) * MODEL_COST_PER_1K_INPUT_TOKENS[model_id] + (
        completion_tokens / 1000
    ) * MODEL_COST_PER_1K_OUTPUT_TOKENS[model_id]


class DeepSeekTokenUsageCallbackAsync(AsyncCallbackHandler):
    """Callback Handler that tracks bedrock anthropic info."""
    
    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    successful_requests: int = 0
    total_cost: float = 0.0
    def __init__(self, model_name:str, thread_id:str, collection_name:str,*args, **kwargs):
        self.model_name = model_name
        self.thread_id=thread_id
        self.collection_name=collection_name
        self.imageT = kwargs.get('chat_imageT', 0)
        self.isMedia=kwargs.get('isMedia',False)
        self._lock = threading.Lock()

    def __repr__(self) -> str:
        return (
            f"Tokens Used: {self.total_tokens}\n"
            f"\tPrompt Tokens: {self.prompt_tokens}\n"
            f"\tCompletion Tokens: {self.completion_tokens}\n"
            f"Successful Requests: {self.successful_requests}\n"
            f"Total Cost (USD): ${self.total_cost}"
        )

    @property
    async def always_verbose(self) -> bool:
        """Whether to call verbose callbacks even if verbose is False."""
        return True


    async def on_chat_model_start(
        self, serialized: Dict[str, Any], messages, **kwargs: Any
    ) -> Any:
        """Run when Chat Model starts running."""
        pass

    async def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Print out the prompts."""
        pass

    async def on_llm_new_token(self, token: str,**kwargs: Any) -> None:
        """Print out the token."""
        """Collect token usage."""
        
     


    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Collect token usage."""

        generations = response.generations[0][0]
       
        # compute tokens and cost for this request
        
        completion_tokens = generations.message.usage_metadata['output_tokens']
        prompt_tokens = generations.message.usage_metadata['input_tokens']
        total_tokens = generations.message.usage_metadata['total_tokens']
        # model_id = response.response.get("model", None)
        prompt_tokens += self.imageT
        total_cost = _get_deepseek_token_cost(
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            model_id=self.model_name,
        )
        # update shared state behind lock
        with self._lock:
            self.total_cost += total_cost
            self.total_tokens += total_tokens
            self.prompt_tokens += prompt_tokens
            self.completion_tokens += completion_tokens
            self.successful_requests += 1

        token_data =  {
            "totalUsed":self.total_tokens,
            "promptT": self.prompt_tokens,
            "completion": self.completion_tokens,
            "totalCost": self.total_cost
        }
        additional_data = {"imageT":self.imageT,"isMedia":self.isMedia}
        thread_repo.initialization(self.thread_id, self.collection_name)
        thread_repo.update_tools_token_data(token_data,additional_data=additional_data)
        logger.info("Updated token data in database in on_llm_end",
            extra={"tags": {"method": "CostCalcCallbackHandler.on_llm_end"}})

    async def __copy__(self) -> "WeamDeepSeekUsageCallbackAsync":
        """Return a copy of the callback handler."""
        return self

    async def __deepcopy__(self, memo: Any) -> "WeamDeepSeekUsageCallbackAsync":
        """Return a deep copy of the callback handler."""
        return self

# Assuming the rest of your setup code is correct and remains unchanged
# cost = CostCalculator()




class DeepSeekTokenUsageCallbackSync(BaseCallbackHandler):
    """Callback Handler that tracks OpenAI info."""

    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    successful_requests: int = 0
    total_cost: float = 0.0

    def __init__(self,model_name:str) -> None:
        super().__init__()
        self._lock = threading.Lock()
        self.model_name = model_name

    def __repr__(self) -> str:
        return (
            f"Tokens Used: {self.total_tokens}\n"
            f"\tPrompt Tokens: {self.prompt_tokens}\n"
            f"\tCompletion Tokens: {self.completion_tokens}\n"
            f"Successful Requests: {self.successful_requests}\n"
            f"Total Cost (USD): ${self.total_cost}"
        )

    @property
    def always_verbose(self) -> bool:
        """Whether to call verbose callbacks even if verbose is False."""
        return True

    def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Print out the prompts."""
        pass

    def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        """Print out the token."""
        pass

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Collect token usage."""
        # Check for usage_metadata (langchain-core >= 0.2.2)
        generations = response.generations[0][0]
       
        # compute tokens and cost for this request
        
        completion_tokens = generations.message.usage_metadata.get('output_tokens',0)
        prompt_tokens = generations.message.usage_metadata.get('input_tokens',0)
        total_tokens = generations.message.usage_metadata.get('total_tokens',0)

            
        if self.model_name in MODEL_COST_PER_1K_INPUT_TOKENS:
            total_cost = _get_deepseek_token_cost(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                model_id=self.model_name,
            )

        # update shared state behind lock
        with self._lock:
            self.total_cost += total_cost
            self.total_tokens += total_tokens
            self.prompt_tokens += prompt_tokens
            self.completion_tokens += completion_tokens
            self.successful_requests += 1

    def __copy__(self) -> "WeamDeepSeekTokenUsageCallbackSync":
        """Return a copy of the callback handler."""
        return self

    def __deepcopy__(self, memo: Any) -> "WeamDeepSeekTokenUsageCallbackSync":
        """Return a deep copy of the callback handler."""
        return self