from dotenv import load_dotenv
import os
from src.logger.default_logger import logger
import re
from fastapi import HTTPException
from typing import Optional

load_dotenv()

BASE_URL_S3 = os.environ.get("AWS_S3_URL")
BASE_URL_CDN= os.environ.get("AWS_CDN_URL")
S3_BUCKET=os.environ.get("AWS_BUCKET")

LSTACK_BASE_URL_CDN = os.environ.get("LSTACK_CDN_URL")
LSTACK_BUCKET=os.environ.get("AWS_BUCKET")
MINIO_CDN_URL = os.environ.get("MINIO_ENDPOINT")
MINIO_BUCKET = os.environ.get("AWS_BUCKET")


def map_s3_url(url: Optional[str]) -> Optional[str]:
    if url:
        if not url.startswith(BASE_URL_CDN):
            mapped_url = BASE_URL_CDN + url
            logger.info(f"Mapped URL: {mapped_url}")
            return mapped_url
        logger.info(f"URL already mapped: {url}")
    return url

def map_public_url(url: Optional[str]) -> Optional[str]:
    logger.info(f"Using public URL: {url}")
    return url

def map_local_url(url: Optional[str]) -> Optional[str]:
    logger.info(f"Using public URL: {url}")
    return url

def map_localstack_url(url: Optional[str]) -> Optional[str]:
    logger.info(f"Using local file URL: {url}")
    if not url.startswith(LSTACK_BASE_URL_CDN):
        mapped_url = os.path.join(LSTACK_BASE_URL_CDN, LSTACK_BUCKET, url.lstrip("/"))
        logger.info(f"Mapped URL:{mapped_url}")
    return mapped_url

def map_minio_url(url: Optional[str]) -> Optional[str]:
    logger.info(f"Using Minio URL: {url}")
    if not url.startswith(MINIO_CDN_URL):
        mapped_url = os.path.join(MINIO_CDN_URL, MINIO_BUCKET, url.lstrip("/"))
        logger.info(f"Mapped URL: {mapped_url}")
        return mapped_url
    return url

# Define mappings for different source types
SOURCE_URL = {
    's3_url': map_s3_url,
    'public_url': map_public_url,
    'local_file': map_local_url,
    'localstack':map_localstack_url,
    'minio':map_minio_url
}

def map_file_url(file_url: Optional[str], source: str) -> Optional[str]:
    try:

        if file_url is None:
            logger.info("No file URL provided.")
            return None
        
        if source in SOURCE_URL:
            mapped_url = SOURCE_URL[source](file_url)
            logger.info(f"Successfully mapped URL for source '{source}': {mapped_url}")
            return mapped_url
        else:
            error_msg = f"Unsupported source type: {source}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    except Exception as e:
        error_msg = f"Error mapping file URL: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)

# Define validation functions for each source type
def validate_s3_url(url: Optional[str]) -> Optional[str]:
    if url is None:
        logger.info("No URL provided for S3 validation.")
        return None
    
    image_url_regex = re.compile(r'^https://.*\.(?:png|jpg|jpeg|gif|bmp|tiff|svg|webp)$')
    if not image_url_regex.match(url):
        raise ValueError('Invalid S3 image URL format')
    return url

def validate_public_url(url: Optional[str]) -> Optional[str]:
    if url is None:
        logger.info("No URL provided for public URL validation.")
        return None
    
    image_url_regex = re.compile(r'^https://.*\.(?:png|jpg|jpeg|gif|bmp|tiff|svg|webp)$')
    if not image_url_regex.match(url):
        raise ValueError('Invalid public URL format')
    return url

def validate_localstack_url(url: Optional[str]) -> Optional[str]:
    if url is None:
        logger.info("No URL provided for public URL validation.")
        return None
    
    image_url_regex = re.compile(r'^http://.*\.(?:png|jpg|jpeg|gif|bmp|tiff|svg|webp)$')
    if not image_url_regex.match(url):
        raise ValueError('Invalid public URL format')
    return url

def validate_local_url(url: Optional[str]) -> Optional[str]:
    if url is None:
        logger.info("No URL provided for local file validation.")
        return None
    else:
        return url
    
    # # Assuming local file paths should start with '/' and have valid extensions
    # image_url_regex = re.compile(r'^/.*\.(?:png|jpg|jpeg|gif|bmp|tiff|svg|webp)$')
    # if not image_url_regex.match(url):
    #     raise ValueError('Invalid local file URL format')
    # return url

# Define validations for different source types
SOURCE_VALIDATION = {
    's3_url': validate_s3_url,
    "localstack": validate_localstack_url,
    'public_url': validate_public_url,
    'local_file': validate_local_url,
    'minio': validate_local_url
}

def validate_file_url(file_url: Optional[str], source: str) -> Optional[str]:
    try:
        if file_url is None:
            logger.info("No file URL provided for validation.")
            return None
        
        if source in SOURCE_VALIDATION:
            validated_url = SOURCE_VALIDATION[source](file_url)
            logger.info(f"Successfully validated URL for source '{source}': {validated_url}")
            return validated_url
        else:
            error_msg = f"Unsupported source type: {source}"
            logger.error(error_msg)
            raise ValueError(error_msg)
    except Exception as e:
        error_msg = f"Error validating file URL: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=400, detail=error_msg)