from src.content_extraction.text.extractor_base import TextExtractor
from src.content_extraction.text.s3_extractor import S3TextExtractor,LocalStackTextExtractor,MinioTextExtractor
from typing import Union, List
import re

class SQLExtractor(TextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extracts text from a SQL file."""
        try:
            # For local file, content is a file path
            if self.source.split('.')[-1].lower() != 'sql':
                raise ValueError("Unsupported file format for this extractor: Only .html files are supported.")

            raw_text = self.content.getvalue().decode('utf-8')
            content = re.sub(r'\s+', ' ', raw_text).strip()
            return content
        except Exception as e:
            raise Exception(f"Error extracting SQL content: {str(e)}")

class S3SQLExtractor(S3TextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extracts text from a SQL file stored in S3."""
        try:
            if self.source.split('.')[-1].lower() != 'sql':
                raise ValueError("Unsupported file format for this extractor: Only .html files are supported.")

            raw_text = self.content.getvalue().decode('utf-8')
            content = re.sub(r'\s+', ' ', raw_text).strip()
            return content
        except Exception as e:
            raise Exception(f"Error extracting SQL content from S3: {str(e)}")

class LSTACKSQLExtractor(LocalStackTextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extracts text from a SQL file stored in S3."""
        try:
            if self.source.split('.')[-1].lower() != 'sql':
                raise ValueError("Unsupported file format for this extractor: Only .html files are supported.")

            raw_text = self.content.getvalue().decode('utf-8')
            content = re.sub(r'\s+', ' ', raw_text).strip()
            return content
        except Exception as e:
            raise Exception(f"Error extracting SQL content from S3: {str(e)}")
    
class MINIOSQLExtractor(MinioTextExtractor):
    def extract_text(self, page_wise: bool = False) -> Union[str, List[str]]:
        """Extracts text from a SQL file stored in S3."""
        try:
            if self.source.split('.')[-1].lower() != 'sql':
                raise ValueError("Unsupported file format for this extractor: Only .html files are supported.")

            raw_text = self.content.getvalue().decode('utf-8')
            content = re.sub(r'\s+', ' ', raw_text).strip()
            return content
        except Exception as e:
            raise Exception(f"Error extracting SQL content from S3: {str(e)}")