from src.content_extraction.text.extractor_base import TextExtractor
from src.content_extraction.text.s3_extractor import S3TextExtractor,LocalStackTextExtractor,MinioTextExtractor
from typing import Union, List
import time
from src.logger.default_logger import logger
import re

class PythonExtractor(TextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from a .py file."""
        start_time = time.time()
        try:
            if self.source.split('.')[-1].lower() != 'py':
                raise ValueError("Unsupported file format for this extractor: Only .py files are supported.")

            raw_text = self.content.getvalue().decode('utf-8')
            content = re.sub(r'\s+', ' ', raw_text).strip()

            logger.info(f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "PythonExtractor.extract_text"}})
            logger.info(f"Time taken: {time.time() - start_time} seconds",
                extra={"tags": {"method": "PythonExtractor.extract_text"}})
            return content
        except Exception as e:
            logger.error(f"Failed to extract text: {e}",
                extra={"tags": {"method": "PythonExtractor.extract_text"}})
            raise e

class S3PythonExtractor(S3TextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from a .py file stored in S3."""
        start_time = time.time()
        try:
            if self.source.split('.')[-1].lower() != 'py':
                raise ValueError("Unsupported file format for this extractor: Only .py files are supported.")

            raw_text = self.content.getvalue().decode('utf-8')
            content = re.sub(r'\s+', ' ', raw_text).strip()

            logger.info(f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "S3PythonExtractor.extract_text"}})
            logger.info(f"Time taken: {time.time() - start_time} seconds",
                extra={"tags": {"method": "S3PythonExtractor.extract_text"}})
            return content
        except Exception as e:
            logger.error(f"Failed to extract text: {e}",
                extra={"tags": {"method": "S3PythonExtractor.extract_text"}})
            raise e

class LSTACKPythonExtractor(LocalStackTextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from a .py file stored in S3."""
        start_time = time.time()
        try:
            if self.source.split('.')[-1].lower() != 'py':
                raise ValueError("Unsupported file format for this extractor: Only .py files are supported.")

            raw_text = self.content.getvalue().decode('utf-8')
            content = re.sub(r'\s+', ' ', raw_text).strip()

            logger.info(f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "LSTACKPythonExtractor.extract_text"}})
            logger.info(f"Time taken: {time.time() - start_time} seconds",
                extra={"tags": {"method": "LSTACKPythonExtractor.extract_text"}})
            return content
        except Exception as e:
            logger.error(f"Failed to extract text: {e}",
                extra={"tags": {"method": "LSTACKPythonExtractor.extract_text"}})
            raise e
        
class MINIOPythonExtractor(MinioTextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from a .py file stored in S3."""
        start_time = time.time()
        try:
            if self.source.split('.')[-1].lower() != 'py':
                raise ValueError("Unsupported file format for this extractor: Only .py files are supported.")

            raw_text = self.content.getvalue().decode('utf-8')
            content = re.sub(r'\s+', ' ', raw_text).strip()

            logger.info(f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "MINIOPythonExtractor.extract_text"}})
            logger.info(f"Time taken: {time.time() - start_time} seconds",
                extra={"tags": {"method": "MINIOPythonExtractor.extract_text"}})
            return content
        except Exception as e:
            logger.error(f"Failed to extract text: {e}",
                extra={"tags": {"method": "MINIOPythonExtractor.extract_text"}})
            raise e