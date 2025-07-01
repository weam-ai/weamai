from src.celery_worker_hub.import_worker.utils import get_task_statuses
from src.celery_worker_hub.import_worker.celery_app import celery_app
from bson import ObjectId
from src.db.config import db_instance
from pymongo import UpdateOne,UpdateMany
from dotenv import load_dotenv
from src.Emailsend.email_service import EmailService
from src.celery_worker_hub.import_worker.config import ImportChatConfig
from fastapi import HTTPException, status
from src.logger.default_logger import logger
from src.celery_worker_hub.import_worker.utils import delete_failed_records
from src.db.config import db_instance
from langchain_community.callbacks.openai_info import get_openai_token_cost_for_model
from src.custom_lib.langchain.callbacks.anthropic.cost.cost_calc_handler import _get_anthropic_claude_token_cost
from src.Firebase.firebase import firebase
from src.celery_worker_hub.web_scraper.utils.prompt_notification import add_notification_data
from src.celery_worker_hub.import_worker.tasks.config import ImportChatConfig
from src.crypto_hub.utils.encode_decode import encode_object
load_dotenv()



@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 0, 'countdown': 0},
    queue="bulk_update_task"
)
def bulk_update_task(self,results,config, import_id,bulk_updates):
    try:
        chat_collection = db_instance.get_collection('chat')
        chat_member_collection = db_instance.get_collection('chatmember')

        task_id_chat_id_mapper = {result["task_id"]: result["chat_id"] for result in results}
        task_id_list = list(task_id_chat_id_mapper.keys())
        
        
        total_prompt_tokens = sum(result['imported_prompt_tokens'] for result in results)
        total_completion_tokens = sum(result['imported_completion_tokens'] for result in results)
        total_import_tokens = total_completion_tokens+total_prompt_tokens
        total_summary_tokens = sum(result['summary_total_tokens'] for result in results)
        total_summary_prompt = sum(result['summary_prompt_tokens'] for result in results)
        total_summary_completion = sum(result['summary_completion_tokens'] for result in results)
        status_dict=get_task_statuses(task_id_list)
        bulk_updates_task = []
        bulk_chat_task = []
        bulk_chat_member = []
        sucess_count=0
        failed_chat_ids = []
        for task,task_id in zip(bulk_updates,task_id_list):
            chat_id = task_id_chat_id_mapper.get(task_id)
            if status_dict.get(task_id)=="SUCCESS":
                sucess_count+=1
                # Ensure the taskstatus is pushed correctly
                task["$set"][f"conversationData.{chat_id}"].update({'taskIds':task_id})
                task["$set"][f'conversationData.{chat_id}'].update({"taskstatus":status_dict.get(task_id,"Failed")})

                # Ensure the ObjectId is correctly assigned 
                filter_id = {"_id":ObjectId(import_id)}
                filter_chat_id = {"_id":ObjectId(chat_id)}
                filter_chatMember_id = {"chatId":ObjectId(chat_id)}
                chat_task ={
                    "$set": {
                        "isNewChat":False
                    }
                }

                bulk_updates_task.append(UpdateOne(filter_id,task,upsert=False)
                )  
                bulk_chat_task.append(UpdateOne(filter_chat_id,chat_task,upsert=False))
                bulk_chat_member.append(UpdateMany(filter_chatMember_id,chat_task,upsert=False))
            else:
                if chat_id:
                    failed_chat_ids.append(chat_id)

        # Perform bulk update only for successful tasks
        if bulk_updates_task or bulk_chat_task or bulk_chat_member:
            importChat_collection = db_instance.get_collection("importChat")
            importChat_collection.bulk_write(bulk_updates_task)
            chat_collection.bulk_write(bulk_chat_task)
            chat_member_collection.bulk_write(bulk_chat_member)
            importChat_collection.update_one(
                    {"_id": ObjectId(import_id)}, 
                    {"$inc": {"successImportedChat": sucess_count,"totalImportedTokens": total_import_tokens,"totalImportedPrompt":total_prompt_tokens,"totalImportedCompletion":total_completion_tokens,"totalSummaryTokens":total_summary_tokens,"totalSummaryPrompt":total_summary_prompt,"totalSummaryCompletion":total_summary_completion}}
                )
            logger.info("Bulk write operations completed successfully for import ID: %s", import_id)
            
        if failed_chat_ids:
            delete_failed_records(import_id,failed_chat_ids)
            
    except Exception as e:
        logger.error(
            f"Error executing while Bulk updating: {e}",
            extra={"tags": {"task_function": "bulk_update_task"}}
        )
        raise HTTPException(status_code=400, detail=str(e))




@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 1, 'countdown': 0},
    queue="bulk_update_task"
)
def on_task_success(self, data: dict, user_data: dict):  # Make sure to accept `self` and `data` explicitly
    try:
        cost_task=final_cost_calculate.s(data=data,user_data=user_data).apply_async()
    except Exception as e:
        logger.error(f"Failed to send success notification: {e}", extra={"tags": {"method": "ImportChat.on_task_success"}})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to send success email: {e}")
    
@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 1, 'countdown': 0},
    queue="bulk_update_task"
)
def final_cost_calculate(self, data: dict, user_data: dict):  # Make sure to accept `self` and `data` explicitly
    """
    Task to calculate the final cost based on OpenAI token usage and update the database.
    Args:
        self: The task instance (automatically passed by Celery).
        data (dict): A dictionary containing the import ID.
    Raises:
        HTTPException: If there is an error during the process, an HTTPException is raised with status code 400.
    The task performs the following steps:
    1. Retrieves the import chat data from the database using the provided import ID.
    2. Calculates the completion cost and prompt cost using the OpenAI token cost model.
    3. Computes the total cost by summing the completion and prompt costs.
    4. Updates the import chat collection with the calculated total cost.
    5. Logs a success message upon successful completion.
    6. Logs an error message and raises an HTTPException if any exception occurs during the process.
    """
    try:
        
        import_chat_collection=db_instance.get_collection("importChat")
        import_chat_data=import_chat_collection.find_one({"_id":ObjectId(data['import_id'])},{"totalSummaryCompletion":1,"totalSummaryPrompt":1,"responseAPI":1, "successImportedChat": 1,"conversationData":1, "totalImportChat": 1})
        
        conversationData = import_chat_data['conversationData']
        success_count = len(conversationData)
        total_count = import_chat_data.get('totalImportChat')

        content_body = {
            "source": data.get('source'),
            "total_count": total_count,
            "success_count": success_count
        }
        email_service = EmailService()
        email_service.send_email(
            email=data.get('email'),
            subject=ImportChatConfig.SUCCESS_TITLE,
            username=data.get('username'),
            content_body=content_body,
            slug=encode_object(data.get("brain_id")),
            template_name="import-chat-success-mail",
            url_type="chat"
        )
        logger.info(f"🎉✅ Send mail executed for task with title: {ImportChatConfig.SUCCESS_TITLE}", extra={"tags": {"method": "ImportChatJson.final_cost_calculate"}})

        fcm_tokens = user_data.get('fcmtokens', [])
        if fcm_tokens:
            logger.info("Sending push notification.", extra={"tags": {"method": "ImportChat.final_cost_calculate"}})
            firebase.send_push_notification(
                fcm_tokens,
                ImportChatConfig.SUCCESS_TITLE,
                ImportChatConfig.SUCCESS_BODY.format(
                    source=data['source'], count=success_count, brain_name=data['brain_name']
                )
            )
            add_notification_data(ImportChatConfig.SUCCESS_TITLE, user_data, "notificationList")
            logger.info(f"🎉🔔✅ Send notification successfully: {ImportChatConfig.SUCCESS_TITLE}",
                extra={"tags": {"method": "ImportChat.final_cost_calculate"}})
        else:
            add_notification_data(ImportChatConfig.SUCCESS_TITLE, user_data, "notificationList")
            logger.info("❌🚫 No FCM tokens available. Skipping push notification.", extra={"tags": {"method": "ImportChat.final_cost_calculate"}})

        if import_chat_data['responseAPI']=="OPENAI":
            completion_cost = get_openai_token_cost_for_model(
                    "gpt-4.1-mini", import_chat_data['totalSummaryCompletion'], is_completion=True
                )
            prompt_cost = get_openai_token_cost_for_model("gpt-4.1-mini", import_chat_data['totalSummaryPrompt'])
            total_cost=completion_cost+prompt_cost
        else:
            total_cost=_get_anthropic_claude_token_cost(prompt_tokens=import_chat_data['totalSummaryPrompt'],completion_tokens=import_chat_data['totalSummaryCompletion'],model_id="claude-3-5-sonnet-latest")

           

        import_chat_collection.update_one({"_id":ObjectId(data['import_id'])},{"$set":{"totalSummaryCost":f"${total_cost}","successImportedChat":success_count}})
            
        logger.info(f"Task executed successfully: {ImportChatConfig.SUCCESS_TITLE}",
            extra={"tags": {"method": "ImportChat.final_cost_calculate"}})

    except Exception as e:
        logger.error(f"Failed to send success notification: {e}", extra={"tags": {"method": "ImportChat.final_cost_calculate"}})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to send success email: {e}")
    

