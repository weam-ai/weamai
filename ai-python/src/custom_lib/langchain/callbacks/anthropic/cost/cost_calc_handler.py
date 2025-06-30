from typing import Any, Dict, List
from langchain.callbacks.base import AsyncCallbackHandler
from langchain.schema import LLMResult
from src.chatflow_langchain.repositories.thread_repository import ThreadRepostiory
from src.logger.default_logger import logger
import threading
from typing import Any, Dict, List, Union
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, LLMResult
from src.round_robin.llm_key_manager import APIKeySelectorService,APIKeyUsageService
from src.chatflow_langchain.service.config.model_config_anthropic import Functionality
thread_repo=ThreadRepostiory()

MODEL_COST_PER_1K_INPUT_TOKENS = {
    "claude-instant-1.2": 0.0008,
    "claude-2.1": 0.008,
    "claude-2.0": 0.008,
    "claude-3-sonnet-20240229": 0.003,
    "claude-3-haiku-20240307": 0.00025,
    "claude-3-opus-20240229": 0.015,
    "claude-3-opus-latest":0.015,
    "claude-3-5-sonnet-20241022": 0.003,
    "claude-3-5-sonnet-latest":0.003,
    "claude-3-5-haiku-20241022": 0.001,
    "claude-3-5-haiku-latest":0.001,
    "claude-3-7-sonnet-latest":0.003,
    "claude-3-7-sonnet-20250219":0.003,
    "claude-opus-4-20250514":0.015,
    "claude-opus-4-0":0.015,
    "claude-sonnet-4-20250514":0.003,
    "claude-sonnet-4-0":0.003
}   

MODEL_COST_PER_1K_OUTPUT_TOKENS = {
    "claude-instant-1.2": 0.0024,
    "claude-2.1": 0.024,
    "claude-2.0": 0.024,
    "claude-3-sonnet-20240229": 0.015,
    "claude-3-haiku-20240307": 0.00125,
    "claude-3-opus-20240229": 0.075,
    "claude-3-opus-latest":0.075,
    "claude-3-5-sonnet-20241022": 0.015,
    "claude-3-5-sonnet-latest":0.015,
    "claude-3-5-haiku-20241022": 0.005,
    "claude-3-5-haiku-latest":0.005,
    "claude-3-7-sonnet-latest":0.015,
    "claude-3-7-sonnet-20250219":0.015,
    "claude-opus-4-20250514":0.075,
    "claude-opus-4-0":0.075,
    "claude-sonnet-4-20250514":0.015,
    "claude-sonnet-4-0":0.015
}


def _get_anthropic_claude_token_cost(
    prompt_tokens: int, completion_tokens: int, model_id: Union[str, None]
) -> float:
    """Get the cost of tokens for the Claude model."""

    return (prompt_tokens / 1000) * MODEL_COST_PER_1K_INPUT_TOKENS[model_id] + (
        completion_tokens / 1000
    ) * MODEL_COST_PER_1K_OUTPUT_TOKENS[model_id]


class AnthropicTokenUsageCallbackAsync(AsyncCallbackHandler):
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
        self.api_usage_service = APIKeyUsageService()
        generations = response.generations[0][0]
       
        # compute tokens and cost for this request
        
        completion_tokens = generations.message.usage_metadata['output_tokens']
        prompt_tokens = generations.message.usage_metadata['input_tokens']
        total_tokens = generations.message.usage_metadata['total_tokens']
        # model_id = response.response.get("model", None)
        prompt_tokens += self.imageT
        total_cost = _get_anthropic_claude_token_cost(
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
        # await self.api_usage_service.update_usage_anthropic(provider='ANTHROPIC',tokens_used= token_data, model=self.model_name, api_key=self.encrypted_key,functionality=Functionality.CHAT,company_id=self.companyRedis_id)
        additional_data = {"imageT":self.imageT,"isMedia":self.isMedia}
        thread_repo.initialization(self.thread_id, self.collection_name)
        thread_repo.update_tools_token_data(token_data,additional_data=additional_data)
        logger.info("Updated token data in database in on_llm_end",
            extra={"tags": {"method": "CostCalcCallbackHandler.on_llm_end"}})

    async def __copy__(self) -> "AnthropicTokenUsageCallbackAsync":
        """Return a copy of the callback handler."""
        return self

    async def __deepcopy__(self, memo: Any) -> "AnthropicTokenUsageCallbackAsync":
        """Return a deep copy of the callback handler."""
        return self

# Assuming the rest of your setup code is correct and remains unchanged
# cost = CostCalculator()




class AnthropicTokenUsageCallbackSync(BaseCallbackHandler):
    """Callback Handler that tracks OpenAI info."""

    total_tokens: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    successful_requests: int = 0
    total_cost: float = 0.0

    def __init__(self) -> None:
        super().__init__()
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
        try:
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
            response_metadata = response_metadata or {}  # Ensure response_metadata is a dictionary
            if response_model_name := response_metadata.get("model"):
                model_name = response_model_name
            elif response.llm_output is None:
                model_name = ""
            else:
                model_name = response.llm_output.get("model", "")
                

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
            model_name = response.llm_output.get("model_name", "")

        if model_name in MODEL_COST_PER_1K_INPUT_TOKENS:
            total_cost = _get_anthropic_claude_token_cost(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                model_id=model_name,
            )

        # update shared state behind lock
        with self._lock:
            self.total_cost += total_cost
            self.total_tokens += token_usage.get("total_tokens", 0)
            self.prompt_tokens += prompt_tokens
            self.completion_tokens += completion_tokens
            self.successful_requests += 1

    def __copy__(self) -> "AnthropicTokenUsageCallbackSync":
        """Return a copy of the callback handler."""
        return self

    def __deepcopy__(self, memo: Any) -> "AnthropicTokenUsageCallbackSync":
        """Return a deep copy of the callback handler."""
        return self