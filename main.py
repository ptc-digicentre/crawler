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
    Save IP address to Google Cloud Storage with timestamp as HTML file.
    
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
        
        # 创建HTML内容
        html_content = f"""
        <html>
        <head>
            <title>IP Information</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    padding: 20px;
                    background-color: #f0f0f0;
                }}
                .container {{
                    background-color: white;
                    padding: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    max-width: 600px;
                    margin: 0 auto;
                }}
                h1 {{
                    color: #333;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .info {{
                    margin: 10px 0;
                    padding: 10px;
                    border-bottom: 1px solid #eee;
                }}
                .info:last-child {{
                    border-bottom: none;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Hello World!</h1>
                <div class="info">IP Address: {ip_address}</div>
                <div class="info">Timestamp: {timestamp}</div>
                <div class="info">Timezone: Asia/Taipei</div>
            </div>
        </body>
        </html>
        """
        
        # 只保存HTML版本
        html_blob = bucket.blob(f"ip_logs/ip_{timestamp}.html")
        html_blob.upload_from_string(html_content, content_type='text/html')
        
        logger.info(f"Successfully saved IP data to GCS: {html_blob.name}")
        return True
        
    except Exception as e:
        logger.error(f"Error saving to GCS: {str(e)}")
        return False

def main() -> None:
    """Main function to orchestrate IP scraping and storage."""
    print("Hello World!")  # 控制台显示
    logger.info("Hello World!")  # 日志记录
    
    try:
        # Check for required environment variable
        if not bucket_name:
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

