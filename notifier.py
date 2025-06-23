import os
import logging
import telegram

def send_telegram_notification(message):
    """
    Sends a message to a Telegram user or group.
    
    It reads the bot token and chat ID from environment variables.
    """
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        logging.error("Telegram bot token or chat ID is not configured. Skipping notification.")
        return

    try:
        bot = telegram.Bot(token=bot_token)
        bot.send_message(chat_id=chat_id, text=message, parse_mode=telegram.ParseMode.MARKDOWN)
        logging.info("Telegram notification sent successfully.")
    except Exception as e:
        logging.error(f"Failed to send Telegram notification: {e}") 