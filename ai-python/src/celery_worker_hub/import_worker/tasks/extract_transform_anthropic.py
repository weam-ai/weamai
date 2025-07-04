from src.celery_worker_hub.import_worker.celery_app import celery_app
from langchain_core.prompts import PromptTemplate
from langchain_community.callbacks.manager import get_bedrock_anthropic_callback
from src.crypto_hub.utils.crypto_utils import crypto_service
from src.custom_lib.langchain.chat_models.anthropic.chatanthropic_cache import MyChatAnthropic as ChatAnthropic
from dotenv import load_dotenv
from bson import ObjectId
from src.celery_worker_hub.import_worker.utils import ConversationSummaryMemory
from src.celery_worker_hub.import_worker.tasks.config import SUM_MEMORY_LIMIT
from src.chatflow_langchain.service.config.model_config_anthropic import ANTHROPICMODEL
import json
from src.db.config import db_instance
import os 
import hashlib
from src.celery_worker_hub.import_worker.utils import convert_to_ist
from fastapi import HTTPException, status
from src.logger.default_logger import logger
import tiktoken
from datetime import datetime
import pytz


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 0, 'countdown': 0},
    queue="extract_and_transform_anthropic"
)
def extract_and_transform_anthropic(self,config, conversation, chat_id, import_id,current_user,api_key,model_id):
        """Process and transform chat data into MongoDB document format."""
        document = []
        total_imported_tokens = 0
        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_summary_completion=0
        total_summary_prompt=0
        total_summary_tokens=0
        conversation_id = conversation.get("id")  # Get conversation ID
        max_summary_token=0
        if current_user.get("profile", {}).get("id") is not None:                   
            current_user['profile']['id'] = ObjectId(current_user['profile']['id'])  
        llm = ChatAnthropic(api_key=api_key, model=ANTHROPICMODEL.CLAUDE_HAIKU_3_5, temperature=0.7,max_tokens=1000)
        encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        timezone = pytz.timezone("Asia/Kolkata")  # Adjust timezone if needed
        SUMMARY_PROMPT = PromptTemplate(
            input_variables=["summary", "new_lines"],
            template=(
                "Summarize and new line the conversation below, focusing on key points, user intents, and assistant responses, "
                "and ensure a coherent narrative. Make the best possible summary of the conversation. Don't lose the main context of the conversation. "
                "Please summarize the conversation between 700 to 1000 tokens."
                "Updated Summary:\n\n"
                "Current Summary:\n{summary}\n\n"
                "New Lines:\n{new_lines}\n\n"
                "Updated Summary:"
            )
        )
        memory = ConversationSummaryMemory(llm=llm, max_token_limit=SUM_MEMORY_LIMIT.MAX_TOKEN_LIMIT, memory_key="summary", prompt=SUMMARY_PROMPT)

        chat_messages = conversation["chat_messages"]

        # Filter out invalid mappings and sort by create_time (oldest to newest)
        filtered_sorted_messages = sorted(
            [
                msg for msg in chat_messages
                if msg
                and isinstance(msg, dict)
                and msg.get("content")
                and any(
                    part.get("text", "").strip() for part in msg.get("content", [])
                    if part.get("type") == "text"
                )
            ],
            key=lambda x: x["created_at"]
        )

        current_user_message = None
        assistant_message = None
        create_time = None
        new_sumhistory_checkpoint=None
     
        tokens = {
            "imageT": 0,
            "promptT": 0,
            "completion": 0,
            "totalUsed": 0,
            "totalCost": "$0.0",
            "summary": {
                "promptT": 0,
                "completion": 0,
                "totalUsed": 0,
                "totalCost": "$0.0"
            }
        }

        for message in filtered_sorted_messages:
            sender = message["sender"]
            content_parts = message["content"]
            msg_text = " ".join(
                [
                    part.get("text", "").strip() if isinstance(part, dict) else str(part).strip()
                    for part in content_parts
                    if (isinstance(part, str) and part.strip()) or (isinstance(part, dict) and part.get("text", "").strip())
                ]
            )
            # model = "gpt-4.1-mini"  # Example model, adjust accordingly
            # Get cost for the model based on the number of tokens

            createTime = datetime.strptime(message["created_at"][:-1], "%Y-%m-%dT%H:%M:%S.%f")
            UpdateTime = datetime.strptime(message["updated_at"][:-1], "%Y-%m-%dT%H:%M:%S.%f")
            created_time = convert_to_ist(createTime.timestamp())
            updated_time = convert_to_ist(UpdateTime.timestamp())

            if sender == "human":
                current_user_message = msg_text
                tokens["promptT"] += len(encoding.encode(current_user_message))
                total_prompt_tokens += tokens['promptT']
                max_summary_token+=tokens['promptT']

            elif sender == "assistant" and current_user_message:
                assistant_message = msg_text
                tokens["completion"] += len(encoding.encode(assistant_message))

                max_summary_token+=tokens['completion']
                tokens["totalUsed"] = tokens["promptT"] + tokens["completion"]

                total_imported_tokens += tokens["totalUsed"]
                # Calculate the total cost for all tokens used
                tokens["totalCost"] = f"${tokens['totalUsed'] * 0.00001:.6f}"
                total_completion_tokens +=tokens['completion']
                summarized_history = ''


                # Check if total tokens used is less than 10000
                if max_summary_token < SUM_MEMORY_LIMIT.MAX_TOKEN_LIMIT:
                    # If tokens used are less than 10000, hash the chat_id
                    memory.save_context({"input": current_user_message}, {"output": assistant_message})
                    if new_sumhistory_checkpoint:
                       sumhistory_checkpoint = new_sumhistory_checkpoint
                       summarized_history = new_sumhistory
                    else:
                        sumhistory_checkpoint = hashlib.sha256(str(chat_id).encode("utf-8")).hexdigest()
                    
                else:
                    # If tokens used are 10000 or more, create the summarized history
                    with get_bedrock_anthropic_callback() as cb:
                        memory.save_context({"input": current_user_message}, {"output": assistant_message})
                        memory.trigger_summary()
                        summarized_history = memory.load_memory_variables({"input": current_user_message, "output": assistant_message}).get("summary", "")

                        # Extract and store the values separately
                       
                        tokens["summary"]["totalUsed"] = cb.total_tokens
                        tokens["summary"]["promptT"] = cb.prompt_tokens
                        tokens["summary"]["completion"] = cb.completion_tokens
                        tokens["summary"]["totalCost"] = f"${cb.total_cost}"
                        total_summary_tokens += tokens["summary"]["totalUsed"]
                        total_summary_prompt += tokens["summary"]["promptT"]
                        total_summary_completion += tokens["summary"]["completion"]
                        # If summarized_history exists, calculate its token usage and cost
                        summarized_history_tokens = len(encoding.encode(summarized_history))
                        max_summary_token=summarized_history_tokens


                        new_sumhistory_checkpoint = hashlib.sha256(summarized_history.encode("utf-8")).hexdigest()
                        sumhistory_checkpoint = new_sumhistory_checkpoint
                        new_sumhistory = summarized_history
                            

                # Create a new document for the conversation pair
                
                seq_current_datetime = datetime.now(timezone)
                document.append({
                    "_id": ObjectId(),
                    "message": crypto_service.encrypt(json.dumps({
                        "type": "human",
                        "data": {
                            "content": current_user_message,
                            "additional_kwargs": {},
                            "response_metadata": {},
                            "type": "human",
                            "name": None,
                            "id": None,
                            "example": False,
                            "tool_calls": [],
                            "invalid_tool_calls": []
                        }
                    })),
                    "chatId": ObjectId(chat_id),
                    "chat_session_id": ObjectId(chat_id),
                    "importId": ObjectId(import_id),
                    "threadIds": [],
                    "tokens": tokens,
                    "model": {
                        "title": "Anthropic",
                        "code": "ANTHROPIC",
                        "id": ObjectId(model_id)
                    },
                    "brain": {
                        "title": config["brain_title"],
                        "slug": config["brain_slug"],
                        "id": ObjectId(config["brain_id"])
                    },
                    "isActive": True,
                    "responseModel": "claude-3-5-sonnet-latest",
                    "responseAPI": "ANTHROPIC",
                    "media": None,
                    "cloneMedia": None,
                    "seq": seq_current_datetime,
                    "reaction": [],
                    "createdAt": created_time,
                    "updatedAt": updated_time,
                    "__v": {"$numberInt": "0"},
                    "isMedia": False,
                    "ai": crypto_service.encrypt(json.dumps({
                        "type": "ai",
                        "data": {
                            "content": assistant_message,
                            "additional_kwargs": {},
                            "response_metadata": {},
                            "type": "ai",
                            "name": None,
                            "id": None,
                            "example": False,
                            "tool_calls": [],
                            "invalid_tool_calls": [],
                            "usage_metadata": None
                        }
                    })),
                    "sumhistory_checkpoint": str(sumhistory_checkpoint),
                    "system": crypto_service.encrypt(json.dumps({
                        "type": "system",
                        "data": {
                            "content": summarized_history,
                            "additional_kwargs": {},
                            "response_metadata": {},
                            "type": "system",
                            "name": None,
                            "id": None
                        }
                    })),
                    "user": {
                        "email": current_user["email"],
                        **({"fname": current_user["fname"]} if "fname" in current_user else {}),
                        **({"lname": current_user["lname"]} if "lname" in current_user else {}),
                        **({"profile": current_user["profile"]} if "profile" in current_user else {}),
                        "id": ObjectId(config["user_id"]),
                    },
                })

                # Reset user message for the next conversation pair
                current_user_message = None

            try:
                if total_imported_tokens != 0:
                    total_import_tokens = total_imported_tokens
                else:
                    total_import_tokens = 0
            except Exception as e:
                logger.error(
                    f"Error executing Extract And transform Task Anthropic: {e}",
                    extra={"tags": {"task_function": "extract_and_transform_anthropic"}}
                )
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))



        collection = db_instance.get_collection('messages')
        try:
            if document:
                        # Ensure document is a list and contains valid entries
                        if isinstance(document, list) and len(document) > 0:
                            collection.insert_many(document)
                        else:
                            logger.info("Warning: Document is not a valid list or is empty.")
            else:
                print("Warning: No document returned.")
        except Exception as e:
            logger.error(
                f"Error executing Extract And transform Task Anthropic: {e}",
                extra={"tags": {"task_function": "extract_and_transform_anthropic"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        return [{"task_id":self.request.id,"imported_tokens":total_import_tokens,"chat_id":chat_id,"imported_prompt_tokens":total_prompt_tokens,"imported_completion_tokens":total_completion_tokens,"summary_total_tokens":total_summary_tokens,"summary_prompt_tokens":total_summary_prompt,"summary_completion_tokens":total_summary_completion}]