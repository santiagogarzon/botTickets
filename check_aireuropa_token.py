#!/usr/bin/env python3
"""
Utility script to check AirEuropa token status and help with token refresh.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_client import AIR_EUROPA_AUTH_TOKEN, AIR_EUROPA_D_TOKEN
import requests

def test_aireuropa_connection():
    """
    Test the AirEuropa API connection with current tokens.
    """
    print("🔍 AirEuropa Token Checker")
    print("=" * 50)
    
    from api_client import get_aireuropa_headers, AIR_EUROPA_API_BASE_URL
    
    # Test payload for a simple search
    test_payload = {
        "commercialFareFamilies": ["DIGITAL1"],
        "travelers": [{"passengerTypeCode": "ADT"}],
        "itineraries": [
            {
                "departureDateTime": "2026-03-10T00:00:00.000",
                "originLocationCode": "MAD",
                "destinationLocationCode": "COR",
                "flexibility": 7,
                "isRequestedBound": True
            },
            {
                "departureDateTime": "2026-04-11T00:00:00.000",
                "originLocationCode": "COR",
                "destinationLocationCode": "MAD",
                "isRequestedBound": False
            }
        ],
        "searchPreferences": {
            "showUnavailableEntries": True,
            "showMilesPrice": False
        }
    }
    
    try:
        print("🔄 Testing AirEuropa API connection...")
        response = requests.post(AIR_EUROPA_API_BASE_URL, json=test_payload, headers=get_aireuropa_headers())
        
        if response.status_code == 200:
            print("✅ AirEuropa API connection successful!")
            data = response.json()
            
            if 'data' in data and len(data['data']) > 0:
                print(f"📊 Found {len(data['data'])} flight options")
                
                # Show first flight details
                first_flight = data['data'][0]
                departure_date = first_flight.get('departureDate')
                return_date = first_flight.get('returnDate')
                
                if 'prices' in first_flight and 'totalPrices' in first_flight['prices']:
                    total_price_centavos = first_flight['prices']['totalPrices'][0]['total']
                    total_price_eur = total_price_centavos / 100
                    
                    print(f"💰 Sample flight price: {total_price_eur} EUR")
                    print(f"📅 Sample dates: {departure_date} -> {return_date}")
                
                print("✅ Tokens are working correctly!")
            else:
                print("⚠️  API responded but no flight data found")
        else:
            print(f"❌ API connection failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing AirEuropa API: {e}")
    
    print("\n" + "=" * 50)
    print("🔄 How to refresh AirEuropa tokens:")
    print("1. Go to https://digital.aireuropa.com")
    print("2. Open browser developer tools (F12)")
    print("3. Go to Network tab")
    print("4. Search for a flight (e.g., MAD to COR)")
    print("5. Look for API calls to /v2/search/air-calendars")
    print("6. Copy the 'authorization' header value")
    print("7. Copy the 'x-d-token' header value")
    print("8. Update AIR_EUROPA_AUTH_TOKEN and AIR_EUROPA_D_TOKEN in api_client.py")
    print("\n💡 Tip: AirEuropa tokens may expire periodically")

if __name__ == "__main__":
    test_aireuropa_connection() 