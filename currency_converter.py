import os
import requests
import logging

# A fixed conversion rate as a fallback
FIXED_EUR_TO_USD = 1.08

def get_eur_to_usd_rate():
    """
    Fetches the EUR to USD conversion rate from an API.
    Falls back to a fixed rate if the API key is not set or the request fails.
    """
    api_key = os.getenv("EXCHANGERATE_API_KEY")
    if not api_key:
        logging.info("EXCHANGERATE_API_KEY not found. Using fixed conversion rate.")
        return FIXED_EUR_TO_USD

    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/EUR"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        if data.get("result") == "success":
            return data["conversion_rates"]["USD"]
        else:
            logging.error(f"Failed to get conversion rate from API: {data.get('error-type')}")
            return FIXED_EUR_TO_USD
    except requests.exceptions.RequestException as e:
        logging.error(f"Error fetching conversion rate: {e}")
        return FIXED_EUR_TO_USD

def convert_eur_to_usd(amount_eur, rate):
    """Converts an amount from EUR to USD using the provided rate."""
    return amount_eur * rate 