import schedule
import time
import logging
from dotenv import load_dotenv

import api_client
import database
import notifier
#from currency_converter import get_eur_to_usd_rate, convert_eur_to_usd
from config import PRICE_THRESHOLD_EUR, ONE_WAY_THRESHOLD_EUR, SPECIFIC_THRESHOLD_EUR

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

    # 1. Fetch all flight prices (round trip, one-way, and specific date range)
    deals = api_client.fetch_all_flights()
    
    if not deals:
        logging.info("No flight deals found in this run.")
        return

    # 2. Process and save deals
    for deal in deals:
        # Skip saving if this deal already exists
        if database.flight_price_exists(
            deal['outbound_date'],
            deal['return_date'] or 'ONE_WAY',
            deal['price']
        ):
            continue

        # Save every found deal to the database
        database.save_flight_price(
            deal['outbound_date'],
            deal['return_date'] or 'ONE_WAY',
            deal['price'],
            deal['currency']
        )

        # 3. Check for deals below the threshold in EUR
        if deal['currency'] == 'EUR':
            if deal['type'] == 'one_way' and deal['price'] < ONE_WAY_THRESHOLD_EUR:
                logging.info(f"Found a cheap one-way flight! Price: €{deal['price']:.2f}")
                # Format the message for one-way flights
                booking_url = f"https://www.flylevel.com/Flight/Select?culture=es-ES&triptype=OW&o1={api_client.ONE_WAY_ORIGIN}&d1={api_client.ONE_WAY_DESTINATION}&dd1={deal['outbound_date']}&ADT=1&CHD=0&INL=0&forcedCurrency=EUR&forcedCulture=es-ES&newecom=true&currency=EUR"

                message = (
                    f"✈️ *¡Vuelo de IDA barato encontrado!*\n\n"
                    f"*Ruta:* {api_client.ONE_WAY_ORIGIN} ➔ {api_client.ONE_WAY_DESTINATION} (Buenos Aires)\n"
                    f"*Fecha:* {deal['outbound_date']}\n"
                    f"*Precio:* *{deal['price']} EUR*\n\n"
                    f"[¡Reserva ahora!]({booking_url})"
                )
                # Send notification
                notifier.send_telegram_notification(message)
                
            elif deal['type'] == 'round_trip' and deal['price'] < PRICE_THRESHOLD_EUR:
                logging.info(f"Found a cheap round trip flight! Price: €{deal['price']:.2f}")
                # Format the message for round trip flights
                booking_url = f"https://www.flylevel.com/Flight/Select?culture=es-ES&triptype=RT&o1={api_client.ORIGIN}&d1={api_client.DESTINATION}&dd1={deal['outbound_date']}&ADT=1&CHD=0&INL=0&r=true&mm=true&dd2={deal['return_date']}&forcedCurrency=EUR&forcedCulture=es-ES&newecom=true&currency=EUR"

                message = (
                    f"✈️ *¡Vuelo redondo barato encontrado!*\n\n"
                    f"*Ruta:* {api_client.ORIGIN} ➔ {api_client.DESTINATION}\n"
                    f"*Salida:* {deal['outbound_date']}\n"
                    f"*Regreso:* {deal['return_date']}\n"
                    f"*Precio:* *{deal['price']} EUR*\n\n"
                    f"[¡Reserva ahora!]({booking_url})"
                )
                # Send notification
                notifier.send_telegram_notification(message)
                
            elif deal['type'] == 'specific_range' and deal['price'] < SPECIFIC_THRESHOLD_EUR:
                logging.info(f"Found a cheap specific range flight! Price: €{deal['price']:.2f}")
                # Format the message for specific date range flights
                booking_url = f"https://www.flylevel.com/Flight/Select?culture=es-ES&triptype=RT&o1={api_client.SPECIFIC_ORIGIN}&d1={api_client.SPECIFIC_DESTINATION}&dd1={deal['outbound_date']}&ADT=1&CHD=0&INL=0&r=true&mm=true&dd2={deal['return_date']}&forcedCurrency=EUR&forcedCulture=es-ES&newecom=true&currency=EUR"

                message = (
                    f"🎯 *¡Vuelo específico barato encontrado!*\n\n"
                    f"*Ruta:* {api_client.SPECIFIC_ORIGIN} ➔ {api_client.SPECIFIC_DESTINATION}\n"
                    f"*Salida:* {deal['outbound_date']}\n"
                    f"*Regreso:* {deal['return_date']}\n"
                    f"*Duración:* {deal['duration_days']} días\n"
                    f"*Precio:* *{deal['price']} EUR*\n\n"
                    f"[¡Reserva ahora!]({booking_url})"
                )
                # Send notification
                notifier.send_telegram_notification(message)
                
            elif deal['type'] == 'aerolineas_argentinas' and deal['price'] < deal.get('threshold', SPECIFIC_THRESHOLD_EUR):
                logging.info(f"Found a cheap Aerolíneas Argentinas flight! Price: €{deal['price']:.2f}")
                # Format the message for Aerolíneas Argentinas flights
                # Create booking URL for Aerolíneas Argentinas
                outbound_date_formatted = deal['outbound_date'].replace('-', '')
                return_date_formatted = deal['return_date'].replace('-', '')
                origin = deal.get('origin', 'MAD')
                destination = deal.get('destination', 'COR')
                booking_url = f"https://www.aerolineas.com.ar/es-ar/vuelos/buscar?adt=1&inf=0&chd=0&flexDates=true&cabinClass=Economy&flightType=ROUND_TRIP&leg={origin}-{destination}-{outbound_date_formatted}&leg={destination}-{origin}-{return_date_formatted}"

                message = (
                    f"🇦🇷 *¡Vuelo Aerolíneas Argentinas barato encontrado!*\n\n"
                    f"*Aerolínea:* {deal.get('airline', 'Aerolíneas Argentinas')}\n"
                    f"*Ruta:* {deal.get('route', f'{origin} ➔ {destination}')}\n"
                    f"*Salida:* {deal['outbound_date']}\n"
                    f"*Regreso:* {deal['return_date']}\n"
                    f"*Duración:* {deal['duration_days']} días\n"
                    f"*Precio:* *{deal['price']} EUR*\n\n"
                    f"[¡Reserva ahora!]({booking_url})"
                )
                # Send notification
                notifier.send_telegram_notification(message)

            elif deal['type'] == 'aireuropa' and deal['price'] < deal.get('threshold', SPECIFIC_THRESHOLD_EUR):
                logging.info(f"Found a cheap AirEuropa flight! Price: €{deal['price']:.2f}")
                # Format the message for AirEuropa flights
                # Create booking URL for AirEuropa
                origin = deal.get('origin', 'MAD')
                destination = deal.get('destination', 'COR')
                booking_url = f"https://digital.aireuropa.com/es/vuelos/buscar?origin={origin}&destination={destination}&departureDate={deal['outbound_date']}&returnDate={deal['return_date']}&adults=1&children=0&infants=0&cabinClass=economy&fareFamily=DIGITAL1"

                message = (
                    f"✈️ *¡Vuelo AirEuropa barato encontrado!*\n\n"
                    f"*Aerolínea:* {deal.get('airline', 'AirEuropa')}\n"
                    f"*Ruta:* {deal.get('route', f'{origin} ➔ {destination}')}\n"
                    f"*Salida:* {deal['outbound_date']}\n"
                    f"*Regreso:* {deal['return_date']}\n"
                    f"*Duración:* {deal['duration_days']} días\n"
                    f"*Precio:* *{deal['price']} EUR*\n\n"
                    f"[¡Reserva ahora!]({booking_url})"
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
    
    # Schedule the job to run every 15 minutes
    schedule.every(15).minutes.do(check_flights_and_notify)
    
    logging.info("Scheduler started. Will run every 15 minutes.")

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main() 