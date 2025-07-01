from src.content_extraction.text.extractor_base import TextExtractor
from src.content_extraction.text.s3_extractor import S3TextExtractor,LocalStackTextExtractor,MinioTextExtractor
import email
from typing import Union, List
import time
from src.logger.default_logger import logger

class EMLExtractor(TextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from an .eml file."""
        start_time = time.time()
        try:
            if self.source.split('.')[-1].lower() != 'eml':
                raise ValueError("Unsupported file format for this extractor: Only .eml files are supported.")

            # Parse the email content
            msg = email.message_from_bytes(self.content.getvalue())
            
            # Extract email metadata
            metadata = f"From: {msg['from']}\nTo: {msg['to']}\nSubject: {msg['subject']}\nDate: {msg['date']}\n\n"
            
            # Extract body content
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body += part.get_payload(decode=True).decode()
            else:
                body = msg.get_payload(decode=True).decode()

            full_content = metadata + body

            logger.info(
                f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "EMLExtractor.extract_text"}}
            )
            end_time = time.time()
            logger.info(
                f"Time taken to extract text from EML: {end_time - start_time} seconds",
                extra={"tags": {"method": "EMLExtractor.extract_text"}}
            )
            return full_content
        except Exception as e:
            logger.error(
                f"Failed to extract text from {self.source}: {e}",
                extra={"tags": {"method": "EMLExtractor.extract_text"}}
            )
            raise e

class S3EMLExtractor(S3TextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from an .eml file stored in S3."""
        start_time = time.time()
        try:
            if self.source.split('.')[-1].lower() != 'eml':
                raise ValueError("Unsupported file format for this extractor: Only .eml files are supported.")

            # Parse the email content
            msg = email.message_from_bytes(self.content.getvalue())
            
            # Extract email metadata
            metadata = f"From: {msg['from']}\nTo: {msg['to']}\nSubject: {msg['subject']}\nDate: {msg['date']}\n\n"
            
            # Extract body content
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body += part.get_payload(decode=True).decode()
            else:
                body = msg.get_payload(decode=True).decode()

            full_content = metadata + body

            logger.info(
                f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "S3EMLExtractor.extract_text"}}
            )
            end_time = time.time()
            logger.info(
                f"Time taken to extract text from EML: {end_time - start_time} seconds",
                extra={"tags": {"method": "S3EMLExtractor.extract_text"}}
            )
            return full_content
        except Exception as e:
            logger.error(
                f"Failed to extract text from {self.source}: {e}",
                extra={"tags": {"method": "S3EMLExtractor.extract_text"}}
            )
            raise e
        
class LSTACKEMLExtractor(LocalStackTextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from an .eml file stored in S3."""
        start_time = time.time()
        try:
            if self.source.split('.')[-1].lower() != 'eml':
                raise ValueError("Unsupported file format for this extractor: Only .eml files are supported.")

            # Parse the email content
            msg = email.message_from_bytes(self.content.getvalue())
            
            # Extract email metadata
            metadata = f"From: {msg['from']}\nTo: {msg['to']}\nSubject: {msg['subject']}\nDate: {msg['date']}\n\n"
            
            # Extract body content
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body += part.get_payload(decode=True).decode()
            else:
                body = msg.get_payload(decode=True).decode()

            full_content = metadata + body

            logger.info(
                f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "LSTACKEMLExtractor.extract_text"}}
            )
            end_time = time.time()
            logger.info(
                f"Time taken to extract text from EML: {end_time - start_time} seconds",
                extra={"tags": {"method": "LSTACKEMLExtractor.extract_text"}}
            )
            return full_content
        except Exception as e:
            logger.error(
                f"Failed to extract text from {self.source}: {e}",
                extra={"tags": {"method": "LSTACKEMLExtractor.extract_text"}}
            )
            raise e
        

class MINIOEMLExtractor(MinioTextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from an .eml file stored in S3."""
        start_time = time.time()
        try:
            if self.source.split('.')[-1].lower() != 'eml':
                raise ValueError("Unsupported file format for this extractor: Only .eml files are supported.")

            # Parse the email content
            msg = email.message_from_bytes(self.content.getvalue())
            
            # Extract email metadata
            metadata = f"From: {msg['from']}\nTo: {msg['to']}\nSubject: {msg['subject']}\nDate: {msg['date']}\n\n"
            
            # Extract body content
            body = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        body += part.get_payload(decode=True).decode()
            else:
                body = msg.get_payload(decode=True).decode()

            full_content = metadata + body

            logger.info(
                f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "MINIOEMLExtractor.extract_text"}}
            )
            end_time = time.time()
            logger.info(
                f"Time taken to extract text from EML: {end_time - start_time} seconds",
                extra={"tags": {"method": "MINIOEMLExtractor.extract_text"}}
            )
            return full_content
        except Exception as e:
            logger.error(
                f"Failed to extract text from {self.source}: {e}",
                extra={"tags": {"method": "MINIOEMLExtractor.extract_text"}}
            )
            raise e