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
from urllib.parse import urlparse

def get_extension_from_content_type(content_type):
    mapping = {
        "audio/mpeg": ".mp3",
        "audio/mp4": ".m4a",
        "audio/x-m4a": ".m4a",
        "audio/wav": ".wav"
    }
    return mapping.get(content_type, ".bin") 

@celery_app.task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 0, 'countdown': 0}, queue="gemini")
def upload_gemini_audio(self, url: str, encrypt_api_key: str):
    """
    Uploads an audio file to Gemini and returns the response.

    Args:
        url (str): The URL of the audio file to upload.
        encrypt_api_key (str): The encrypted API key for authentication.

    Returns:
        dict: The response from the Gemini API.
    """
    try:
        header = get_default_header()
        api_key = crypto_service.decrypt(encrypt_api_key)

        with requests.get(url, stream=True, headers=header) as response:
            response.raise_for_status()
            ext = get_extension_from_content_type(response.headers.get('Content-Type'))
            with NamedTemporaryFile(mode='w+b', suffix=ext, delete=False) as temp_file:
                for chunk in response.iter_content(chunk_size=1 * 1024 * 1024):
                    temp_file.write(chunk)

                temp_file.flush()
                temp_file.seek(0)

                client = genai.Client(api_key=api_key)
                file_path = Path(temp_file.name)
                probe = ffmpeg.probe(file_path)
                duration_audio = float(probe["format"]['duration'])

                if duration_audio <= 5400:  # 30 minutes
                    response = client.files.upload(file=file_path)
                    file_name = response.name
                    return {"gemini_file_name": file_name, "duration": duration_audio}
                else:
                    return {"gemini_file_name":"","duration":duration_audio}


    except Exception as e:
        raise RuntimeError(f"Failed to upload audio to Gemini: {e}")
    finally:
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)