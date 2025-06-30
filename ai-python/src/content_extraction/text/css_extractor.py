from src.content_extraction.text.extractor_base import TextExtractor
from src.content_extraction.text.s3_extractor import S3TextExtractor,LocalStackTextExtractor,MinioTextExtractor
from typing import Union, List
import time
from src.logger.default_logger import logger
import re

class CSSExtractor(TextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from a .css file."""
        start_time = time.time()
        try:
            if self.source.split('.')[-1].lower() != 'css':
                raise ValueError("Unsupported file format for this extractor: Only .css files are supported.")

            raw_text = self.content.getvalue().decode('utf-8')
            content = re.sub(r'\s+', ' ', raw_text).strip()

            logger.info(f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "CSSExtractor.extract_text"}})
            logger.info(f"Time taken: {time.time() - start_time} seconds",
                extra={"tags": {"method": "CSSExtractor.extract_text"}})
            return content
        except Exception as e:
            logger.error(f"Failed to extract text: {e}",
                extra={"tags": {"method": "CSSExtractor.extract_text"}})
            raise e

class S3CSSExtractor(S3TextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from a .css file stored in S3."""
        start_time = time.time()
        try:
            if self.source.split('.')[-1].lower() != 'css':
                raise ValueError("Unsupported file format for this extractor: Only .css files are supported.")

            raw_text = self.content.getvalue().decode('utf-8')
            content = re.sub(r'\s+', ' ', raw_text).strip()

            logger.info(f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "S3CSSExtractor.extract_text"}})
            logger.info(f"Time taken: {time.time() - start_time} seconds",
                extra={"tags": {"method": "S3CSSExtractor.extract_text"}})
            return content
        except Exception as e:
            logger.error(f"Failed to extract text: {e}",
                extra={"tags": {"method": "S3CSSExtractor.extract_text"}})
            raise e
        
class LSTACKCSSExtractor(LocalStackTextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from a .css file stored in S3."""
        start_time = time.time()
        try:
            if self.source.split('.')[-1].lower() != 'css':
                raise ValueError("Unsupported file format for this extractor: Only .css files are supported.")

            raw_text = self.content.getvalue().decode('utf-8')
            content = re.sub(r'\s+', ' ', raw_text).strip()

            logger.info(f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "LSTACKCSSExtractor.extract_text"}})
            logger.info(f"Time taken: {time.time() - start_time} seconds",
                extra={"tags": {"method": "LSTACKCSSExtractor.extract_text"}})
            return content
        except Exception as e:
            logger.error(f"Failed to extract text: {e}",
                extra={"tags": {"method": "LSTACKCSSExtractor.extract_text"}})
            raise e
    
class MINIOCSSExtractor(MinioTextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from a .css file stored in S3."""
        start_time = time.time()
        try:
            if self.source.split('.')[-1].lower() != 'css':
                raise ValueError("Unsupported file format for this extractor: Only .css files are supported.")

            raw_text = self.content.getvalue().decode('utf-8')
            content = re.sub(r'\s+', ' ', raw_text).strip()

            logger.info(f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "LSTACKCSSExtractor.extract_text"}})
            logger.info(f"Time taken: {time.time() - start_time} seconds",
                extra={"tags": {"method": "LSTACKCSSExtractor.extract_text"}})
            return content
        except Exception as e:
            logger.error(f"Failed to extract text: {e}",
                extra={"tags": {"method": "LSTACKCSSExtractor.extract_text"}})
            raise e