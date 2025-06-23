import requests
import logging
from config import API_BASE_URL, ORIGIN, DESTINATION, CURRENCY, SEARCH_DATES, BASE_HEADERS

def fetch_flight_prices():
    """
    Fetches flight prices from the LEVEL API for the configured dates.

    Returns:
        A list of flight deals, where each deal is a dictionary.
        Example: [{'outbound_date': '2025-12-10', 'return_date': '2026-04-15', 'price': 240.5, 'currency': 'EUR'}]
        Returns an empty list if there's an error.
    """
    all_deals = []
    for outbound_year, outbound_month, return_year, return_month in SEARCH_DATES:
        
        outbound_date_str = f"{outbound_year}-{outbound_month:02d}-01"
        
        params = {
            'triptype': 'RT',
            'origin': ORIGIN,
            'destination': DESTINATION,
            'outboundDate': outbound_date_str,
            'month': outbound_month,
            'year': outbound_year,
            'currencyCode': CURRENCY
        }

        # Dynamically create the Referer URL
        referer_url = (
            f"https://www.flylevel.com/Flight/Select?culture=es-ES&triptype=RT&o1={ORIGIN}"
            f"&d1={DESTINATION}&dd1={outbound_year}-{outbound_month:02d}&ADT=1&CHD=0&INL=0&r=true&mm=true"
            f"&dd2={return_year}-{return_month:02d}&forcedCurrency={CURRENCY}&forcedCulture=es-ES"
            "&newecom=true"
        )
        
        headers = BASE_HEADERS.copy()
        headers['Referer'] = referer_url

        try:
            logging.info(f"Fetching flights for outbound: {outbound_year}-{outbound_month}, return: {return_year}-{return_month}")
            response = requests.get(API_BASE_URL, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            logging.debug(f"API Response: {data}")

            # Here we need to parse the response.
            # This is a hypothetical structure based on observing typical flight APIs.
            # It assumes the API returns a structure with available dates and prices.
            if data and data.get('days'):
                for day_info in data['days']:
                    if day_info.get('price'):
                        # We need to construct the full outbound and return dates.
                        # The API only gives us day of the month for the outbound trip.
                        # The return date is not in the calendar response, this is a limitation.
                        # We will assume a fixed return date for now for demonstration,
                        # as the API structure for RT is not fully known.
                        outbound_day = day_info.get('dayNumber')
                        if not outbound_day: continue

                        full_outbound_date = f"{outbound_year}-{outbound_month:02d}-{outbound_day:02d}"
                        
                        # HYPOTHETICAL: The API for a calendar view on a round trip
                        # might not return the full return date for each outbound day's price.
                        # This is a significant unknown.
                        # We will create a placeholder return date. A real implementation
                        # would require deeper API analysis.
                        placeholder_return_date = f"{return_year}-{return_month:02d}-15"

                        deal = {
                            "outbound_date": full_outbound_date,
                            "return_date": placeholder_return_date, # This is a placeholder
                            "price": day_info['price']['amount'],
                            "currency": CURRENCY
                        }
                        all_deals.append(deal)

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching flight data: {e}")
        except ValueError: # Catches JSON decoding errors
            logging.error(f"Error parsing JSON from response. Response text: {response.text}")
            
    return all_deals 