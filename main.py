import requests
import os
import pytz
import logging
from datetime import datetime
from google.cloud import storage
from typing import Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def scrape_whois() -> Optional[str]:
    """
    Retrieve the public IP address using ipify API.
    
    Returns:
        Optional[str]: The public IP address if successful, None otherwise
    """
    url = "https://api.ipify.org?format=json"
    try:
        response = requests.get(url, timeout=10)  # Add timeout
        response.raise_for_status()
        ip_address = response.json()['ip']
        logger.info(f"Successfully retrieved IP address: {ip_address}")
        return ip_address
    except requests.exceptions.Timeout:
        logger.error("Request timed out while fetching IP address")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error scraping IP: {str(e)}")
        return None
    except KeyError:
        logger.error("Unexpected API response format")
        return None

def save_to_gcs(ip_address: str) -> bool:
    """
    Save IP address to Google Cloud Storage with timestamp.
    
    Args:
        ip_address (str): The IP address to save
        
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        ValueError: If BUCKET_NAME environment variable is not set
    """
    bucket_name = os.environ.get('BUCKET_NAME')
    if not bucket_name:
        raise ValueError("BUCKET_NAME environment variable not set")
    
    try:
        tz = pytz.timezone('Asia/Taipei')
        timestamp = datetime.now(tz).strftime("%Y%m%d_%H%M%S")
        
        client = storage.Client()
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(f"ip_logs/ip_{timestamp}.txt")
        
        # Format the content with additional metadata
        content = (
            f"IP Address: {ip_address}\n"
            f"Timestamp: {timestamp}\n"
            f"Timezone: Asia/Taipei"
        )
        
        blob.upload_from_string(content)
        logger.info(f"Successfully saved IP data to GCS: {blob.name}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving to GCS: {str(e)}")
        return False

def main() -> None:
    """Main function to orchestrate IP scraping and storage."""
    print("Hello World!")  # 新增的顯示
    logger.info("Hello World!")  # 同時也加入日誌記錄
    
    try:
        # Check for required environment variable
        if not os.environ.get('BUCKET_NAME'):
            logger.error("BUCKET_NAME environment variable not set")
            return
        
        ip = scrape_whois()
        if ip:
            if save_to_gcs(ip):
                logger.info("IP logging process completed successfully")
            else:
                logger.error("Failed to save IP address to GCS")
        else:
            logger.error("Failed to retrieve IP address")
            
    except Exception as e:
        logger.error(f"Unexpected error in main function: {str(e)}")

if __name__ == "__main__":
    main()

