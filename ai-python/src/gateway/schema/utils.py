import re
import os
def validate_id_field(value: str, field_name: str) -> str:
    if value == "": 
        raise ValueError(f'{field_name.replace("_", " ").capitalize()} must not be blank.')
    if not isinstance(value, str):
        raise ValueError(f'{field_name.replace("_", " ").capitalize()} must be a string.')
    if not re.match(r'^[0-9a-fA-F]{24}$', value):
        raise ValueError(f'{field_name.replace("_", " ").capitalize()} must be a 24-character hexadecimal string.')
    return value

# ✅ Set once per app run — globally
BUCKET_TYPE_MAP = {
    "LOCALSTACK": "localstack",  # Localstack is used for local development
    "AWS_S3": "s3_url",
    "MINIO": "minio",  # Minio is used for local development
                              # S3 is used for production
}

IMAGE_SOURCE_BUCKET = BUCKET_TYPE_MAP.get(os.environ.get("BUCKET_TYPE"))
FILE_SOURCE_BUCKET = BUCKET_TYPE_MAP.get(os.environ.get("BUCKET_TYPE"))
