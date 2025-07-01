from src.content_extraction.text.extractor_base import TextExtractor
from src.content_extraction.text.s3_extractor import S3TextExtractor,LocalStackTextExtractor,MinioTextExtractor
from typing import Union, List
import time
from bs4 import BeautifulSoup
from src.logger.default_logger import logger
import re

class HTMLExtractor(TextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from an .html file."""
        start_time = time.time()
        try:
            if self.source.split('.')[-1].lower() not in ['html', 'htm']:
                raise ValueError("Unsupported file format for this extractor: Only .html files are supported.")

            raw_text = self.content.getvalue().decode('utf-8')
            content = re.sub(r'\s+', ' ', raw_text).strip()
            
            # Parse HTML and extract text content
            # soup = BeautifulSoup(content, 'html.parser')
            # text_content = soup.get_text(separator='\n', strip=True)

            logger.info(f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "HTMLExtractor.extract_text"}})
            logger.info(f"Time taken: {time.time() - start_time} seconds",
                extra={"tags": {"method": "HTMLExtractor.extract_text"}})
            return content
        except Exception as e:
            logger.error(f"Failed to extract text: {e}",
                extra={"tags": {"method": "HTMLExtractor.extract_text"}})
            raise e

class S3HTMLExtractor(S3TextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from an .html file stored in S3."""
        start_time = time.time()
        try:
            if self.source.split('.')[-1].lower() not in ['html', 'htm']:
                raise ValueError("Unsupported file format for this extractor: Only .html files are supported.")

            raw_text = self.content.getvalue().decode('utf-8')
            content = re.sub(r'\s+', ' ', raw_text).strip()
            
            # Parse HTML and extract text content
            # soup = BeautifulSoup(content, 'html.parser')
            # text_content = soup.get_text(separator='\n', strip=True)

            logger.info(f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "S3HTMLExtractor.extract_text"}})
            logger.info(f"Time taken: {time.time() - start_time} seconds",
                extra={"tags": {"method": "S3HTMLExtractor.extract_text"}})
            return content
        except Exception as e:
            logger.error(f"Failed to extract text: {e}",
                extra={"tags": {"method": "S3HTMLExtractor.extract_text"}})
            raise e

class LSTACKHTMLExtractor(LocalStackTextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from an .html file stored in S3."""
        start_time = time.time()
        try:
            if self.source.split('.')[-1].lower() not in ['html', 'htm']:
                raise ValueError("Unsupported file format for this extractor: Only .html files are supported.")

            raw_text = self.content.getvalue().decode('utf-8')
            content = re.sub(r'\s+', ' ', raw_text).strip()
            
            # Parse HTML and extract text content
            # soup = BeautifulSoup(content, 'html.parser')
            # text_content = soup.get_text(separator='\n', strip=True)

            logger.info(f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "LSTACKHTMLExtractor.extract_text"}})
            logger.info(f"Time taken: {time.time() - start_time} seconds",
                extra={"tags": {"method": "LSTACKHTMLExtractor.extract_text"}})
            return content
        except Exception as e:
            logger.error(f"Failed to extract text: {e}",
                extra={"tags": {"method": "LSTACKHTMLExtractor.extract_text"}})
            raise e
        
class MINIOHTMLExtractor(MinioTextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from an .html file stored in S3."""
        start_time = time.time()
        try:
            if self.source.split('.')[-1].lower() not in ['html', 'htm']:
                raise ValueError("Unsupported file format for this extractor: Only .html files are supported.")

            raw_text = self.content.getvalue().decode('utf-8')
            content = re.sub(r'\s+', ' ', raw_text).strip()
            
            # Parse HTML and extract text content
            # soup = BeautifulSoup(content, 'html.parser')
            # text_content = soup.get_text(separator='\n', strip=True)

            logger.info(f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "MINIOHTMLExtractor.extract_text"}})
            logger.info(f"Time taken: {time.time() - start_time} seconds",
                extra={"tags": {"method": "MINIOHTMLExtractor.extract_text"}})
            return content
        except Exception as e:
            logger.error(f"Failed to extract text: {e}",
                extra={"tags": {"method": "MINIOHTMLExtractor.extract_text"}})
            raise e