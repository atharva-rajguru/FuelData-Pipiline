import json
import os
from pathlib import Path

import boto3
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parents[2] / ".env")

def fetch_latest_session_from_s3():
    aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
    aws_region = os.getenv("AWS_DEFAULT_REGION", "ap-southeast-2")

    if not aws_access_key_id or not aws_secret_access_key:
        raise RuntimeError("AWS credentials were not found in the project .env file")

    s3_client = boto3.client(
        "s3",
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=aws_secret_access_key,
        region_name=aws_region,
    )
    BUCKET_NAME = "nsw-fuel-pipeline-data-atharva"

    # 1. List all objects under the logs/ prefix
    response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix="logs/")

    if "Contents" in response:
        # 2. Sort the files by their last modified timestamp (newest first)
        sorted_files = sorted(response["Contents"], key=lambda x: x["LastModified"], reverse=True)

        # 3. Pick the latest file key
        latest_object_key = sorted_files[0]["Key"]
        if latest_object_key.endswith(".json"):
            OBJECT_KEY = latest_object_key
            try:
                # Fetch the object from S3
                response = s3_client.get_object(Bucket=BUCKET_NAME, Key=OBJECT_KEY)

                # Read the body content and decode it from bytes to a string
                file_content = response["Body"].read().decode("utf-8")

                # Parse it back into a Python dictionary (or print it as a raw string)
                json_data = json.loads(file_content)
                return (json.dumps(json_data, indent=4))

            except Exception as e:
                return (f"Error reading file from S3: {e}")
            
    else:
        return("No log files found in the bucket.")


    
    
