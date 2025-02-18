import requests
import os
import pytz
from datetime import datetime
from google.cloud import storage

def scrape_whois():
    url = "https://api.ipify.org?format=json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['ip']
    except Exception as e:
        print(f"Error scraping IP: {str(e)}")
        return None

def save_to_gcs(ip_address):
    bucket_name = os.environ.get('BUCKET_NAME')
    if not bucket_name:
        raise ValueError("BUCKET_NAME environment variable not set")

    tz = pytz.timezone('Asia/Taipei')
    timestamp = datetime.now(tz).strftime("%Y%m%d_%H%M%S")

    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(f"ip_logs/ip_{timestamp}.txt")
    blob.upload_from_string(f"IP Address: {ip_address}\nTimestamp: {timestamp}")

def main():
    ip = scrape_whois()
    if ip:
        save_to_gcs(ip)
        print(f"Successfully logged IP: {ip}")

if __name__ == "__main__":
    main()
