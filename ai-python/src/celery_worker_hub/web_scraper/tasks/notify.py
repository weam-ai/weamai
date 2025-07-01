from fastapi import HTTPException,status
from src.Firebase.firebase import firebase
from src.celery_worker_hub.web_scraper.celery_app import celery_app
from src.logger.default_logger import logger
from src.celery_worker_hub.web_scraper.utils.prompt_notification import add_notification_data
from src.Emailsend.email_service import EmailService
from src.celery_worker_hub.web_scraper.config import MailConfig
from src.crypto_hub.utils.encode_decode import encode_object



@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 1, 'countdown': 0},
    queue="scrapsite"
)
def on_task_success(self,message,data:dict):
    try:
        firebase.send_push_notification(data['token'], data["title"], data["body"])
        add_notification_data(data["title"],data["user_data"],"notificationList")
        email_service = EmailService()
        email_service.send_email(
            email=data.get('user_data', {}).get('email'),
            subject=MailConfig.SUCCESS_MAIL_SUBJECT,
            username=data.get('user_data', {}).get('fname'),
            content_body=MailConfig.SUCCESS_MAIL_BODY,
            slug=encode_object(data["brain_id"]),
            template_name="success-mail",
            url_type="prompts"
        )

        logger.info(f"🎉✅ on_task_success executed for task with title: {data['title']}", extra={"tags": {"method": "ScrapUrlService.on_task_success"}})

    except Exception as e:
        logger.error(f"Failed to send success notification: {e}", extra={"tags": {"method": "ScrapUrlService.on_task_success"}})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to send success notification: {e}")


@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 2, 'countdown': 0},
    queue="scrapsite"
)
def on_task_failed(self,message,data:dict, *args,**kwargs):
    try:
     
        firebase.send_push_notification(data['token'], data["title"], data["body"])
        add_notification_data(data["title"],data["user_data"],"notificationList")

        # email_service.send_email(
        #     email=data.get('user_data', {}).get('email'),
        #     subject=MailConfig.FAILURE_MAIL_SUBJECT,
        #     username=data.get('user_data', {}).get('fname'),
        #     content_body=MailConfig.FAILURE_MAIL_BODY,
        #     slug=encode_object(data["brain_id"]),
        #     template_name="failure-mail"
        # )
   
        logger.info(f"🎉❌ on_task_failed task executed successfully for task with title: {data['title']}", extra={"tags": {"method": "ScrapUrlService.on_task_failed"}})
    except Exception as e:
        logger.error(f"Failed to send failure notification: {e}", extra={"tags": {"method": "ScrapUrlService.on_task_failed"}})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Failed to send failure notification: {e}")