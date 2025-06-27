#!/usr/bin/env python3
"""
Advanced automatic token refresh system.
Captures tokens from network requests using browser automation.
"""

import logging
import time
import json
import re
import base64
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import requests

class AutoTokenRefresh:
    def __init__(self):
        self.driver = None
        self.ar_token = None
        self.aireuropa_auth = None
        self.aireuropa_d_token = None
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for token refresh."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def setup_driver(self):
        """Setup Chrome driver with network logging enabled."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36")
        
        # Enable performance logging
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            logging.info("Chrome driver initialized with network logging")
            return True
        except Exception as e:
            logging.error(f"Failed to initialize Chrome driver: {e}")
            return False
    
    def extract_tokens_from_logs(self):
        """Extract tokens from network logs."""
        try:
            logs = self.driver.get_log('performance')
            
            for log in logs:
                try:
                    log_entry = json.loads(log['message'])
                    
                    # Check for network requests
                    if 'message' in log_entry and log_entry['message']['method'] == 'Network.requestWillBeSent':
                        request = log_entry['message']['params']['request']
                        url = request['url']
                        headers = request.get('headers', {})
                        
                        # Look for AR API calls
                        if 'api.aerolineas.com.ar' in url and 'authorization' in headers:
                            auth_header = headers['authorization']
                            if auth_header.startswith('Bearer '):
                                self.ar_token = auth_header.replace('Bearer ', '')
                                logging.info(f"Captured AR token: {self.ar_token[:50]}...")
                        
                        # Look for AirEuropa API calls
                        elif 'digital.aireuropa.com' in url:
                            if 'authorization' in headers:
                                self.aireuropa_auth = headers['authorization']
                                logging.info(f"Captured AirEuropa auth: {self.aireuropa_auth[:50]}...")
                            
                            if 'd-token' in headers:
                                self.aireuropa_d_token = headers['d-token']
                                logging.info(f"Captured AirEuropa d-token: {self.aireuropa_d_token[:50]}...")
                
                except (json.JSONDecodeError, KeyError):
                    continue
            
            return True
            
        except Exception as e:
            logging.error(f"Error extracting tokens from logs: {e}")
            return False
    
    def refresh_ar_token_manual(self):
        """
        Manual approach to get AR token by making direct API calls.
        """
        logging.info("Attempting manual AR token refresh...")
        
        try:
            # AR uses Auth0, so we need to get a new token from their auth endpoint
            auth_url = "https://aerolineas-test.auth0.com/oauth/token"
            
            payload = {
                "client_id": "oy81ZUn6IX1gv4eGceSFIyaFfhH6a6G",
                "client_secret": "YOUR_CLIENT_SECRET",  # This would need to be obtained
                "audience": "ar-auth",
                "grant_type": "client_credentials",
                "scope": "catalog:read catalog:admin rules:payment:read rules:shopping:read rules:checkout:read loyalty:read"
            }
            
            # For now, we'll use a simpler approach - try to get token from their public endpoint
            response = requests.get("https://www.aerolineas.com.ar/api/v1/flights/search", 
                                  headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"})
            
            if response.status_code == 401:
                # Token expired, we need to get a new one
                logging.info("AR token expired, attempting to get new one...")
                
                # This is a simplified approach - in practice you'd need the actual client credentials
                # For now, we'll return False to indicate manual intervention is needed
                return False
            
            return True
            
        except Exception as e:
            logging.error(f"Error in manual AR token refresh: {e}")
            return False
    
    def refresh_aireuropa_token_manual(self):
        """
        Manual approach to get AirEuropa tokens.
        """
        logging.info("Attempting manual AirEuropa token refresh...")
        
        try:
            # Try to get tokens from their public endpoints
            session = requests.Session()
            
            # Get initial page to capture tokens
            response = session.get("https://digital.aireuropa.com/es/vuelos",
                                 headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"})
            
            # Look for tokens in response headers or cookies
            if 'authorization' in response.headers:
                self.aireuropa_auth = response.headers['authorization']
            
            if 'd-token' in response.headers:
                self.aireuropa_d_token = response.headers['d-token']
            
            # Try to make a search request to trigger token generation
            search_url = "https://digital.aireuropa.com/api/v1/flights/search"
            search_payload = {
                "origin": "MAD",
                "destination": "COR",
                "departureDate": "2025-12-15",
                "returnDate": "2025-12-22",
                "adults": 1,
                "children": 0,
                "infants": 0
            }
            
            response = session.post(search_url, json=search_payload)
            
            # Check for new tokens in response
            if 'authorization' in response.headers:
                self.aireuropa_auth = response.headers['authorization']
            
            if 'd-token' in response.headers:
                self.aireuropa_d_token = response.headers['d-token']
            
            return True
            
        except Exception as e:
            logging.error(f"Error in manual AirEuropa token refresh: {e}")
            return False
    
    def update_tokens_in_file(self):
        """Update tokens in the api_client.py file."""
        try:
            with open('api_client.py', 'r') as file:
                content = file.read()
            
            updated = False
            
            # Update AR token
            if self.ar_token:
                old_token = 'AR_AUTH_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1EaEdRa0U0T0RNeE56WTRRemcxTVRjMVJERXhOekF5T0RCRU1EUTVSakl6TURjNU5qVTVNQSJ9.eyJpc3MiOiJodHRwczovL2Flcm9saW5lYXMtdGVzdC5hdXRoMC5jb20vIiwic3ViIjoib3k4MVpVbjZJWDFndjRlR2NlU0ZJeWFGZmhINmE2NkdAY2xpZW50cyIsImF1ZCI6ImFyLWF1dGgiLCJpYXQiOjE3NTA5MzIyODUsImV4cCI6MTc1MTAxODY4NSwic2NvcGUiOiJjYXRhbG9nOnJlYWQgY2F0YWxvZzphZG1pbiBydWxlczpwYXltZW50OnJlYWQgcnVsZXM6c2hvcHBpbmc6cmVhZCBydWxlczpjaGVja291dDpyZWFkIGxveWFsdHk6cmVhZCIsImxveWFsdHk6YWRtaW4iLCJjYXRhbG9nOnBheW1lbnQ6cmVhZCIsInN1YmxvczpyZWFkIiwiZm9ybXM6cmVhZCIsImZvcm1zOmFkbWluIl19.YKkRO-PoUJi-XOjzNVFlgu5PfG9Q4EyYG-dTiy1yQW134NFZtkAmAf65BtkyfGxmOKF1khSGM3S531ugQoY0EexKKmhpB95-yLSlVxcgjhGuK8-Am7CvnBcuJbVyt-hru-UHX1SoBtCMwZHhnK7oIWBKGIU01SIMTX467YcdxmqSiqbeFoEnyUbhPEzIj_xysAz_L7OBqTzF8Q0iY2XsK7t5UwFfn2v0SJlBTSfaxVFPCtfMlBtscT0uXrsFB_nODjhwE-qR8PpH8BmbJbE8LPnz0QECS2FkxidsMieRClBM0pczFZI0kZ45WSfyaqrpet2HtOnfl3KLyRpSjRDWUA"'
                new_token = f'AR_AUTH_TOKEN = "{self.ar_token}"'
                content = content.replace(old_token, new_token)
                updated = True
                logging.info("AR token updated in api_client.py")
            
            # Update AirEuropa tokens
            if self.aireuropa_auth:
                old_auth = 'AIR_EUROPA_AUTH_TOKEN = "IWDcV5ftwwsFxGrBTMYOkTCK8BCp"'
                new_auth = f'AIR_EUROPA_AUTH_TOKEN = "{self.aireuropa_auth}"'
                content = content.replace(old_auth, new_auth)
                updated = True
                logging.info("AirEuropa auth token updated in api_client.py")
            
            if self.aireuropa_d_token:
                old_d_token = 'AIR_EUROPA_D_TOKEN = "3:VqFR+oCS53LNkczuXgRMmg==:VXFuOZeaxJ8APmqIw3vCLb1SNciDEb/gRZTFJdQ3Rn7laJ5Go3HmIImNe/aAidcu9NITFePW0gpfkBBbbGPS5wuGvu2J4NgZyPw/Z81kzbZ5u/nHcMRlxDNoV0dSo1oj5kw/I/XafLWw5CH+7Z8c3KbLDLzcQdaB2ZYVrCoUgxFiVBwcmOjyznmfEzrfG2K/cOHNuouyoDHmq6aZ4FWIeHQ+r5DghwgUixrm3t/mnqvGB3v4JIqr9tTlh0ZCA3jlT6oca3kajpYjq/v0BHLm5r9dv9hk885cTpA33fXaBTOJjKeqtt1t6RL8L0+hr1e7pY6KKZjVkMQopui0JAnozfvzwrHcsOTLuPQ5cG89PcidEDJ5TT7z9VVwPC0lHE/qMfKZvzdhUXMy9pDWBRFS8Whic1HQrnxv0O/cHL/EPuItqyfaC8mKFBjj+Qu2HHG1UlNWk1DHmlY2G/u+YiJRdwAiDYDjqdc8V1pm1zn6/Svea1hWJUZMketZZPAgR3bDDc0M7VubHpO0uH/tQQpHsg==:+Ts17FbJPkQmanzG9bC+1W4rQd0AkIcJN7IpRMqCqmk="'
                new_d_token = f'AIR_EUROPA_D_TOKEN = "{self.aireuropa_d_token}"'
                content = content.replace(old_d_token, new_d_token)
                updated = True
                logging.info("AirEuropa d-token updated in api_client.py")
            
            if updated:
                with open('api_client.py', 'w') as file:
                    file.write(content)
                logging.info("All tokens updated successfully in api_client.py")
                return True
            else:
                logging.warning("No tokens were captured to update")
                return False
            
        except Exception as e:
            logging.error(f"Error updating tokens in file: {e}")
            return False
    
    def refresh_all_tokens(self):
        """Refresh all tokens using multiple approaches."""
        logging.info("Starting advanced token refresh for all airlines...")
        
        success = False
        
        # Try manual approach first (faster and more reliable)
        logging.info("Trying manual token refresh...")
        
        ar_success = self.refresh_ar_token_manual()
        ae_success = self.refresh_aireuropa_token_manual()
        
        if ar_success or ae_success:
            success = self.update_tokens_in_file()
        
        # If manual approach failed, try browser automation
        if not success:
            logging.info("Manual approach failed, trying browser automation...")
            
            if self.setup_driver():
                try:
                    # Navigate to websites and capture tokens
                    self.driver.get("https://www.aerolineas.com.ar")
                    time.sleep(3)
                    
                    self.driver.get("https://digital.aireuropa.com")
                    time.sleep(3)
                    
                    # Extract tokens from network logs
                    self.extract_tokens_from_logs()
                    
                    # Update tokens in file
                    success = self.update_tokens_in_file()
                    
                finally:
                    self.driver.quit()
                    logging.info("Browser driver closed")
        
        return success

def main():
    """Main function to run advanced token refresh."""
    print("🔄 Starting advanced automatic token refresh...")
    
    token_refresh = AutoTokenRefresh()
    success = token_refresh.refresh_all_tokens()
    
    if success:
        print("✅ Token refresh completed successfully!")
        print("📝 Tokens have been updated in api_client.py")
    else:
        print("❌ Token refresh failed.")
        print("💡 You may need to manually refresh tokens or check the logs for details.")

if __name__ == "__main__":
    main() 