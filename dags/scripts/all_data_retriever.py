import requests
import os
import json
import datetime
from botocore.exceptions import BotoCoreError, ClientError
import boto3
from dotenv import load_dotenv, find_dotenv

# Load environment variables from .env file (works in both local and Docker environments)
load_dotenv(find_dotenv())

def fetch_all_stations(keys):
    if isinstance(keys, str):
        keys = json.loads(keys)  # Convert the JSON string to a Python dictionary
        
    now = datetime.datetime.now()
    formatted = now.strftime("%d/%m/%Y %I:%M:%S %p")
    timestamp_file = now.strftime("%Y-%m-%d_%H-%M-%S")

    try:
        url_prices = 'https://api.onegov.nsw.gov.au/FuelPriceCheck/v1/fuel/prices'
        headers = {
                "accept": "application/json",
                "Authorization": keys.get("access_token"),
                "Content-Type": keys.get("content_type"),
                "apikey": keys.get("api_key"),
                "transactionid": keys.get("transactionid"),
                "requesttimestamp": formatted,
            }

        response2 = requests.get(url_prices, headers=headers)
        response2.raise_for_status()
        data = response2.json()
        
        if response2.status_code == 200:
            # Initialize S3 client with explicit AWS credentials
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

            # --- Save the fuel price data to S3 ---
            try:
                # Extract both the stations and prices lists from the API response dictionary
                stations_list = data.get("stations", [])
                prices_list = data.get("prices", [])

                # Convert each dictionary to its own JSON string separated by a newline (NDJSON)
                stations_ndjson = "\n".join(json.dumps(station) for station in stations_list)
                prices_ndjson = "\n".join(json.dumps(price) for price in prices_list)

                # Define separate object keys for stations and prices
                object_key_stations = f"raw/stations_full/stations_all_{timestamp_file}.json"
                object_key_prices = f"raw/prices_full/prices_all_{timestamp_file}.json"

                # Upload the stations NDJSON string to S3
                if stations_list:
                    s3_client.put_object(
                        Bucket=BUCKET_NAME, 
                        Key=object_key_stations, 
                        Body=stations_ndjson, 
                        ContentType="application/json"
                    )

                # Upload the prices NDJSON string to S3
                if prices_list:
                    s3_client.put_object(
                        Bucket=BUCKET_NAME, 
                        Key=object_key_prices, 
                        Body=prices_ndjson, 
                        ContentType="application/json"
                    )

                return (f"Successfully uploaded stations to s3://{BUCKET_NAME}/{object_key_stations} "
                        f"and prices to s3://{BUCKET_NAME}/{object_key_prices}")

            except (BotoCoreError, ClientError) as e:
                return f"AWS S3 Upload Error: {e}"
        else:
            return f"Failed to fetch fuel prices. Status code: {response2.status_code}"

    except requests.exceptions.RequestException as e:
        return f"Error fetching fuel prices: {e}"