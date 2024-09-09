import requests
import json
import time
# from dotenv import load_dotenv
import os
from datetime import datetime
 
def load_env(filepath='.env'):
    """Manually loads environment variables from a .env file.""" #
    if os.path.exists(filepath):
        with open(filepath) as f:
            for line in f:
                # Remove comments and strip whitespace
                line = line.strip()
                if line and not line.startswith('#'):
                    # Split the line into key-value pair
                    key, value = line.split('=', 1)
                    os.environ[key] = value.strip()

# Load environment variables from the .env file
load_env()

# Get the credentials from the .env file
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_ALERT_BOT_TOKEN = os.getenv('TELEGRAM_ALERT_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Define API endpoints
MEXC_API_URL = 'https://contract.mexc.com/api/v1/contract/funding_rate/MAK_USDT' # modify this field to change the ticker
TELEGRAM_API_URL = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
TELEGRAM_ALERT_BOT_URL = f'https://api.telegram.org/bot{TELEGRAM_ALERT_BOT_TOKEN}/sendMessage'

def get_funding_rate():
    """Fetch the funding rate for MAK_USDT from MEXC"""
    try:
        response = requests.get(MEXC_API_URL)
        data = response.json()

        if data.get('success') and 'data' in data:
            funding_data = data['data']
            symbol = funding_data.get('symbol')
            funding_rate = funding_data.get('fundingRate')
            max_funding_rate = funding_data.get('maxFundingRate')
            min_funding_rate = funding_data.get('minFundingRate')
            next_settle_time = datetime.utcfromtimestamp(funding_data.get('nextSettleTime') / 1000)

            return symbol, funding_rate, max_funding_rate, min_funding_rate, next_settle_time
        else:
            print("Error fetching funding rate:", data)
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def send_telegram_message(message):
    """Send a message to the Telegram bot"""
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    try:
        response = requests.post(TELEGRAM_API_URL, json=payload)
        if response.status_code == 200:
            print("Message sent successfully.")
        else:
            print(f"Failed to send message. Status code: {response.status_code}{response}")
    except Exception as e:
        print(f"An error occurred while sending the message: {e}")


def send_alert_telegram_message(message):
    """Send a message to the Telegram bot"""
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message
    }
    try:
        response = requests.post(TELEGRAM_ALERT_BOT_URL, json=payload)
        if response.status_code == 200:
            print("Message sent successfully.")
        else:
            print(f"Failed to send message. Status code: {response.status_code}{response}")
    except Exception as e:
        print(f"An error occurred while sending the message: {e}")

def main():
    # Get the funding rate data
    funding_data = get_funding_rate()

    if funding_data:
        symbol, funding_rate, max_funding_rate, min_funding_rate, next_settle_time = funding_data

        # Prepare the message
        message = (
            f"Symbol: {symbol}\n"
            f"Funding Rate: {funding_rate:.6f}\n"
            f"Max Funding Rate: {max_funding_rate:.6f}\n"
            f"Min Funding Rate: {min_funding_rate:.6f}\n"
            f"Next Settlement Time (UTC): {next_settle_time}"
        )
        # print(message)
        # Send the message to Telegram
        send_telegram_message(message)

        if min_funding_rate < -0.0002 or funding_rate < -0.0002:
            send_alert_telegram_message(message)

# Schedule the script to run periodically (e.g., every 1 hour)
if __name__ == '__main__':
    while True:
        main()
        time.sleep(60)  # Wait for 1 hour before running the script again
