import re
from io import BytesIO
from src.content_extraction.text.extractor_base import TextExtractor
import os
from src.logger.default_logger import logger
import requests
import re
class S3TextExtractor(TextExtractor):
    def _validate_url(self):
        """Validate the S3 URL to ensure it's well-formed and points to a supported file type."""
        
        # s3_url_pattern = r'^https:\/\/[a-zA-Z0-9-]+\.s3\.([a-zA-Z0-9-]+\.){0,2}amazonaws\.com\/.*'
        cdn_url_pattern = re.compile(os.environ.get("AWS_REGEX_FILE_PATTERN"))
        # cdn_url_pattern = r'^https:\/\/cdn(?:\.[a-zA-Z0-9-]+)*\.weam\.ai\/.*$'

        # Check if the URL ,is a well-formed HTTP URL pointing to S3
        if not re.match(cdn_url_pattern, self.source):
            logger.error("Invalid HTTP URL format", extra={"tags": {"method": "S3TextExtractor._validate_url"}})
            raise ValueError("Invalid HTTP URL format")
        
        # Check if the URL points to a supported file format
        file_extension = self.source.split('.')[-1].lower()
        if file_extension not in self.SUPPORTED_FORMATS:
            logger.error(f"Unsupported file format: {file_extension}", extra={"tags": {"method": "S3TextExtractor._validate_url"}})
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




class LocalStackTextExtractor(TextExtractor):

    def _validate_url(self):
        """Validate that the URL points to a LocalStack S3 object and is a supported file format."""
  
        localstack_pattern = re.compile(os.environ.get("LSTACK_REGEX_FILE_PATTERN"))
        

        if not re.match(localstack_pattern, self.source):
            logger.error("Invalid LocalStack URL format", extra={"tags": {"method": "LocalStackTextExtractor._validate_url"}})
            raise ValueError("Invalid LocalStack URL format")

        file_extension = self.source.split('.')[-1].lower()
        if file_extension not in self.SUPPORTED_FORMATS:
            logger.error(f"Unsupported file format: {file_extension}", extra={"tags": {"method": "LocalStackTextExtractor._validate_url"}})
            raise ValueError(f"Unsupported file format: {file_extension}")

    def _fetch_content_from_url(self) -> BytesIO:
        """Fetch the content from the LocalStack S3 URL and return it as BytesIO."""
        try:
            response = requests.get(self.source)
            response.raise_for_status()
            logger.info(
                f"Successfully fetched content from URL: {self.source}",
                extra={"tags": {"method": "LocalStackTextExtractor._fetch_content_from_url"}}
            )
            return BytesIO(response.content)
        except requests.RequestException as e:
            logger.error(
                f"Failed to fetch content from URL: {self.source}: {e}",
                extra={"tags": {"method": "LocalStackTextExtractor._fetch_content_from_url"}}
            )
            raise

class MinioTextExtractor(TextExtractor):

    def _validate_url(self):
        """Validate that the URL points to a Minio S3 object and is a supported file format."""
  
        # minio_pattern = re.compile(os.environ.get("MINO_REGEX_FILE_PATTERN"))
        

        # if not re.match(minio_pattern, self.source):
        #     logger.error("Invalid Minio URL format", extra={"tags": {"method": "MinioTextExtractor._validate_url"}})
        #     raise ValueError("Invalid Minio URL format")

        file_extension = self.source.split('.')[-1].lower()
        if file_extension not in self.SUPPORTED_FORMATS:
            logger.error(f"Unsupported file format: {file_extension}", extra={"tags": {"method": "MinioTextExtractor._validate_url"}})
            raise ValueError(f"Unsupported file format: {file_extension}")

    def _fetch_content_from_url(self) -> BytesIO:
        """Fetch the content from the Minio S3 URL and return it as BytesIO."""
        try:
            response = requests.get(self.source)
            response.raise_for_status()
            logger.info(
                f"Successfully fetched content from URL: {self.source}",
                extra={"tags": {"method": "MinioTextExtractor._fetch_content_from_url"}}
            )
            return BytesIO(response.content)
        except requests.RequestException as e:
            logger.error(
                f"Failed to fetch content from URL: {self.source}: {e}",
                extra={"tags": {"method": "MinioTextExtractor._fetch_content_from_url"}}
            )
            raise
    # def _fetch_content_from_url(self) -> BytesIO:
    #     """Fetch the content from the S3 URL and return it as a BytesIO object."""
    #     # Split HTTP URL to get bucket and file_key
    #     bucket_name, file_key = self.source.split('https://', 1)[-1].split('.s3.amazonaws.com/', 1)
       
    #     # Use boto3 to fetch the file from S3
    #     s3_client = LocalStackS3Client().client
    #     try:
    #         response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
    #         logger.info("Successfully fetched content from S3.", extra={"tags": {"method": "S3TextExtractor._fetch_content_from_url"}})

    #     except (NoCredentialsError, ClientError) as e:
    #         logger.error(f"Failed to fetch from S3: {str(e)}", extra={"tags": {"method": "S3TextExtractor._fetch_content_from_url"}})
    #         raise ValueError(f"Failed to fetch from S3: {str(e)}")

    #     return BytesIO(response['Body'].read())
