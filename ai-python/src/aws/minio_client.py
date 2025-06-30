import os
from fastapi.responses import FileResponse
from botocore.client import Config
import boto3
from src.logger.default_logger import logger
from src.crypto_hub.utils.crypto_utils import MessageDecryptor,MessageEncryptor
key = os.getenv("SECURITY_KEY").encode("utf-8")

encryptor = MessageEncryptor(key)
decryptor = MessageDecryptor(key)
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            logger.info(f"🌀 Creating singleton instance for {cls.__name__}")
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class MinioClient(metaclass=Singleton):
    def __init__(self,result:dict=None):
        self.endpoint = os.environ.get("MINIO_ENDPOINT", "minio:9000")
        self.region = os.environ.get("AWS_REGION", "us-east-1")
        self.access_key = os.environ.get("AWS_ACCESS_KEY_ID", "minioadmin")
        self.secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY", "minioadmin123")
        self.bucket_name = os.environ.get("AWS_S3_BUCKET")
        self.cdn_url=os.environ.get("MINIO_ENDPOINT")
        self.vectors_backup =os.environ.get("MINIO_VECTORS_BACKUP","vectors-backup")
        self.profiler = os.environ.get("PROFILER_S3_BUCKET", "profiler")
        logger.info("🔐 Initializing MinIO S3 client")
        self.client = boto3.client(
            "s3",
            endpoint_url=f"{self.endpoint}",
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
            config=Config(signature_version="s3v4"),
        )

        # self._ensure_bucket_exists()

    def _ensure_bucket_exists(self):
        try:
            logger.info(f"📁 Ensuring bucket '{self.bucket_name}' exists...")
            buckets = self.s3.list_buckets()
            if not any(b["Name"] == self.bucket_name for b in buckets["Buckets"]):
                logger.info(f"🪣 Bucket '{self.bucket_name}' not found. Creating...")
                self.s3.create_bucket(Bucket=self.bucket_name)
            else:
                logger.info(f"✅ Bucket '{self.bucket_name}' already exists.")
        except Exception as e:
            logger.error(f"❌ Failed to ensure bucket exists: {e}")
