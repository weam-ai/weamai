import os
import boto3
from botocore.exceptions import ClientError
from fastapi import HTTPException, status
from dotenv import load_dotenv
from src.logger.default_logger import logger
from jinja2 import Environment, FileSystemLoader
import smtplib
from src.db.config import  db_instance
from email.message import EmailMessage
from abc import ABC, abstractmethod
from src.crypto_hub.utils.crypto_utils import MessageEncryptor,MessageDecryptor
load_dotenv()

key = os.getenv("SECURITY_KEY").encode("utf-8")
encryptor = MessageEncryptor(key)
decryptor = MessageDecryptor(key)
# ---------- Mongo Helper ----------

class BaseEmailProvider(ABC):
    @abstractmethod
    def send_email(self, email: str, subject: str, username: str, content_body: str, slug: str, template_name: str, show_button: bool = True, url_type: str = "prompts"):
        pass

class SESEmailService(BaseEmailProvider):
    def __init__(self, config = None):
        self.ses_client = boto3.client(
            'ses',
            region_name=os.environ.get("AWS_REGION"),
            aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY")
        )
        self.verified_email = os.environ.get("SENDER_EMAIL")
        self.environment_url = os.environ.get("ENVIRONMENT_URL")
        template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Emailsend/templates'))
        self.load_template = Environment(loader=FileSystemLoader(template_dir))

    def send_email(self, email: str, subject: str, username: str, content_body: str, slug: str, template_name: str,show_button: bool = True, url_type: str = "prompts"):
        try:
            template_html = self.load_template.get_template(f'{template_name}.html')
            html_content = template_html.render(
                username=username,
                content_body=content_body,
                url=f"{self.environment_url}/{url_type}?b={slug}",
                show_button=show_button
            )
            logger.info(f"Email template '{template_name}.html' rendered successfully.")
        except FileNotFoundError:
            logger.error(f"Email template '{template_name}' not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email template not found")

        logger.info(f"Preparing to send email to: {email}")
        return self._send_email_via_ses(email, subject, html_content)

    def _send_email_via_ses(self, email: str, subject: str, html_content: str):
        try:
            response = self.ses_client.send_email(
                Source=self.verified_email,
                Destination={
                    'ToAddresses': [email]
                },
                Message={
                    'Subject': {
                        'Data': subject,
                        'Charset': 'UTF-8'
                    },
                    'Body': {
                        'Html': {
                            'Data': html_content,
                            'Charset': 'UTF-8'
                        }
                    }
                }
            )
            logger.info(f"✅ Email successfully sent to {email}. Response: {response}")
            return response
        except ClientError as e:
            error_message = e.response['Error']['Message']
            logger.error(f"ClientError: {error_message}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_message)
        except Exception as e:
            logger.error(f"❌ Failed to send email to {email}. Error: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))





class SMTPEmailService(BaseEmailProvider):
    def __init__(self,config = None):
        self.smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.environ.get("SMTP_PORT", 587))
        self.smtp_user = os.environ.get("SMTP_USER", "your_email@gmail.com")
        self.smtp_password = os.environ.get("SMTP_PASSWORD", "your_password")
        self.from_email = self.smtp_user
        self.environment_url = os.environ.get("ENVIRONMENT_URL", "http://localhost:8000")

        template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Emailsend/templates'))
        self.load_template = Environment(loader=FileSystemLoader(template_dir))

    def send_email(self, email: str, subject: str, username: str, content_body: str, slug: str, template_name: str, show_button: bool = True, url_type: str = "prompts"):
        try:
            template_html = self.load_template.get_template(f'{template_name}.html')
            html_content = template_html.render(
                username=username,
                content_body=content_body,
                url=f"{self.environment_url}/{url_type}?b={slug}",
                show_button=show_button
            )
            logger.info(f"Email template '{template_name}.html' rendered successfully.")
        except FileNotFoundError:
            logger.error(f"Email template '{template_name}' not found.")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email template not found")

        logger.info(f"Preparing to send email to: {email}")
        return self._send_email_via_smtp(email, subject, html_content)

    def _send_email_via_smtp(self, to_email: str, subject: str, html_content: str):
        try:
            msg = EmailMessage()
            msg["Subject"] = subject
            msg["From"] = self.from_email
            msg["To"] = to_email
            msg.set_content("This is an HTML email. Please view it in an HTML-compatible email viewer.")
            msg.add_alternative(html_content, subtype='html')
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
                logger.info(f"✅ Email successfully sent to {to_email}")
                return {"message": "Email sent successfully"}
        except smtplib.SMTPException as e:
            logger.error(f"SMTPException: {e}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to send email")
        except Exception as e:
            logger.error(f"❌ Failed to send email to {to_email}. Error: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
        




# ---------- Email Service ----------
class EmailService:
    def __init__(self):
        provider_name = os.environ.get("EMAIL_PROVIDER", "SES")
        self.initialization = True

        providers = {
            "SES": SESEmailService,
            "SMTP": SMTPEmailService,
            # future: "SENDGRID": SendGridProviders
        }

        if provider_name not in providers:
            logger.error(f"Email provider '{provider_name}' is not supported.")
            self.initialization = False
        else:
            self.provider: BaseEmailProvider = providers[provider_name]()

            template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Emailsend/templates'))
            self.template_env = Environment(loader=FileSystemLoader(template_dir))

    def send_email(self, email, subject, username, content_body, slug, template_name, show_button=True, url_type="prompts"):
        try:
            if self.initialization:
                 logger.info(f"Sending email using {self.provider.__class__.__name__} provider.")
                 self.provider.send_email(email, subject, username, content_body, slug, template_name, show_button, url_type)
                 return {"message": "Email sent successfully"}
            else:
                logger.warning("Email provider not initialized or credentials missing.")
                return {"message": "Email provider not initialized or credentials missing."}

        except Exception as e:
            logger.error(f"❌ Failed to send email: {e}")
            return {"message": "Failed to send email"}
            

