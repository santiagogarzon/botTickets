import schedule
import time
import logging
from dotenv import load_dotenv

import api_client
import database
import notifier
import currency_converter
from config import PRICE_THRESHOLD_USD

# Load environment variables from .env file
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_flights_and_notify():
    """
    Main job function to be scheduled.
    It fetches flights, saves them, and sends notifications for cheap deals.
    """
    logging.info("Starting flight check job...")
    
    # 1. Get currency conversion rate
    eur_to_usd_rate = currency_converter.get_eur_to_usd_rate()
    logging.info(f"Using EUR to USD conversion rate: {eur_to_usd_rate}")

    # 2. Fetch flight prices
    deals = api_client.fetch_flight_prices()
    
    if not deals:
        logging.info("No flight deals found in this run.")
        return

    # 3. Process and save deals
    for deal in deals:
        # Save every found deal to the database
        database.save_flight_price(
            deal['outbound_date'],
            deal['return_date'],
            deal['price'],
            deal['currency']
        )

        # 4. Check for deals below the threshold
        if deal['currency'] == 'EUR':
            price_usd = currency_converter.convert_eur_to_usd(deal['price'], eur_to_usd_rate)
            
            if price_usd < PRICE_THRESHOLD_USD:
                logging.info(f"Found a cheap flight! Price: ${price_usd:.2f}")
                # Format the message for Telegram
                message = (
                    f"✈️ *¡Vuelo barato encontrado!*\n\n"
                    f"*Ruta:* {api_client.ORIGIN} ➔ {api_client.DESTINATION}\n"
                    f"*Salida:* {deal['outbound_date']}\n"
                    f"*Regreso:* {deal['return_date']} (placeholder)\n"
                    f"*Precio:* *{deal['price']} {deal['currency']}* (${price_usd:.2f} USD)\n\n"
                    f"¡Reserva ahora!"
                )
                # Send notification
                notifier.send_telegram_notification(message)

    logging.info("Flight check job finished.")


def main():
    """Main function to initialize and run the scheduler."""
    logging.info("Application starting...")
    # Initialize the database
    database.init_db()

    # Run the job immediately at startup
    check_flights_and_notify()
    
    # Schedule the job to run every 2 minutes
    schedule.every(2).minutes.do(check_flights_and_notify)
    
    logging.info("Scheduler started. Will run every 2 minutes.")

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main() 