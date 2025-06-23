import requests
import logging
from config import API_BASE_URL, ORIGIN, DESTINATION, CURRENCY, SEARCH_DATES, BASE_HEADERS

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
                            return_flights.append({
                                'date': day_info['date'],
                                'price': day_info['price']
                            })
                    
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
                            "currency": CURRENCY
                        }
                        all_deals.append(deal)
                        logging.info(f"Found deal: {outbound_date} -> {return_date} = {total_price} {CURRENCY}")
                    
                except requests.exceptions.RequestException as e:
                    logging.error(f"Error fetching return flights for {outbound_date}: {e}")
                except ValueError as e:
                    logging.error(f"Error parsing return flights JSON for {outbound_date}: {e}")
                    
        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching outbound flight data: {e}")
        except ValueError as e:
            logging.error(f"Error parsing outbound flights JSON: {e}")
            
    return all_deals 