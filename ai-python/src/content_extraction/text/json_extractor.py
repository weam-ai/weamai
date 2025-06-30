from src.content_extraction.text.extractor_base import TextExtractor
import json
from typing import Union, List
from src.content_extraction.text.s3_extractor import S3TextExtractor,LocalStackTextExtractor,MinioTextExtractor
import time
from src.logger.default_logger import logger

class JSONExtractor(TextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extracts and pretty-prints JSON content from a file."""
        start_time = time.time()
        try:
            # Decode bytes to string and load JSON
            raw_text = self.content.getvalue().decode('utf-8')
            json_obj = json.loads(raw_text)
            # Pretty-print JSON
            content = json.dumps(json_obj, indent=2, ensure_ascii=False)
            logger.info(
                f"Successfully extracted JSON from {self.source}",
                extra={"tags": {"method": "JSONExtractor.extract_text"}}
            )
            end_time = time.time()
            logger.info(
                f"Time taken to extract text from JSON: {end_time - start_time} seconds",
                extra={"tags": {"method": "JSONExtractor.extract_text"}}
            )
            return content
        except Exception as e:
            logger.error(
                f"Failed to extract JSON from {self.source}: {e}",
                extra={"tags": {"method": "JSONExtractor.extract_text"}}
            )
            raise e

class S3JSONExtractor(S3TextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extracts and pretty-prints JSON content from an S3 file."""
        start_time = time.time()
        try:
            raw_text = self.content.getvalue().decode('utf-8')
            json_obj = json.loads(raw_text)
            content = json.dumps(json_obj, indent=2, ensure_ascii=False)
            logger.info(
                f"Successfully extracted JSON from {self.source}",
                extra={"tags": {"method": "S3JSONExtractor.extract_text"}}
            )
            end_time = time.time()
            logger.info(
                f"Time taken to extract text from JSON: {end_time - start_time} seconds",
                extra={"tags": {"method": "S3JSONExtractor.extract_text"}}
            )
            return content
        except Exception as e:
            logger.error(
                f"Failed to extract JSON from {self.source}: {e}",
                extra={"tags": {"method": "S3JSONExtractor.extract_text"}}
            )
            raise e
        
class LSTACKJSONExtractor(LocalStackTextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extracts and pretty-prints JSON content from an S3 file."""
        start_time = time.time()
        try:
            raw_text = self.content.getvalue().decode('utf-8')
            json_obj = json.loads(raw_text)
            content = json.dumps(json_obj, indent=2, ensure_ascii=False)
            logger.info(
                f"Successfully extracted JSON from {self.source}",
                extra={"tags": {"method": "LSTACKJSONExtractor.extract_text"}}
            )
            end_time = time.time()
            logger.info(
                f"Time taken to extract text from JSON: {end_time - start_time} seconds",
                extra={"tags": {"method": "LSTACKJSONExtractor.extract_text"}}
            )
            return content
        except Exception as e:
            logger.error(
                f"Failed to extract JSON from {self.source}: {e}",
                extra={"tags": {"method": "LSTACKJSONExtractor.extract_text"}}
            )
            raise e
        
class MINIOJSONExtractor(MinioTextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extracts and pretty-prints JSON content from an S3 file."""
        start_time = time.time()
        try:
            raw_text = self.content.getvalue().decode('utf-8')
            json_obj = json.loads(raw_text)
            content = json.dumps(json_obj, indent=2, ensure_ascii=False)
            logger.info(
                f"Successfully extracted JSON from {self.source}",
                extra={"tags": {"method": "MINIOJSONExtractor.extract_text"}}
            )
            end_time = time.time()
            logger.info(
                f"Time taken to extract text from JSON: {end_time - start_time} seconds",
                extra={"tags": {"method": "MINIOJSONExtractor.extract_text"}}
            )
            return content
        except Exception as e:
            logger.error(
                f"Failed to extract JSON from {self.source}: {e}",
                extra={"tags": {"method": "MINIOJSONExtractor.extract_text"}}
            )
            raise e