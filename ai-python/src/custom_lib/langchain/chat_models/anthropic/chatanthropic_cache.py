from __future__ import annotations

import gc
import logging
import os
import sys
import warnings
from typing import (
    TYPE_CHECKING,
    Any,
    AsyncIterator,
    Callable,
    Dict,
    Iterator,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Type,
    Union,
)

from langchain_anthropic.chat_models import ChatAnthropic,_format_messages,convert_to_anthropic_tool
from langchain_core.messages import BaseMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
import tiktoken as tiktoken_
from src.custom_lib.langchain.tiktoken_load.encoding_cache import get_cached_encoding
if TYPE_CHECKING:
    import tiktoken

class MyChatAnthropic(ChatAnthropic):
    def get_num_tokens_from_messages(
        self,
        messages: list[BaseMessage],
        tools: Optional[
            Sequence[Union[dict[str, Any], type, Callable, BaseTool]]
        ] = None,
        **kwargs: Any,
    ) -> int:
        """Count tokens in a sequence of input messages.

        Args:
            messages: The message inputs to tokenize.
            tools: If provided, sequence of dict, BaseModel, function, or BaseTools
                to be converted to tool schemas.

        Basic usage:
            .. code-block:: python

                from langchain_anthropic import ChatAnthropic
                from langchain_core.messages import HumanMessage, SystemMessage

                llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")

                messages = [
                    SystemMessage(content="You are a scientist"),
                    HumanMessage(content="Hello, Claude"),
                ]
                llm.get_num_tokens_from_messages(messages)

            .. code-block:: none

                14

        Pass tool schemas:
            .. code-block:: python

                from langchain_anthropic import ChatAnthropic
                from langchain_core.messages import HumanMessage
                from langchain_core.tools import tool

                llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")

                @tool(parse_docstring=True)
                def get_weather(location: str) -> str:
                    \"\"\"Get the current weather in a given location

                    Args:
                        location: The city and state, e.g. San Francisco, CA
                    \"\"\"
                    return "Sunny"

                messages = [
                    HumanMessage(content="What's the weather like in San Francisco?"),
                ]
                llm.get_num_tokens_from_messages(messages, tools=[get_weather])

            .. code-block:: none

                403

        .. versionchanged:: 0.3.0

                Uses Anthropic's token counting API to count tokens in messages. See:
                https://docs.anthropic.com/en/docs/build-with-claude/token-counting
        """
        formatted_system, formatted_messages = _format_messages(messages)
        if isinstance(formatted_system, str):
            kwargs["system"] = formatted_system
        if tools:
            kwargs["tools"] = [convert_to_anthropic_tool(tool) for tool in tools]

        model = 'gpt-4o'

        # Get encoding using the global cache.
        encoding = get_cached_encoding(model)

        # Set token count parameters based on the model.
        if model.startswith("gpt-3.5-turbo-0301"):
            tokens_per_message = 4
            tokens_per_name = -1
        elif model.startswith("gpt-3.5-turbo") or model.startswith("gpt-4"):
            tokens_per_message = 3
            tokens_per_name = 1
        else:
            raise NotImplementedError(
                f"get_num_tokens_from_messages() is not implemented for model {model}. "
                "See https://github.com/openai/openai-python/blob/main/chatml.md for details."
            )

        # Calculate the total number of tokens.
        num_tokens = 0
        for message in formatted_messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                # Cast value to str in case it's not a string.
                num_tokens += len(encoding.encode(str(value)))
                if key == "name":
                    num_tokens += tokens_per_name
        try:
            del encoding
            gc.collect()
        except Exception as e:
            pass
        return num_tokens