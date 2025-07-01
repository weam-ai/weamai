from src.aws.boto3_client import Boto3S3Client
from src.aws.localstack_client import LocalStackS3Client
from src.aws.minio_client import MinioClient
import requests
import os
from io import BytesIO
from bson.objectid import ObjectId
from src.logger.default_logger import logger
from src.aws.storageClient_service import ClientService
def upload_image_to_s3(image_url, s3_file_name):
    # Initialize the S3 client singleton
    client_service = ClientService()
    s3_client = client_service.client_type.client
    bucket_name = client_service.client_type.bucket_name

    # Download the image
    response = requests.get(image_url)
    if response.status_code == 200:
        # Upload the image to S3
        s3_client.put_object(Bucket=bucket_name, Key=s3_file_name, Body=response.content)
        logger.info(f"\nImage successfully uploaded to S3 bucket:{bucket_name} as :{s3_file_name}")
    else:
        logger.error(f"Failed to download image from {image_url}")


def upload_huggingfaceimage_to_s3(image,s3_file_name):
    """
    Upload a PIL Image directly to S3 without saving it locally.
    """
    # Create an in-memory byte stream
    buffer = BytesIO()
    image.save(buffer, format=image.format)  # Save the image to the buffer in its original format
    buffer.seek(0)  # Reset the stream's position to the beginning

    # Initialize S3 client
    client_service = ClientService()
    s3_client = client_service.client_type.client
    bucket_name = client_service.client_type.bucket_name

    # Upload the image directly to S3 using `upload_fileobj`
    s3_client.upload_fileobj(buffer, bucket_name, s3_file_name, ExtraArgs={'ContentType': f'image/{image.format.lower()}'})

def generate_random_file_name():
    return "images/"+str(ObjectId())+".png"