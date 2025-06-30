from src.content_extraction.text.extractor_base import TextExtractor
from src.content_extraction.text.s3_extractor import S3TextExtractor,LocalStackTextExtractor,MinioTextExtractor
from typing import Union, List
import time
from src.logger.default_logger import logger
import re

class JSExtractor(TextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from a .js file."""
        start_time = time.time()
        try:
            if self.source.split('.')[-1].lower() != 'js':
                raise ValueError("Unsupported file format for this extractor: Only .js files are supported.")

            raw_text = self.content.getvalue().decode('utf-8')
            content = re.sub(r'\s+', ' ', raw_text).strip()

            logger.info(f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "JSExtractor.extract_text"}})
            logger.info(f"Time taken: {time.time() - start_time} seconds",
                extra={"tags": {"method": "JSExtractor.extract_text"}})
            return content
        except Exception as e:
            logger.error(f"Failed to extract text: {e}",
                extra={"tags": {"method": "JSExtractor.extract_text"}})
            raise e

class S3JSExtractor(S3TextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from a .js file stored in S3."""
        start_time = time.time()
        try:
            if self.source.split('.')[-1].lower() != 'js':
                raise ValueError("Unsupported file format for this extractor: Only .js files are supported.")

            raw_text = self.content.getvalue().decode('utf-8')
            content = re.sub(r'\s+', ' ', raw_text).strip()

            logger.info(f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "S3JSExtractor.extract_text"}})
            logger.info(f"Time taken: {time.time() - start_time} seconds",
                extra={"tags": {"method": "S3JSExtractor.extract_text"}})
            return content
        except Exception as e:
            logger.error(f"Failed to extract text: {e}",
                extra={"tags": {"method": "S3JSExtractor.extract_text"}})
            raise e

class LSTACKJSExtractor(LocalStackTextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from a .js file stored in S3."""
        start_time = time.time()
        try:
            if self.source.split('.')[-1].lower() != 'js':
                raise ValueError("Unsupported file format for this extractor: Only .js files are supported.")

            raw_text = self.content.getvalue().decode('utf-8')
            content = re.sub(r'\s+', ' ', raw_text).strip()

            logger.info(f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "LSTACKJSExtractor.extract_text"}})
            logger.info(f"Time taken: {time.time() - start_time} seconds",
                extra={"tags": {"method": "LSTACKJSExtractor.extract_text"}})
            return content
        except Exception as e:
            logger.error(f"Failed to extract text: {e}",
                extra={"tags": {"method": "LSTACKJSExtractor.extract_text"}})
            raise e
        
class MINIOJSExtractor(MinioTextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from a .js file stored in S3."""
        start_time = time.time()
        try:
            if self.source.split('.')[-1].lower() != 'js':
                raise ValueError("Unsupported file format for this extractor: Only .js files are supported.")

            raw_text = self.content.getvalue().decode('utf-8')
            content = re.sub(r'\s+', ' ', raw_text).strip()

            logger.info(f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "MINIOJSExtractor.extract_text"}})
            logger.info(f"Time taken: {time.time() - start_time} seconds",
                extra={"tags": {"method": "MINIOJSExtractor.extract_text"}})
            return content
        except Exception as e:
            logger.error(f"Failed to extract text: {e}",
                extra={"tags": {"method": "MINIOJSExtractor.extract_text"}})
            raise e