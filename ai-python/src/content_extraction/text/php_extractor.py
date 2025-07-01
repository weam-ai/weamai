from src.content_extraction.text.extractor_base import TextExtractor
from src.content_extraction.text.s3_extractor import S3TextExtractor,LocalStackTextExtractor,MinioTextExtractor
from typing import Union, List
import time
from src.logger.default_logger import logger
import re  # Add this at the top

class PHPExtractor(TextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from a .php file."""
        start_time = time.time()
        try:
            if self.source.split('.')[-1].lower() != 'php':
                raise ValueError("Unsupported file format for this extractor: Only .php files are supported.")

            raw_text = self.content.getvalue().decode('utf-8')
            content = re.sub(r'\s+', ' ', raw_text).strip()

            logger.info(
                f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "PHPExtractor.extract_text"}}
            )
            end_time = time.time()
            logger.info(
                f"Time taken to extract text from PHP: {end_time - start_time} seconds",
                extra={"tags": {"method": "PHPExtractor.extract_text"}}
            )
            return content
        except Exception as e:
            logger.error(
                f"Failed to extract text from {self.source}: {e}",
                extra={"tags": {"method": "PHPExtractor.extract_text"}}
            )
            raise e

class S3PHPExtractor(S3TextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from a .php file stored in S3."""
        start_time = time.time()
        try:
            if self.source.split('.')[-1].lower() != 'php':
                raise ValueError("Unsupported file format for this extractor: Only .php files are supported.")

            # Read the PHP file content
            raw_text = self.content.getvalue().decode('utf-8')
            content = re.sub(r'\s+', ' ', raw_text).strip()

            logger.info(
                f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "S3PHPExtractor.extract_text"}}
            )
            end_time = time.time()
            logger.info(
                f"Time taken to extract text from PHP: {end_time - start_time} seconds",
                extra={"tags": {"method": "S3PHPExtractor.extract_text"}}
            )
            return content
        except Exception as e:
            logger.error(
                f"Failed to extract text from {self.source}: {e}",
                extra={"tags": {"method": "S3PHPExtractor.extract_text"}}
            )
            raise e

class LSTACKPHPExtractor(LocalStackTextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from a .php file stored in S3."""
        start_time = time.time()
        try:
            if self.source.split('.')[-1].lower() != 'php':
                raise ValueError("Unsupported file format for this extractor: Only .php files are supported.")

            # Read the PHP file content
            raw_text = self.content.getvalue().decode('utf-8')
            content = re.sub(r'\s+', ' ', raw_text).strip()

            logger.info(
                f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "LSTACKPHPExtractor.extract_text"}}
            )
            end_time = time.time()
            logger.info(
                f"Time taken to extract text from PHP: {end_time - start_time} seconds",
                extra={"tags": {"method": "LSTACKPHPExtractor.extract_text"}}
            )
            return content
        except Exception as e:
            logger.error(
                f"Failed to extract text from {self.source}: {e}",
                extra={"tags": {"method": "LSTACKPHPExtractor.extract_text"}}
            )
            raise e
        
class MINIOPHPExtractor(MinioTextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extract text from a .php file stored in S3."""
        start_time = time.time()
        try:
            if self.source.split('.')[-1].lower() != 'php':
                raise ValueError("Unsupported file format for this extractor: Only .php files are supported.")

            # Read the PHP file content
            raw_text = self.content.getvalue().decode('utf-8')
            content = re.sub(r'\s+', ' ', raw_text).strip()

            logger.info(
                f"Successfully extracted text from {self.source}",
                extra={"tags": {"method": "MINIOPHPExtractor.extract_text"}}
            )
            end_time = time.time()
            logger.info(
                f"Time taken to extract text from PHP: {end_time - start_time} seconds",
                extra={"tags": {"method": "MINIOPHPExtractor.extract_text"}}
            )
            return content
        except Exception as e:
            logger.error(
                f"Failed to extract text from {self.source}: {e}",
                extra={"tags": {"method": "MINIOPHPExtractor.extract_text"}}
            )
            raise e