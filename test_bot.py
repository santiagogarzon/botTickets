#!/usr/bin/env python3
"""
Quick test script to verify Telegram bot is working
"""
import os
import telegram
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_telegram_bot():
    """Test if the Telegram bot can send messages"""
    
    # Get credentials from environment
    bot_token = "7679580588:AAHdMgZKVieTm2C7q42Wr18IbsOYohvcfR8"
    # Use group chat ID for testing
    chat_id = "-4936979548"  # Group chat ID
    
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN not found in environment variables")
        return False
    
    print(f"🤖 Testing bot with token: {bot_token[:10]}...")
    print(f"👥 Group Chat ID: {chat_id}")
    
    try:
        # Create bot instance
        bot = telegram.Bot(token=bot_token)
        
        # Send test message
        test_message = (
            "🧪 Bot Test Successful!\n\n"
            "✅ Your bot is working correctly\n"
            "✅ Can send messages to the group\n"
            "✅ Ready to receive flight notifications\n\n"
            "The flight monitoring bot will start sending updates soon!"
        )
        
        bot.send_message(
            chat_id=chat_id, 
            text=test_message
        )
        
        print("✅ Test message sent successfully!")
        print("📱 Check your Telegram group for the test message")
        return True
        
    except Exception as e:
        print(f"❌ Error sending test message: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing Telegram Bot...")
    success = test_telegram_bot()
    
    if success:
        print("\n🎉 Bot test completed successfully!")
        print("Your bot is ready to receive flight notifications.")
    else:
        print("\n💥 Bot test failed!")
        print("Please check your TELEGRAM_BOT_TOKEN")