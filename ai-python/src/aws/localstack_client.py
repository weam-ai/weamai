import boto3
import os
from botocore.config import Config
from src.logger.default_logger import logger
from src.crypto_hub.utils.crypto_utils import MessageDecryptor,MessageEncryptor
key = os.getenv("SECURITY_KEY").encode("utf-8")

encryptor = MessageEncryptor(key)
decryptor = MessageDecryptor(key)
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class LocalStackS3Client(metaclass=Singleton):
    def __init__(self,result):
        self.aws_access_key_id = os.environ.get('LSTACK_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.environ.get('LSTACK_SECRET_ACCESS_KEY')
        self.endpoint_url = os.environ.get('LSTACK_CDN_URL')  # LocalStack endpoint
        self.bucket_name = os.environ.get("LSTACK_BUCKET")
        self.cdn_url=os.environ.get("LSTACK_CDN_URL")
        self.vectors_backup = os.environ.get("LSTACK_VECTORS_BACKUP","vectors-backup")
        self.profiler = os.environ.get("LSTACK_PROFILER","profiler")

        if not self.endpoint_url:
            raise ValueError("LocalStack endpoint URL (AWS_CDN_URL) not set in environment variables")

        config = Config(
            retries={
                'total_max_attempts': 5,
                'mode': 'standard'
            },
            connect_timeout=120,
            read_timeout=600,
        )

        logger.info(f"Using LocalStack S3 endpoint: {self.endpoint_url}")

        self.client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            endpoint_url=self.endpoint_url,
            config=config
        )
