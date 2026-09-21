import os
import requests
from dotenv import load_dotenv, find_dotenv
import datetime
import json
import boto3
from botocore.exceptions import BotoCoreError, ClientError

# Load environment variables from .env file (works in both local and Docker environments)
load_dotenv(find_dotenv())

def main_outh():
    def outh():
        now = datetime.datetime.now()
        formatted = now.strftime("%d/%m/%Y %I:%M:%S %p")
        # Establish connection
        authorization = os.getenv("Authorization_Header")
        url = f"https://api.onegov.nsw.gov.au/oauth/client_credential/accesstoken"

        params = {
                "grant_type": 'client_credentials'
            }

        headers = {
                        "Accept":"application/json",
                        "Authorization": 'Basic eVBjU3BDRkU0R2pIaVhCdndBTG5BT2hVdzRvMDVPWjA6TXNCdTRYbFlISEtPVFZWNg=='
                    }

        resp = requests.get(url, params=params, headers=headers)

        resp.raise_for_status()
        output = resp.json()
    
        session_data = {
                                "access_token": "Bearer " + output.get("access_token", ""),
                                "api_key": output.get("client_id", ""),
                                "content_type": "application/json; charset=utf-8",
                                "transactionid": "transact_id_activity-10_group-10",
                                "requesttimestamp": formatted
                            }
        json_output = json.dumps(session_data, indent=4)
        return json_output



    # Initialise s3 client with explicit AWS credentials
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

    def upload_session_to_s3(session_data_dict, bucket_name, object_name):
        try:
            # Put the object into S3
            s3_client.put_object(
                Bucket=bucket_name,
                Key=object_name,
                Body=session_data_dict,
                ContentType="application/json",
            )

            print (f"Successfully uploaded session log to s3://{bucket_name}/{object_name}")

        except (BotoCoreError, ClientError) as e:
            print (f"Failed to upload to S3: {e}")



    
    # 2nd
    BUCKET_NAME = ("nsw-fuel-pipeline-data-atharva")
        
    # 3rd
    now = datetime.datetime.now()
    formatted = now.strftime("%Y-%m-%d_%H-%M-%S")
    OBJECT_KEY = f"logs/auth_session{formatted}.json"  # The path/filename in S3

    return upload_session_to_s3(outh(), BUCKET_NAME, OBJECT_KEY)

