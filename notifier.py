import os
import logging
import requests

def send_telegram_notification(message):
    """
    Sends a message to a Telegram user or group using the Telegram HTTP API.

    It reads the bot token and chat ID from environment variables.
    """
    bot_token = "7679580588:AAHdMgZKVieTm2C7q42Wr18IbsOYohvcfR8"
    chat_id = "-4936979548"

    if not bot_token or not chat_id:
        logging.error("Telegram bot token or chat ID is not configured. Skipping notification.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logging.info("Telegram notification sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send Telegram notification: {e}")

# Send startup message when the module is run directly
if __name__ == "__main__":
    send_telegram_notification("🤖 Bot is online and ready to check flights!")