import requests
import logging
from config import (
    API_BASE_URL, ORIGIN, DESTINATION, CURRENCY, SEARCH_DATES, BASE_HEADERS,
    ONE_WAY_ORIGIN, ONE_WAY_DESTINATION, ONE_WAY_DATES, ONE_WAY_THRESHOLD_EUR
)

def fetch_one_way_flights():
    """
    Fetches one-way flight prices from BCN to Buenos Aires for the configured dates.
    
    Returns:
        A list of one-way flight deals.
    """
    one_way_deals = []
    
    for year, month in ONE_WAY_DATES:
        logging.info(f"Fetching one-way flights BCN -> BUE for {year}-{month}")
        
        # API call for one-way flights
        params = {
            'triptype': 'OW',  # One-way
            'origin': ONE_WAY_ORIGIN,
            'destination': ONE_WAY_DESTINATION,
            'month': month,
            'year': year,
            'currencyCode': CURRENCY
        }
        
        referer = (
            f"https://www.flylevel.com/Flight/Select?o1={ONE_WAY_ORIGIN}&d1={ONE_WAY_DESTINATION}"
            f"&dd1={year}-{month:02d}&ADT=1&CHD=0&INL=0&forcedCurrency={CURRENCY}&forcedCulture=es-ES&newecom=true"
        )
        
        headers = BASE_HEADERS.copy()
        headers['Referer'] = referer
        
        try:
            response = requests.get(API_BASE_URL, params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            # Parse one-way flights
            if 'data' in data and 'dayPrices' in data['data']:
                for day_info in data['data']['dayPrices']:
                    price = day_info['price']
                    if price < ONE_WAY_THRESHOLD_EUR:
                        deal = {
                            "outbound_date": day_info['date'],
                            "return_date": None,  # One-way flight
                            "price": price,
                            "currency": CURRENCY,
                            "type": "one_way"
                        }
                        one_way_deals.append(deal)
                        logging.info(f"Found cheap one-way flight: {day_info['date']} = {price} {CURRENCY}")
            
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching one-way flight data for {year}-{month}: {e}")
        except ValueError as e:
            logging.error(f"Error parsing one-way flights JSON for {year}-{month}: {e}")
    
    return one_way_deals

def fetch_flight_prices():
    """
    Fetches flight prices from the LEVEL API for the configured dates.
    Makes two separate calls: one for outbound flights and one for return flights.

    Returns:
        A list of flight deals, where each deal is a dictionary.
        Example: [{'outbound_date': '2025-12-10', 'return_date': '2026-04-15', 'price': 240.5, 'currency': 'EUR'}]
        Returns an empty list if there's an error.
    """
    all_deals = []
    
    for outbound_year, outbound_month, return_year, return_month in SEARCH_DATES:
        logging.info(f"Processing outbound: {outbound_year}-{outbound_month}, return: {return_year}-{return_month}")
        
        # First call: Get outbound flights (inbound tickets)
        outbound_params = {
            'triptype': 'RT',
            'origin': ORIGIN,
            'destination': DESTINATION,
            'month': outbound_month,
            'year': outbound_year,
            'currencyCode': CURRENCY
        }
        
        outbound_referer = (
            f"https://www.flylevel.com/Flight/Select?o1={ORIGIN}&d1={DESTINATION}"
            f"&dd1={outbound_year}-{outbound_month:02d}&ADT=1&CHD=0&INL=0&r=true&mm=true"
            f"&dd2={outbound_year}-{outbound_month:02d}&forcedCurrency={CURRENCY}&forcedCulture=es-ES&newecom=true"
        )
        
        outbound_headers = BASE_HEADERS.copy()
        outbound_headers['Referer'] = outbound_referer
        
        try:
            logging.info(f"Fetching outbound flights for {outbound_year}-{outbound_month}")
            outbound_response = requests.get(API_BASE_URL, params=outbound_params, headers=outbound_headers)
            outbound_response.raise_for_status()
            outbound_data = outbound_response.json()
            logging.info(f"Outbound API Response received: {len(str(outbound_data))} characters")
            
            # Parse outbound flights (new format)
            outbound_flights = []
            if 'data' in outbound_data and 'dayPrices' in outbound_data['data']:
                for day_info in outbound_data['data']['dayPrices']:
                    outbound_flights.append({
                        'date': day_info['date'],
                        'price': day_info['price']
                    })
            logging.info(f"Found {len(outbound_flights)} outbound flights")
            
            # For each outbound flight, get return flights
            for outbound_flight in outbound_flights[:5]:  # Limit to first 5 to avoid too many requests
                outbound_date = outbound_flight['date']
                
                # Second call: Get return flights for specific outbound date
                return_params = {
                    'triptype': 'RT',
                    'origin': ORIGIN,
                    'destination': DESTINATION,
                    'outboundDate': outbound_date,
                    'month': return_month,
                    'year': return_year,
                    'currencyCode': CURRENCY
                }
                
                return_referer = (
                    f"https://www.flylevel.com/Flight/Select?o1={ORIGIN}&d1={DESTINATION}"
                    f"&dd1={outbound_date}&dd2={return_year}-{return_month:02d}-16&ADT=1&CHD=0&INL=0&r=true&mm=true"
                    f"&forcedCurrency={CURRENCY}&forcedCulture=es-ES&newecom=true"
                )
                
                return_headers = BASE_HEADERS.copy()
                return_headers['Referer'] = return_referer
                
                try:
                    logging.info(f"Fetching return flights for outbound date {outbound_date}")
                    return_response = requests.get(API_BASE_URL, params=return_params, headers=return_headers)
                    return_response.raise_for_status()
                    return_data = return_response.json()
                    
                    # Parse return flights (new format)
                    return_flights = []
                    if 'data' in return_data and 'dayPrices' in return_data['data']:
                        for day_info in return_data['data']['dayPrices']:
                            return_date = day_info['date']
                            # Filter to only include return dates in April or May 2026
                            if return_date.startswith('2026-04') or return_date.startswith('2026-05'):
                                return_flights.append({
                                    'date': return_date,
                                    'price': day_info['price']
                                })
                            else:
                                logging.warning(f"Skipping return date {return_date} - not in configured months (Apr/May 2026)")
                    
                    # Find cheapest return flight
                    if return_flights:
                        cheapest_return = min(return_flights, key=lambda x: x['price'])
                        return_date = cheapest_return['date']
                        
                        # Calculate total price
                        total_price = outbound_flight['price'] + cheapest_return['price']
                        
                        deal = {
                            "outbound_date": outbound_date,
                            "return_date": return_date,
                            "price": total_price,
                            "currency": CURRENCY,
                            "type": "round_trip"
                        }
                        all_deals.append(deal)
                        logging.info(f"Found deal: {outbound_date} -> {return_date} = {total_price} {CURRENCY}")
                    else:
                        logging.info(f"No valid return flights found for outbound date {outbound_date} in Apr/May 2026")
                    
                except requests.exceptions.RequestException as e:
                    logging.error(f"Error fetching return flights for {outbound_date}: {e}")
                except ValueError as e:
                    logging.error(f"Error parsing return flights JSON for {outbound_date}: {e}")
                    
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching outbound flight data: {e}")
        except ValueError as e:
            logging.error(f"Error parsing outbound flights JSON: {e}")
            
    return all_deals

def fetch_all_flights():
    """
    Fetches both round trip and one-way flights.
    """
    round_trip_deals = fetch_flight_prices()
    one_way_deals = fetch_one_way_flights()
    
    return round_trip_deals + one_way_deals