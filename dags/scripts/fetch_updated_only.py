import requests
import os
import json
import datetime
from botocore.exceptions import BotoCoreError, ClientError
import boto3
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file (works in both local and Docker environments)
load_dotenv(find_dotenv())

def fetch_updated_data(keys):
    if isinstance(keys, str):
        keys = json.loads(keys)  
        
    now = datetime.datetime.now()
    formatted = now.strftime("%d/%m/%Y %I:%M:%S %p")
    timestamp_file = now.strftime("%Y-%m-%d_%H-%M-%S")

    try:
        url_prices = 'https://api.onegov.nsw.gov.au/FuelPriceCheck/v1/fuel/prices/new'
        headers = {
            "accept": "application/json",
            "Authorization": keys.get("access_token"),
            "Content-Type": keys.get("content_type"),
            "apikey": keys.get("api_key"),
            "transactionid": keys.get("transactionid"),
            "requesttimestamp": formatted,
        }

        response = requests.get(url_prices, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if response.status_code == 200:
            # Extract both arrays to catch any new station metadata alongside prices
            stations_list = data.get('stations', [])
            prices_list = data.get('prices', [])
            
            if prices_list or stations_list:
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
                upload_messages = []

                # Convert and upload incremental stations if any exist
                if stations_list:
                    stations_ndjson = "\n".join(json.dumps(station) for station in stations_list)
                    stations_key = f"raw/stations_incremental/updated_stations_{timestamp_file}.json"
                    
                    s3_client.put_object(
                        Bucket=BUCKET_NAME, 
                        Key=stations_key, 
                        Body=stations_ndjson, 
                        ContentType="application/json"
                    )
                    upload_messages.append(f"Stations -> s3://{BUCKET_NAME}/{stations_key}")

                # Convert and upload incremental prices if any exist
                if prices_list:
                    prices_ndjson = "\n".join(json.dumps(price) for price in prices_list)
                    prices_key = f"raw/prices_incremental/updated_prices_{timestamp_file}.json"
                    
                    s3_client.put_object(
                        Bucket=BUCKET_NAME, 
                        Key=prices_key, 
                        Body=prices_ndjson, 
                        ContentType="application/json"
                    )
                    upload_messages.append(f"Prices -> s3://{BUCKET_NAME}/{prices_key}")

                return "Successfully uploaded: " + " | ".join(upload_messages)
            else:
                return "No new data received from API."
        else:
            return f"Failed to fetch data. Status code: {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"