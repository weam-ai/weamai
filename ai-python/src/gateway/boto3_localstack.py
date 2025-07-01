import boto3
import os
from src.aws.storageClient_service import ClientService

def upload_file_to_s3():
    client_service = ClientService()
    bucket_name = client_service.client_type.bucket_name
    client = client_service.client_type.client

    # Upload the file

    object_key = "documents/6846741b1dcc393f790d5e49.pdf"
    with open("./src/gateway/6846741b1dcc393f790d5e49.pdf", "rb") as file_data:
        s3_client=client
        s3_client.put_object(
            Bucket=bucket_name,
            Key=object_key,
            Body=file_data,
            ContentType="application/pdf"  # Optional
        )

    # object_key = "images/674e918166b4c1afa0db7ba8.png"
    # with open("./src/gateway/674e918166b4c1afa0db7ba8.png", "rb") as file_data:
    #     s3_client=MinioClient().client
    #     s3_client.put_object(
    #         Bucket=bucket_name,
    #         Key=object_key,
    #         Body=file_data,
    #         ContentType="image/png"  # Correct MIME type for PNG images
    #     )
    
    # object_key = "images/6745b3767a839dd1b62bd6c6.png"
    # with open("./src/gateway/6745b3767a839dd1b62bd6c6.png", "rb") as file_data:
    #     s3_client=MinioClient().client
    #     s3_client.put_object(
    #         Bucket=bucket_name,
    #         Key=object_key,
    #         Body=file_data,
    #         ContentType="image/png"  # Correct MIME type for PNG images
    #     )