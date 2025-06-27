import requests
import logging
import base64
import json
from datetime import datetime, timedelta
from config import (
    API_BASE_URL, ORIGIN, DESTINATION, CURRENCY, SEARCH_DATES, BASE_HEADERS,
    ONE_WAY_ORIGIN, ONE_WAY_DESTINATION, ONE_WAY_DATES, ONE_WAY_THRESHOLD_EUR,
    SPECIFIC_ORIGIN, SPECIFIC_DESTINATION, SPECIFIC_THRESHOLD_EUR,
    SPECIFIC_START_DATE, SPECIFIC_END_DATE, MIN_DURATION_DAYS, MAX_DURATION_DAYS
)

# Aerolíneas Argentinas API configuration
AR_API_BASE_URL = "https://api.aerolineas.com.ar/v1/flights/offers"
AR_AUTH_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1EaEdRa0U0T0RNeE56WTRRemcxTVRjMVJERXhOekF5T0RCRU1EUTVSakl6TURjNU5qVTVNQSJ9.eyJpc3MiOiJodHRwczovL2Flcm9saW5lYXMtdGVzdC5hdXRoMC5jb20vIiwic3ViIjoib3k4MVpVbjZJWDFndjRlR2NlU0ZJeWFGZmhINmE2NkdAY2xpZW50cyIsImF1ZCI6ImFyLWF1dGgiLCJpYXQiOjE3NTA5MzIyODUsImV4cCI6MTc1MTAxODY4NSwic2NvcGUiOiJjYXRhbG9nOnJlYWQgY2F0YWxvZzphZG1pbiBydWxlczpwYXltZW50OnJlYWQgcnVsZXM6c2hvcHBpbmc6cmVhZCBydWxlczpjaGVja291dDpyZWFkIGxveWFsdHk6cmVhZCIsImxveWFsdHk6YWRtaW4iLCJjYXRhbG9nOnBheW1lbnQ6cmVhZCIsInN1YmxvczpyZWFkIiwiZm9ybXM6cmVhZCIsImZvcm1zOmFkbWluIl19.YKkRO-PoUJi-XOjzNVFlgu5PfG9Q4EyYG-dTiy1yQW134NFZtkAmAf65BtkyfGxmOKF1khSGM3S531ugQoY0EexKKmhpB95-yLSlVxcgjhGuK8-Am7CvnBcuJbVyt-hru-UHX1SoBtCMwZHhnK7oIWBKGIU01SIMTX467YcdxmqSiqbeFoEnyUbhPEzIj_xysAz_L7OBqTzF8Q0iY2XsK7t5UwFfn2v0SJlBTSfaxVFPCtfMlBtscT0uXrsFB_nODjhwE-qR8PpH8BmbJbE8LPnz0QECS2FkxidsMieRClBM0pczFZI0kZ45WSfyaqrpet2HtOnfl3KLyRpSjRDWUA"

def decode_jwt_token(token):
    """
    Decodes a JWT token to extract its payload.
    Note: This doesn't verify the signature, just decodes the payload.
    """
    try:
        # Split the token into parts
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        # Decode the payload (second part)
        payload = parts[1]
        # Add padding if needed
        payload += '=' * (4 - len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        logging.error(f"Error decoding JWT token: {e}")
        return None

def is_token_expired(token):
    """
    Checks if the JWT token is expired.
    """
    payload = decode_jwt_token(token)
    if not payload:
        return True
    
    # Get expiration time
    exp_timestamp = payload.get('exp')
    if not exp_timestamp:
        return True
    
    # Convert to datetime
    exp_datetime = datetime.fromtimestamp(exp_timestamp)
    current_datetime = datetime.now()
    
    # Add 5 minutes buffer to refresh before actual expiration
    buffer_time = timedelta(minutes=5)
    
    return current_datetime + buffer_time >= exp_datetime

def get_ar_headers():
    """
    Returns the headers for Aerolíneas Argentinas API with current token.
    """
    global AR_AUTH_TOKEN
    
    # Check if token is expired
    if is_token_expired(AR_AUTH_TOKEN):
        logging.warning("AR token is expired or will expire soon. You need to refresh it manually.")
        logging.info("To get a new token:")
        logging.info("1. Go to https://www.aerolineas.com.ar")
        logging.info("2. Open browser developer tools (F12)")
        logging.info("3. Go to Network tab")
        logging.info("4. Search for a flight")
        logging.info("5. Look for API calls to /v1/flights/offers")
        logging.info("6. Copy the 'authorization' header value")
        logging.info("7. Update the AR_AUTH_TOKEN in api_client.py")
    
    return {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'es-EU',
        'authorization': f'Bearer {AR_AUTH_TOKEN}',
        'origin': 'https://www.aerolineas.com.ar',
        'priority': 'u=1, i',
        'referer': 'https://www.aerolineas.com.ar/',
        'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
        'x-channel-id': 'WEB_ES'
    }

def fetch_aerolineas_argentinas_flights():
    """
    Fetches flights from Aerolíneas Argentinas API for the specific date range logic.
    Searches for flights between March 10 and April 15 with 20-30 days duration.
    
    Returns:
        A list of Aerolíneas Argentinas flight deals.
    """
    ar_deals = []
    
    # Parse start and end dates
    start_date = datetime.strptime(SPECIFIC_START_DATE, "%Y-%m-%d")
    end_date = datetime.strptime(SPECIFIC_END_DATE, "%Y-%m-%d")
    
    logging.info(f"Fetching Aerolíneas Argentinas flights: {SPECIFIC_START_DATE} to {SPECIFIC_END_DATE}")
    
    # Generate all possible outbound dates in the range
    current_date = start_date
    while current_date <= end_date:
        outbound_date_str = current_date.strftime("%Y%m%d")
        
        # Calculate valid return date range (20-30 days after outbound)
        min_return_date = current_date + timedelta(days=MIN_DURATION_DAYS)
        max_return_date = current_date + timedelta(days=MAX_DURATION_DAYS)
        
        # Ensure return date doesn't exceed our end date
        max_return_date = min(max_return_date, end_date)
        
        if min_return_date <= max_return_date:
            return_date_str = max_return_date.strftime("%Y%m%d")
            
            # AR API parameters
            params = {
                'adt': 1,
                'inf': 0,
                'chd': 0,
                'flexDates': 'true',
                'cabinClass': 'Economy',
                'flightType': 'ROUND_TRIP',
                'leg': [f'MAD-COR-{outbound_date_str}', f'COR-MAD-{return_date_str}']
            }
            
            try:
                logging.info(f"Fetching AR flights for {current_date.strftime('%Y-%m-%d')} -> {max_return_date.strftime('%Y-%m-%d')}")
                response = requests.get(AR_API_BASE_URL, params=params, headers=get_ar_headers())
                response.raise_for_status()
                data = response.json()
                
                # Parse AR API response
                if 'calendarOffers' in data:
                    # Check outbound flights (index 0)
                    if '0' in data['calendarOffers']:
                        outbound_offers = data['calendarOffers']['0']
                        for offer in outbound_offers:
                            if offer.get('leg') and offer.get('offerDetails'):
                                offer_date = datetime.strptime(offer['departure'], "%Y-%m-%d")
                                if offer_date == current_date:
                                    outbound_price = offer['offerDetails']['fare']['total']
                                    
                                    # Check return flights (index 1)
                                    if '1' in data['calendarOffers']:
                                        return_offers = data['calendarOffers']['1']
                                        for return_offer in return_offers:
                                            if return_offer.get('leg') and return_offer.get('offerDetails'):
                                                return_date = datetime.strptime(return_offer['departure'], "%Y-%m-%d")
                                                duration_days = (return_date - current_date).days
                                                
                                                # Check if return date is within valid range
                                                if min_return_date <= return_date <= max_return_date:
                                                    if MIN_DURATION_DAYS <= duration_days <= MAX_DURATION_DAYS:
                                                        return_price = return_offer['offerDetails']['fare']['total']
                                                        total_price = outbound_price + return_price
                                                        
                                                        if total_price < SPECIFIC_THRESHOLD_EUR:
                                                            deal = {
                                                                "outbound_date": offer['departure'],
                                                                "return_date": return_offer['departure'],
                                                                "price": total_price,
                                                                "currency": "EUR",  # AR API returns EUR
                                                                "type": "aerolineas_argentinas",
                                                                "duration_days": duration_days,
                                                                "airline": "Aerolíneas Argentinas"
                                                            }
                                                            ar_deals.append(deal)
                                                            logging.info(f"Found AR deal: {offer['departure']} -> {return_offer['departure']} ({duration_days} days) = {total_price} EUR")
                                                            break
                
            except requests.exceptions.RequestException as e:
                logging.error(f"Error fetching AR flights for {current_date.strftime('%Y-%m-%d')}: {e}")
            except ValueError as e:
                logging.error(f"Error parsing AR flights JSON for {current_date.strftime('%Y-%m-%d')}: {e}")
        
        # Move to next day
        current_date += timedelta(days=1)
    
    return ar_deals

def fetch_specific_date_range_flights():
    """
    Fetches flights for specific date range with duration filtering.
    Searches for flights between March 10 and April 15 with 20-30 days duration.
    
    Returns:
        A list of specific date range flight deals.
    """
    specific_deals = []
    
    # Parse start and end dates
    start_date = datetime.strptime(SPECIFIC_START_DATE, "%Y-%m-%d")
    end_date = datetime.strptime(SPECIFIC_END_DATE, "%Y-%m-%d")
    
    logging.info(f"Fetching specific date range flights: {SPECIFIC_START_DATE} to {SPECIFIC_END_DATE}")
    
    # Generate all possible outbound dates in the range
    current_date = start_date
    while current_date <= end_date:
        outbound_date_str = current_date.strftime("%Y-%m-%d")
        
        # Calculate valid return date range (20-30 days after outbound)
        min_return_date = current_date + timedelta(days=MIN_DURATION_DAYS)
        max_return_date = current_date + timedelta(days=MAX_DURATION_DAYS)
        
        # Ensure return date doesn't exceed our end date
        max_return_date = min(max_return_date, end_date)
        
        if min_return_date <= max_return_date:
            # Get return flights for this outbound date
            return_params = {
                'triptype': 'RT',
                'origin': SPECIFIC_ORIGIN,
                'destination': SPECIFIC_DESTINATION,
                'outboundDate': outbound_date_str,
                'month': max_return_date.month,
                'year': max_return_date.year,
                'currencyCode': CURRENCY
            }
            
            return_referer = (
                f"https://www.flylevel.com/Flight/Select?o1={SPECIFIC_ORIGIN}&d1={SPECIFIC_DESTINATION}"
                f"&dd1={outbound_date_str}&dd2={max_return_date.strftime('%Y-%m-%d')}&ADT=1&CHD=0&INL=0&r=true&mm=true"
                f"&forcedCurrency={CURRENCY}&forcedCulture=es-ES&newecom=true"
            )
            
            return_headers = BASE_HEADERS.copy()
            return_headers['Referer'] = return_referer
            
            try:
                logging.info(f"Fetching return flights for outbound date {outbound_date_str}")
                return_response = requests.get(API_BASE_URL, params=return_params, headers=return_headers)
                return_response.raise_for_status()
                return_data = return_response.json()
                
                # Parse return flights
                return_flights = []
                if 'data' in return_data and 'dayPrices' in return_data['data']:
                    for day_info in return_data['data']['dayPrices']:
                        return_date_str = day_info['date']
                        return_date = datetime.strptime(return_date_str, "%Y-%m-%d")
                        
                        # Check if return date is within valid range
                        if min_return_date <= return_date <= max_return_date:
                            duration_days = (return_date - current_date).days
                            if MIN_DURATION_DAYS <= duration_days <= MAX_DURATION_DAYS:
                                return_flights.append({
                                    'date': return_date_str,
                                    'price': day_info['price'],
                                    'duration': duration_days
                                })
                
                # Find cheapest return flight
                if return_flights:
                    cheapest_return = min(return_flights, key=lambda x: x['price'])
                    return_date_str = cheapest_return['date']
                    duration = cheapest_return['duration']
                    
                    # Calculate total price (we need to get outbound price)
                    outbound_params = {
                        'triptype': 'RT',
                        'origin': SPECIFIC_ORIGIN,
                        'destination': SPECIFIC_DESTINATION,
                        'month': current_date.month,
                        'year': current_date.year,
                        'currencyCode': CURRENCY
                    }
                    
                    outbound_referer = (
                        f"https://www.flylevel.com/Flight/Select?o1={SPECIFIC_ORIGIN}&d1={SPECIFIC_DESTINATION}"
                        f"&dd1={current_date.strftime('%Y-%m')}&ADT=1&CHD=0&INL=0&r=true&mm=true"
                        f"&dd2={max_return_date.strftime('%Y-%m')}&forcedCurrency={CURRENCY}&forcedCulture=es-ES&newecom=true"
                    )
                    
                    outbound_headers = BASE_HEADERS.copy()
                    outbound_headers['Referer'] = outbound_referer
                    
                    outbound_response = requests.get(API_BASE_URL, params=outbound_params, headers=outbound_headers)
                    outbound_response.raise_for_status()
                    outbound_data = outbound_response.json()
                    
                    # Find outbound price for this specific date
                    outbound_price = None
                    if 'data' in outbound_data and 'dayPrices' in outbound_data['data']:
                        for day_info in outbound_data['data']['dayPrices']:
                            if day_info['date'] == outbound_date_str:
                                outbound_price = day_info['price']
                                break
                    
                    if outbound_price is not None:
                        total_price = outbound_price + cheapest_return['price']
                        
                        if total_price < SPECIFIC_THRESHOLD_EUR:
                            deal = {
                                "outbound_date": outbound_date_str,
                                "return_date": return_date_str,
                                "price": total_price,
                                "currency": CURRENCY,
                                "type": "specific_range",
                                "duration_days": duration
                            }
                            specific_deals.append(deal)
                            logging.info(f"Found specific range deal: {outbound_date_str} -> {return_date_str} ({duration} days) = {total_price} {CURRENCY}")
                
            except requests.exceptions.RequestException as e:
                logging.error(f"Error fetching specific range flights for {outbound_date_str}: {e}")
            except ValueError as e:
                logging.error(f"Error parsing specific range flights JSON for {outbound_date_str}: {e}")
        
        # Move to next day
        current_date += timedelta(days=1)
    
    return specific_deals

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
    Fetches all types of flights: round trip, one-way, specific date range, and Aerolíneas Argentinas.
    """
    round_trip_deals = fetch_flight_prices()
    one_way_deals = fetch_one_way_flights()
    specific_deals = fetch_specific_date_range_flights()
    ar_deals = fetch_aerolineas_argentinas_flights()
    
    return round_trip_deals + one_way_deals + specific_deals + ar_deals