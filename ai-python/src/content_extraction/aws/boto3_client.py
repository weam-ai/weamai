import boto3
import os
from botocore.config import Config
from src.content_extraction.config import AWSConfig
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Boto3S3Client(metaclass=Singleton):
    def __init__(self):
        # Read AWS credentials from environment variables
        aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')

        config = Config(
            retries={
            'total_max_attempts': AWSConfig.MAX_ATTEMPTS,
            'mode': AWSConfig.MODE  # Uses the standardized retry rules
            }, 
            connect_timeout=AWSConfig.CONNECT_TIMEOUT,   # Connection timeout in seconds
            read_timeout=AWSConfig.READ_TIMEOUT,       # Read timeout in seconds
            # Retry configuration
        )

        # Initialize the S3 client with the specified config
        self.client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            config=config
        )

        # Initialize the S3 client
        self.client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            
        )
