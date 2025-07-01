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

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_core.runnables import Runnable
from langchain_core.tools import BaseTool
from langchain_community.adapters.openai import convert_message_to_dict

import tiktoken as tiktoken_
from src.custom_lib.langchain.tiktoken_load.encoding_cache import get_cached_encoding
if TYPE_CHECKING:
    import tiktoken

class MyChatOpenAI(ChatOpenAI):
    def get_num_tokens_from_messages(
        self,
        messages: List[BaseMessage],
        tools: Optional[
            Sequence[Union[Dict[str, Any], Type, Callable, BaseTool]]
        ] = None,
    ) -> int:
        if tools is not None:
            warnings.warn(
                "Counting tokens in tool schemas is not yet supported. Ignoring tools."
            )
        if sys.version_info[1] <= 7:
            return super().get_num_tokens_from_messages(messages)
        
        # Determine the model to use.
        if self.tiktoken_model_name is not None:
            model = self.tiktoken_model_name
        else:
            model = self.model_name
            if model == "gpt-3.5-turbo":
                model = "gpt-3.5-turbo-0301"
            elif model == "gpt-4":
                model = "gpt-4-0314"
            elif model == "chatgpt-4o-latest":
                model="gpt-4o"
            elif model == "o4-mini":
                model="gpt-4o"
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
        messages_dict = [convert_message_to_dict(m) for m in messages]
        for message in messages_dict:
            num_tokens += tokens_per_message
            for key, value in message.items():
                # Cast value to str in case it's not a string.
                num_tokens += len(encoding.encode(str(value)))
                if key == "name":
                    num_tokens += tokens_per_name
        # Account for the priming of every reply.
        try:
            del encoding
            gc.collect()
        except Exception as e:
            pass
        return num_tokens
        
