#!/usr/bin/env python3
"""
Utility script to check Aerolíneas Argentinas token status and help with token refresh.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api_client import decode_jwt_token, is_token_expired, AR_AUTH_TOKEN
from datetime import datetime

def main():
    print("🔍 Aerolíneas Argentinas Token Checker")
    print("=" * 50)
    
    # Decode the token
    payload = decode_jwt_token(AR_AUTH_TOKEN)
    
    if not payload:
        print("❌ Error: Could not decode the token")
        return
    
    print(f"✅ Token decoded successfully")
    print(f"📋 Token info:")
    print(f"   - Issuer: {payload.get('iss', 'Unknown')}")
    print(f"   - Subject: {payload.get('sub', 'Unknown')}")
    print(f"   - Audience: {payload.get('aud', 'Unknown')}")
    
    # Check expiration
    exp_timestamp = payload.get('exp')
    if exp_timestamp:
        exp_datetime = datetime.fromtimestamp(exp_timestamp)
        current_datetime = datetime.now()
        time_until_expiry = exp_datetime - current_datetime
        
        print(f"   - Expires at: {exp_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   - Current time: {current_datetime.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if time_until_expiry.total_seconds() > 0:
            hours = int(time_until_expiry.total_seconds() // 3600)
            minutes = int((time_until_expiry.total_seconds() % 3600) // 60)
            print(f"   - Time until expiry: {hours}h {minutes}m")
            
            if is_token_expired(AR_AUTH_TOKEN):
                print("⚠️  Token will expire soon (within 5 minutes)")
            else:
                print("✅ Token is still valid")
        else:
            print("❌ Token has expired!")
    else:
        print("❌ No expiration time found in token")
    
    print("\n" + "=" * 50)
    print("🔄 How to refresh the token:")
    print("1. Go to https://www.aerolineas.com.ar")
    print("2. Open browser developer tools (F12)")
    print("3. Go to Network tab")
    print("4. Search for a flight (e.g., MAD to COR)")
    print("5. Look for API calls to /v1/flights/offers")
    print("6. Copy the 'authorization' header value")
    print("7. Update the AR_AUTH_TOKEN in api_client.py")
    print("\n💡 Tip: The token usually expires after 24 hours")

if __name__ == "__main__":
    main() 