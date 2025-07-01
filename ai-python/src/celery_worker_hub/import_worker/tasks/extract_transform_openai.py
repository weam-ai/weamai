import hashlib
from src.celery_worker_hub.import_worker.celery_app import celery_app
from src.custom_lib.langchain.chat_models.openai.chatopenai_cache import MyChatOpenAI as ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.callbacks.manager import get_openai_callback
from src.crypto_hub.utils.crypto_utils import MessageEncryptor
from dotenv import load_dotenv
from bson import ObjectId
from src.celery_worker_hub.import_worker.utils import ConversationSummaryMemory
from src.celery_worker_hub.import_worker.tasks.config import SUM_MEMORY_LIMIT
import json
from src.db.config import db_instance
import os
from src.celery_worker_hub.import_worker.utils import convert_to_ist
from fastapi import HTTPException, status
from src.logger.default_logger import logger
from datetime import datetime
from src.chatflow_langchain.service.config.model_config_openai import OPENAIMODEL
import pytz
load_dotenv()
import tiktoken

security_key = os.getenv("SECURITY_KEY").encode("utf-8")
@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 0, 'countdown': 0},
    queue="extract_and_transform_openai"
)
def extract_and_transform_openai(self,config, conversation, chat_id, import_id,current_user,api_key,model_id):
        """Process and transform chat data into MongoDB document format."""
        document = []
        max_summary_token=0
        total_imported_tokens = 0
        total_prompt_tokens = 0
        total_completion_tokens = 0
        total_summary_completion=0
        total_summary_prompt=0
        total_summary_tokens=0
        count = 0
        conversation_id = conversation.get("id")  # Get conversation ID
        if current_user.get("profile", {}).get("id") is not None:                       
            current_user['profile']['id'] = ObjectId(current_user['profile']['id']) 
            
        llm = ChatOpenAI(api_key=api_key, model=OPENAIMODEL.GPT_4_1_MINI, temperature=0.7,max_tokens=1000,use_responses_api=True)
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
        encryptor = MessageEncryptor(security_key)

        # Filter out invalid mappings and sort by create_time (oldest to newest)
        filtered_sorted_mappings = sorted(
            [
                value for value in conversation.get("mapping", {}).values()
                if value
                and isinstance(value, dict)
                and value.get("message")
                and isinstance(value["message"], dict)
                and value["message"].get("create_time") is not None
                and value["message"].get("content", {}).get("parts")  # Ensure content_parts exists and is not null
                and any(
                    isinstance(part, str) and part.strip()  # Ensure part is a string and not empty or whitespace
                    for part in value["message"]["content"].get("parts", [])
                )
            ],
            key=lambda x: x["message"]["create_time"]
        )

        current_user_message = None
        assistant_message = None
        create_time = None
        new_sumhistory_checkpoint=None

        # Process each message in the conversation
        for mapping in filtered_sorted_mappings:
            message = mapping["message"]
            metadata = message.get("metadata", {})
            msg_id = message.get("id", {})
            author_role = message.get("author", {}).get("role")
            content_parts = message["content"]["parts"]
            create_time = int(float(message["create_time"]))
            created_time = convert_to_ist(create_time)
            update_time = message.get("create_time")
            updated_time = convert_to_ist(update_time)
            model_slug = metadata.get("model_slug")


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

            # Initialize response_model with a default value
            response_model = None
            if model_slug != "auto":
                response_model = model_slug

            # Process user and assistant messages
            if author_role == "user":
                # Store user message temporarily to pair with the assistant response
                current_user_message = " ".join(
                    [
                        part.get("text", "").strip() if isinstance(part, dict) else str(part).strip()
                        for part in content_parts
                        if (isinstance(part, str) and part.strip()) or (isinstance(part, dict) and part.get("text", "").strip())
                    ]
                )
                tokens["promptT"] += len(encoding.encode(current_user_message))
                total_prompt_tokens += tokens['promptT']
                max_summary_token+=tokens['promptT']

            elif author_role == "assistant" and current_user_message:
                # Pair the assistant response with the previous user message
                assistant_message = " ".join(
                    [
                        part.get("text", "").strip() if isinstance(part, dict) else str(part).strip()
                        for part in content_parts
                        if isinstance(part, (str, dict)) and (part.strip() if isinstance(part, str) else part.get("text", "").strip())
                    ]
                )
                tokens["completion"] += len(encoding.encode(assistant_message))
                total_completion_tokens +=tokens['completion']
                max_summary_token+=tokens['completion']

                # Save both user query and assistant response in a single document
                tokens["totalUsed"] = tokens["promptT"] + tokens["completion"]
                total_imported_tokens += tokens["totalUsed"]
                tokens["totalCost"] = f"${tokens['totalUsed'] * 0.00001:.6f}"    
                


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
                    with get_openai_callback() as cb:
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
                    "message": encryptor.encrypt(json.dumps({
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
                        "title": "Open AI",
                        "code": "OPEN_AI",
                        "id": ObjectId(model_id)
                    },
                    "brain": {
                        "title": config["brain_title"],
                        "slug": config["brain_slug"],
                        "id": ObjectId(config["brain_id"])
                    },
                    "isActive": True,
                    "responseModel": response_model,
                    "responseAPI": "OPEN_AI",
                    "media": None,
                    "cloneMedia": None,
                    "companyId":ObjectId(config['company_id']),
                    "reaction": [],
                    "seq":seq_current_datetime,
                    "createdAt": created_time,
                    "updatedAt": updated_time,
                    "__v": {"$numberInt": "0"},
                    "isMedia": False,
                    "ai": encryptor.encrypt(json.dumps({
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
                    "system": encryptor.encrypt(json.dumps({
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
                    f"Error executing Extract And transform Task OpenAI: {e}",
                    extra={"tags": {"task_function": "extract_and_transform_openai"}}
                )
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


        collection = db_instance.get_collection('messages')
        try:
            if document:
                        # Ensure document is a list and contains valid entries
                        if isinstance(document, list) and len(document) > 0:
                            responseAPI = document[0].get('responseAPI')
                            if responseAPI:
                                logger.info(f"Response API: {responseAPI}")
                            else:
                                logger.warning("Warning: 'responseAPI' not found in document.")
                            
                            # print(f"Inserting {len(document)} documents into MongoDB.")
                            collection.insert_many(document)
                        else:
                            logger.warning("Warning: Document is not a valid list or is empty.")
            else:
                logger.warning("Warning: No document returned.")
        except Exception as e:
            logger.error(
                f"Error executing Extract And transform Task OpenAI: {e}",
                extra={"tags": {"task_function": "extract_and_transform_openai"}}
            )
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

        return [{"task_id":self.request.id,"imported_tokens":total_import_tokens,"chat_id":chat_id,"imported_prompt_tokens":total_prompt_tokens,"imported_completion_tokens":total_completion_tokens,"summary_total_tokens":total_summary_tokens,"summary_prompt_tokens":total_summary_prompt,"summary_completion_tokens":total_summary_completion}]