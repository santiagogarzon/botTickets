# Flight Search Configuration

# API Endpoint
API_BASE_URL = "https://www.flylevel.com/nwe/flights/api/calendar/"

# Search parameters
ORIGIN = "BCN"
DESTINATION = "EZE"
CURRENCY = "EUR"

# Dates for the flight search
# Each tuple represents (outbound_year, outbound_month, return_year, return_month)
# We will search for outbound flights in Dec 2025 and Jan 2026, with return in Apr 2026
SEARCH_DATES = [
    (2025, 12, 2026, 4),
    (2026, 1, 2026, 4),
]

# Headers for the API request
BASE_HEADERS = {
    'sec-ch-ua-platform': '"macOS"',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0'
}

# Price threshold for notifications
PRICE_THRESHOLD_EUR = 500

# Database file name
DB_FILE = "flight_prices.db" 