from src.celery_service.celery_worker import celery_app
import os
from src.logger.default_logger import logger
from botocore.exceptions import NoCredentialsError
from src.aws.storageClient_service import ClientService
import pandas as pd
import json


@celery_app.task
def upload_df_embed_to_s3(data_list: list, s3_key: str):
    """
    Upload a DataFrame directly to S3 in Parquet format without a local buffer.
    :param data: List of dictionaries to be converted to DataFrame.
    :param s3_bucket_name: The name of the S3 bucket.
    :param s3_key: The key (path) in the S3 bucket.
    """
    # Convert list of dictionaries to DataFrame
 
    data_updated_list = [
    {**item, 'metadata': json.dumps(item['metadata'])} 
    for item in data_list]
    

    df = pd.DataFrame(data=data_updated_list)
   


    # Serialize the DataFrame to Parquet format in-memory

    parquet_data = df.to_parquet(index=False, engine="pyarrow")
    client_service = ClientService()
    vectors_bucket = client_service.client_type.vectors_backup

    # Upload the serialized data directly to S3
    try:
        s3_client = client_service.client_type.client
        s3_client.put_object(
            Bucket=vectors_bucket,
            Key=s3_key,
            Body=parquet_data
        )
        
        logger.info(f"DataFrame uploaded to s3://{vectors_bucket}/{s3_key} successfully.")
        return f"DataFrame uploaded to s3://{vectors_bucket}/{s3_key} successfully."
    except NoCredentialsError:
        logger.error("AWS credentials not found!")
        return "AWS credentials not found!"
    except Exception as e:
        logger.error(f"Failed to upload DataFrame: {e}")
        return f"Failed to upload DataFrame: {e}"