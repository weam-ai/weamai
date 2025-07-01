from abc import ABC, abstractmethod
import requests
from io import BytesIO
import re
import os
from src.logger.default_logger import logger

class TextExtractor(ABC):
    SUPPORTED_FORMATS = ['pdf', 'doc', 'docx', "txt", "text", 'xlsx', 'csv', 'xls', 'eml', 'php', 'js', 'css', 'html', 'htm', 'sql', 'py', 'json']


    def __init__(self, source: str, is_url: bool = True):
        self.source = source
        self.is_url = is_url
        self.content = None

        try:
            if self.is_url:
                self._validate_url()
                self.content = self._fetch_content_from_url()
            else:
                self._validate_file_path()
                self.content = self._fetch_content_from_file()

            self._validate_content()
            logger.info(
                f"Initialization successful for {self.source}",
                extra={"tags": {"method": "TextExtractor.__init__"}}
            )
        except Exception as e:
            logger.error(
                f"Initialization failed for {self.source}: {e}",
                extra={"tags": {"method": "TextExtractor.__init__"}}
            )
            raise e

    def _validate_url(self):
        """Validate the URL to ensure it's well-formed and points to a supported file type."""
        
        if not re.match(r'https?://[^\s]+', self.source):
            logger.error(
                "Invalid URL format",
                extra={"tags": {"method": "TextExtractor._validate_url"}}
            )
            raise ValueError("Invalid URL format")
        self._validate_extension(self.source)

    def _validate_file_path(self):
        """Validate the file path to ensure it points to a supported file type."""
        if not os.path.exists(self.source):
            logger.error(
                "File does not exist",
                extra={"tags": {"method": "TextExtractor._validate_file_path"}}
            )
            raise ValueError("File does not exist")
        self._validate_extension(self.source)

    def _validate_extension(self, path):
        """Validate the extension of the file or URL."""
        file_extension = path.split('.')[-1].lower()
        if file_extension not in self.SUPPORTED_FORMATS:
            logger.error(
                f"Unsupported file format: {file_extension}",
                extra={"tags": {"method": "TextExtractor._validate_extension"}}
            )
            raise ValueError(f"Unsupported file format: {file_extension}")

    def _fetch_content_from_url(self) -> BytesIO:
        """Fetch the content from the URL and return it as a BytesIO object."""
        try:
            response = requests.get(self.source)
            response.raise_for_status()  # Raises an exception for HTTP errors
            logger.info(
                f"Successfully fetched content from URL: {self.source}",
                extra={"tags": {"method": "TextExtractor._fetch_content_from_url"}}
            )
            return BytesIO(response.content)
        except requests.RequestException as e:
            logger.error(
                f"Failed to fetch content from URL: {self.source}: {e}",
                extra={"tags": {"method": "TextExtractor._fetch_content_from_url"}}
            )
            raise

    def _fetch_content_from_file(self) -> BytesIO:
        """Read the content from a file and return it as a BytesIO object."""
        try:
            with open(self.source, 'rb') as file:
                content = BytesIO(file.read())
            logger.info(
                f"Successfully read content from file: {self.source}",
                extra={"tags": {"method": "TextExtractor._fetch_content_from_file"}}
            )
            return content
        except IOError as e:
            logger.error(
                f"Failed to read content from file: {self.source}: {e}",
                extra={"tags": {"method": "TextExtractor._fetch_content_from_file"}}
            )
            raise

    def _validate_content(self):
        """Validate the fetched content to ensure it's not empty."""
        if self.content.getbuffer().nbytes == 0:
            logger.error(
                "Fetched content is empty",
                extra={"tags": {"method": "TextExtractor._validate_content"}}
            )
            raise ValueError("Fetched content is empty")

    @abstractmethod
    def extract_text(self) -> str:
        """Abstract method to be implemented by subclasses for extracting text."""
        pass
