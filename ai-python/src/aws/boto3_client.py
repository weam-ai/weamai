import boto3
import os
from botocore.config import Config
from src.logger.default_logger import logger
from src.aws.config import Boto3AWSClientConfig
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


class Boto3S3Client(metaclass=Singleton):
    def __init__(self,result:dict=None):
        # Read AWS credentials from environment variables
        self.aws_access_key_id = os.environ.get('AWS_S3_ACCESS_KEY')
        self.aws_secret_access_key = os.environ.get('AWS_SECRET_KEY')
        self.bucket_name = os.environ.get("AWS_BUCKET")
        self.cdn_url=os.environ.get("AWS_S3_URL")
        self.vectors_backup =os.environ.get("AWS_VECTORS_BACKUP","vectors-backup")
        self.profiler = os.environ.get("PROFILER_S3_BUCKET", "profiler")
        config = Config(
            retries={
            'total_max_attempts': 5,
            'mode': 'standard'  # Uses the standardized retry rules
            }, 
            connect_timeout=120,   # Connection timeout in seconds
            read_timeout=600,       # Read timeout in seconds
            # Retry configuration
        )

        # Initialize the S3 client with the specified config
        self.client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            config=config
        )

        # Initialize the S3 client
        self.client = boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            
        )

class Boto3AWSClient(metaclass=Singleton):
    def __init__(self):
        self.aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.region_name = os.getenv("AWS_REGION", "us-east-1")  # Default to 'us-east-1'

        # Configuration for retries and timeouts
        self.config = Config(
            retries={'total_max_attempts': 5, 'mode': 'standard'},
            connect_timeout=120,
            read_timeout=600)
        
        self.clients = {}

    def get_client(self, service_name: str):
        """Get or create a boto3 client for the specified service."""
        try:
            # Return cached client if exists
            if service_name in self.clients:
                return self.clients[service_name]

            # Create and cache a new client
            self.clients[service_name] = boto3.client(
                service_name,
                region_name=self.region_name,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
                config=self.config
            )
            return self.clients[service_name]
        except Exception as e:
            logger.error(f"Error creating boto3 client for {service_name}: {e}")
            return None  # Return None if client creation fails

    def send_metric_to_cloudwatch(self, count: int):
        """Send API count metric to CloudWatch."""
        try:
            stack_name = os.getenv("STACK_NAME", "CommonStack")
            current_environment = os.getenv("WEAM_ENVIRONMENT", "dev")
            dimension_value = f"{current_environment}-openai-store-vector"

            cloudwatch_client = self.get_client(Boto3AWSClientConfig.CLOUDWATCH)

            if not cloudwatch_client:
                logger.error("CloudWatch client is unavailable.")
                return False
            
            response = cloudwatch_client.put_metric_data(
                Namespace=Boto3AWSClientConfig.CLOUDWATCH_NAMESPACE,
                MetricData=[
                    {
                        'MetricName': Boto3AWSClientConfig.CLOUDWATCH_METRIC_NAME,
                        'Dimensions': [
                            {
                                'Name': stack_name, 
                                'Value': dimension_value
                            }
                        ],
                        'Value': count,
                        'Unit': Boto3AWSClientConfig.CLOUDWATCH_UNIT,
                    },
                ]
            )
            logger.info(f"Sent API call count to CloudWatch: {count}, Status: {response['ResponseMetadata']['HTTPStatusCode']}")
            return True
        except Exception as e:
            logger.error(f"Failed to send API count to CloudWatch: {e}")
            return False