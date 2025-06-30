from src.celery_worker_hub.import_worker.celery_app import celery_app
from fastapi import HTTPException, status
from src.logger.default_logger import logger
from src.aws.boto3_client import Boto3S3Client
from src.aws.localstack_client import LocalStackS3Client
from src.aws.minio_client import MinioClient
import zipfile
from io import BytesIO
import os
from dotenv import load_dotenv
from src.aws.storageClient_service import ClientService
load_dotenv()
client_service = ClientService()

@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 1, 'countdown': 0},
    queue="upload_stream_to_s3"
)
def upload_stream_to_s3(self,file_content,s3_bucket,s3_key):
    """Uploads a file-like object to an S3 bucket."""
    try:
        s3_client = client_service.client_type.client
        s3_client.put_object(Bucket=client_service.client_type.bucket_name, Key=s3_key, Body=file_content)
        logger.info(f"Successfully uploaded to s3://{s3_bucket}/{s3_key}")
    except Exception as e:
        logger.error(
            f"Error executing Uploading the file: {e}",
            extra={"tags": {"task_function": "upload_stream_to_s3"}}
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@celery_app.task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={'max_retries': 2, 'countdown': 0},
    queue="upload_zip_file"
)
def zip_process_and_upload_files(self,zip_file_bytes,import_id):  
    bucket_name = client_service.client_type.bucket_name
    try:
        s3_folder = "importdata"
        file_list = []
        with zipfile.ZipFile(BytesIO(zip_file_bytes), 'r') as zip_ref:
            file_list = zip_ref.namelist()
            for file_name in file_list:
                with zip_ref.open(file_name) as file:
                    file_content = file.read()
                    base_file_name = os.path.basename(file_name)
                    if base_file_name != "":
                        s3_key = f"{s3_folder}/{import_id}/{base_file_name}"
                        upload_stream_to_s3.apply_async(args=[file_content, bucket_name, s3_key])
        logger.info(f"Successfully processed ZIP file for import_id={import_id}, files: {file_list}")
    except Exception as e:
        logger.error(
            f"Error executing processing and Uploading the zip file: {e}",
            extra={"tags": {"task_function": "upload_zip_file"}}
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))