# Flight Search Configuration

# API Endpoint
API_BASE_URL = "https://www.flylevel.com/nwe/flights/api/calendar/"

# Search parameters for round trips
ORIGIN = "BCN"
DESTINATION = "EZE"
CURRENCY = "EUR"

# Search parameters for one-way flights to Buenos Aires
ONE_WAY_ORIGIN = "BCN"
ONE_WAY_DESTINATION = "BUE"  # Buenos Aires airport code
ONE_WAY_THRESHOLD_EUR = 300

# Search parameters for specific date range flights
SPECIFIC_ORIGIN = "BCN"
SPECIFIC_DESTINATION = "EZE"
SPECIFIC_THRESHOLD_EUR = 800
SPECIFIC_START_DATE = "2026-03-10"
SPECIFIC_END_DATE = "2026-04-15"
MIN_DURATION_DAYS = 20
MAX_DURATION_DAYS = 40

# Aerolíneas Argentinas configuration
AR_ROUTES = [
    {
        "origin": "MAD",
        "destination": "COR", 
        "description": "Madrid ➔ Córdoba",
        "threshold_eur": 1000
    }
]

# AirEuropa configuration
AIR_EUROPA_ROUTES = [
    {
        "origin": "MAD",
        "destination": "COR",
        "description": "Madrid ➔ Córdoba (AirEuropa)",
        "threshold_eur": 1000
    }
]

# Dates for the round trip flight search
# Each tuple represents (outbound_year, outbound_month, return_year, return_month)
# We will search for outbound flights in Dec 2025, Jan 2026, Feb 2026, and Mar 2026, with return in Apr 2026 or May 2026
SEARCH_DATES = [
    (2025, 12, 2026, 4),  # Diciembre 2025 -> Abril 2026
    (2025, 12, 2026, 5),  # Diciembre 2025 -> Mayo 2026
    (2026, 1, 2026, 4),   # Enero 2026 -> Abril 2026
    (2026, 1, 2026, 5),   # Enero 2026 -> Mayo 2026
    (2026, 2, 2026, 4),   # Febrero 2026 -> Abril 2026
    (2026, 2, 2026, 5),   # Febrero 2026 -> Mayo 2026
    (2026, 3, 2026, 4),   # Marzo 2026 -> Abril 2026
    (2026, 3, 2026, 5),   # Marzo 2026 -> Mayo 2026
]

# Dates for one-way flights to Buenos Aires
ONE_WAY_DATES = [
    (2026, 1),  # Enero 2026
    (2026, 2),  # Febrero 2026
    (2026, 3),  # Marzo 2026
]

# Headers for the API request
BASE_HEADERS = {
    'sec-ch-ua-platform': '"macOS"',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0'
}

# Price threshold for round trip notifications
PRICE_THRESHOLD_EUR = 700

# Database file name
DB_FILE = "flight_prices.db" 