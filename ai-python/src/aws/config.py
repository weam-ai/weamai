class ServiceConfig:
    CLOUDWATCH = "cloudwatch"
    S3 = "s3"

class CloudWatchConfig():
    CLOUDWATCH_NAMESPACE = "PythonGateway"
    CLOUDWATCH_METRIC_NAME = "API_Call_Count"
    CLOUDWATCH_UNIT = "Count"

class Boto3AWSClientConfig(ServiceConfig,CloudWatchConfig):
    pass