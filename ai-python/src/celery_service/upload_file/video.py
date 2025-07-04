from src.celery_service.celery_worker import celery_app
from src.aws.boto3_client import Boto3S3Client
from src.aws.localstack_client import LocalStackS3Client
from src.aws.minio_client import MinioClient
from google import genai
import os
from bson.objectid import ObjectId
import requests
from io import BytesIO
from src.crypto_hub.utils.crypto_utils import crypto_service
import requests
from io import BytesIO
from dotenv import load_dotenv
from src.celery_service.utils import get_default_header
from tempfile import SpooledTemporaryFile,NamedTemporaryFile
from pathlib import Path
import ffmpeg
import asyncio

@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 0, 'countdown': 0},queue="gemini")
def upload_gemini_video(self, url: str, encrypt_api_key: str):
    """
    Uploads a video to Gemini and returns the response.

    Args:
        url (str): The URL of the video to upload.
        api_key (str): The API key for authentication.

    Returns:
        dict: The response from the Gemini API.
    """
    try:
        # Initialize the Gemini client  
        # s3_client = LocalStackS3Client().client
        # bucket_name = os.environ.get("AWS_BUCKET", "gocustomai")
        header=get_default_header()
        api_key=crypto_service.decrypt(encrypt_api_key)
    
        with NamedTemporaryFile(mode='w+b', suffix='.mp4', delete=False) as temp_file:
            with requests.get(url, stream=True,headers=header) as response:
                response.raise_for_status()
                for chunk in response.iter_content(chunk_size=1*1024 * 1024):  # 20MB chunks
                    temp_file.write(chunk)
            
            # Rewind to the beginning for reading
            
            temp_file.flush()
            temp_file.seek(0)

            client=genai.Client(api_key=api_key)
            # video_id=ObjectId()

            # s3_file_name=f"video/{video_id}.mp4"

            file_path = Path(temp_file.name)
            probe = ffmpeg.probe(file_path)
            duration_video=float(probe["format"]['duration'])
            if duration_video<=1800:
                # Upload the file (pass the file object)
                # loop = asyncio.new_event_loop()
                # asyncio.set_event_loop(loop)

                # async def upload_to_s3():
                #     await loop.run_in_executor(None, s3_client.upload_fileobj, temp_file, bucket_name, s3_file_name)

                # loop.run_until_complete(upload_to_s3())
                response = client.files.upload(file=file_path)
                file_name=response.name
                return {"gemini_file_name":file_name,"duration":duration_video}
            else:
                return {"gemini_file_name":"","duration":duration_video}
        

    except Exception as e:
        raise RuntimeError(f"Failed to upload video to Gemini: {e}")
    finally:
        # Cleanup or additional logic can be added here
        os.remove(file_path)
        pass