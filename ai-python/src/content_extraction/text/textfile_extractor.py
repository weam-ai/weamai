from src.content_extraction.text.extractor_base import TextExtractor
from src.content_extraction.text.s3_extractor import S3TextExtractor,LocalStackTextExtractor,MinioTextExtractor
import time
from typing import Union, List
from src.logger.default_logger import logger
class TextFileExtractor(TextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from a .txt file."""
        start_time = time.time()
        try:
            # Ensure we are working with the right file format
            if self.source.split('.')[-1].lower() not in  ["text",'txt']:
                raise ValueError("Unsupported file format for this extractor: Only .txt files are supported.")

            # For URLs, the content is already fetched as a BytesIO object
            # For local files, it was also converted to BytesIO for consistency
            # Convert BytesIO back to a string for text processing
            text_content = self.content.getvalue().decode('utf-8')  # Assuming UTF-8 encoding, change if necessary

            logger.info(
                f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "TextFileExtractor.extract_text"}}
            )
            end_time = time.time()  # End timing
            logger.info(
                f"Time taken to extract text from PDF: {end_time - start_time} seconds",
                extra={"tags": {"method": "TextFileExtractor.extract_text"}}
            )
            return text_content
        except Exception as e:
            logger.error(
                f"Failed to extract text from {self.source}: {e}",
                extra={"tags": {"method": "TextFileExtractor.extract_text"}}
            )
            raise e


class S3TextFileExtractor(S3TextExtractor):
       def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from a .txt file."""
        start_time = time.time()
        try:
            # Ensure we are working with the right file format
            if self.source.split('.')[-1].lower() not in ['txt',"text"]:
                raise ValueError("Unsupported file format for this extractor: Only .txt files are supported.")

            # For URLs, the content is already fetched as a BytesIO object
            # For local files, it was also converted to BytesIO for consistency
            # Convert BytesIO back to a string for text processing
            text_content = self.content.getvalue().decode('utf-8')  # Assuming UTF-8 encoding, change if necessary

            logger.info(
                f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "S3TextFileExtractor.extract_text"}}
            )
            end_time = time.time()  # End timing
            logger.info(
                f"Time taken to extract text from PDF: {end_time - start_time} seconds",
                extra={"tags": {"method": "S3TextFileExtractor.extract_text"}}
            )
            return text_content
        except Exception as e:
            logger.error(
                f"Failed to extract text from {self.source}: {e}",
                extra={"tags": {"method": "S3TextFileExtractor.extract_text"}}
            )
            raise e

class LSTACKTextFileExtractor(LocalStackTextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from a .txt file."""
        start_time = time.time()
        try:
            # Ensure we are working with the right file format
            if self.source.split('.')[-1].lower() not in ['txt',"text"]:
                raise ValueError("Unsupported file format for this extractor: Only .txt files are supported.")

            # For URLs, the content is already fetched as a BytesIO object
            # For local files, it was also converted to BytesIO for consistency
            # Convert BytesIO back to a string for text processing
            text_content = self.content.getvalue().decode('utf-8')  # Assuming UTF-8 encoding, change if necessary

            logger.info(
                f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "LSTACKTextFileExtractor.extract_text"}}
            )
            end_time = time.time()  # End timing
            logger.info(
                f"Time taken to extract text from PDF: {end_time - start_time} seconds",
                extra={"tags": {"method": "LSTACKTextFileExtractor.extract_text"}}
            )
            return text_content
        except Exception as e:
            logger.error(
                f"Failed to extract text from {self.source}: {e}",
                extra={"tags": {"method": "LSTACKTextFileExtractor.extract_text"}}
            )
            raise e
        
class MINIOTextFileExtractor(MinioTextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from a .txt file."""
        start_time = time.time()
        try:
            # Ensure we are working with the right file format
            if self.source.split('.')[-1].lower() not in ['txt',"text"]:
                raise ValueError("Unsupported file format for this extractor: Only .txt files are supported.")

            # For URLs, the content is already fetched as a BytesIO object
            # For local files, it was also converted to BytesIO for consistency
            # Convert BytesIO back to a string for text processing
            text_content = self.content.getvalue().decode('utf-8')  # Assuming UTF-8 encoding, change if necessary

            logger.info(
                f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "MINIOTextFileExtractor.extract_text"}}
            )
            end_time = time.time()  # End timing
            logger.info(
                f"Time taken to extract text from PDF: {end_time - start_time} seconds",
                extra={"tags": {"method": "MINIOTextFileExtractor.extract_text"}}
            )
            return text_content
        except Exception as e:
            logger.error(
                f"Failed to extract text from {self.source}: {e}",
                extra={"tags": {"method": "MINIOTextFileExtractor.extract_text"}}
            )
            raise e