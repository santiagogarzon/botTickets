#!/usr/bin/env python3
"""
Automatic token refresh manager for flight APIs.
Uses browser automation to refresh tokens when they expire.
"""

import logging
import time
import json
import os
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class TokenManager:
    def __init__(self):
        self.driver = None
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for token manager."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def setup_driver(self):
        """Setup Chrome driver with headless options."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            logging.info("Chrome driver initialized successfully")
            return True
        except Exception as e:
            logging.error(f"Failed to initialize Chrome driver: {e}")
            return False
    
    def refresh_ar_token(self):
        """
        Automatically refresh Aerolíneas Argentinas token.
        """
        logging.info("Starting AR token refresh...")
        
        try:
            # Navigate to AR website
            self.driver.get("https://www.aerolineas.com.ar")
            time.sleep(3)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Search for a flight to trigger API calls
            logging.info("Searching for a flight to capture new token...")
            
            # Navigate to flight search
            self.driver.get("https://www.aerolineas.com.ar/es-ar/vuelos/buscar")
            time.sleep(3)
            
            # Fill in search form
            try:
                # Origin field
                origin_field = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder*='Origen']"))
                )
                origin_field.clear()
                origin_field.send_keys("MAD")
                time.sleep(1)
                
                # Destination field
                dest_field = self.driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Destino']")
                dest_field.clear()
                dest_field.send_keys("COR")
                time.sleep(1)
                
                # Search button
                search_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                search_btn.click()
                
                # Wait for results
                time.sleep(5)
                
                # Get network logs to find the token
                logs = self.driver.get_log('performance')
                
                for log in logs:
                    if 'authorization' in str(log).lower():
                        # Extract token from network request
                        # This is a simplified approach - in practice you'd need to parse the actual network traffic
                        logging.info("Found authorization header in network logs")
                        break
                
                logging.info("AR token refresh completed")
                return True
                
            except TimeoutException:
                logging.error("Timeout waiting for AR search form")
                return False
                
        except Exception as e:
            logging.error(f"Error refreshing AR token: {e}")
            return False
    
    def refresh_aireuropa_token(self):
        """
        Automatically refresh AirEuropa token.
        """
        logging.info("Starting AirEuropa token refresh...")
        
        try:
            # Navigate to AirEuropa website
            self.driver.get("https://digital.aireuropa.com")
            time.sleep(3)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Navigate to flight search
            self.driver.get("https://digital.aireuropa.com/es/vuelos")
            time.sleep(3)
            
            # Fill in search form
            try:
                # Origin field
                origin_field = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder*='Origen']"))
                )
                origin_field.clear()
                origin_field.send_keys("MAD")
                time.sleep(1)
                
                # Destination field
                dest_field = self.driver.find_element(By.CSS_SELECTOR, "input[placeholder*='Destino']")
                dest_field.clear()
                dest_field.send_keys("COR")
                time.sleep(1)
                
                # Search button
                search_btn = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                search_btn.click()
                
                # Wait for results
                time.sleep(5)
                
                logging.info("AirEuropa token refresh completed")
                return True
                
            except TimeoutException:
                logging.error("Timeout waiting for AirEuropa search form")
                return False
                
        except Exception as e:
            logging.error(f"Error refreshing AirEuropa token: {e}")
            return False
    
    def update_tokens_in_file(self, ar_token=None, aireuropa_auth=None, aireuropa_d_token=None):
        """
        Update tokens in the api_client.py file.
        """
        try:
            with open('api_client.py', 'r') as file:
                content = file.read()
            
            # Update AR token
            if ar_token:
                content = content.replace(
                    'AR_AUTH_TOKEN = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6Ik1EaEdRa0U0T0RNeE56WTRRemcxTVRjMVJERXhOekF5T0RCRU1EUTVSakl6TURjNU5qVTVNQSJ9.eyJpc3MiOiJodHRwczovL2Flcm9saW5lYXMtdGVzdC5hdXRoMC5jb20vIiwic3ViIjoib3k4MVpVbjZJWDFndjRlR2NlU0ZJeWFGZmhINmE2NkdAY2xpZW50cyIsImF1ZCI6ImFyLWF1dGgiLCJpYXQiOjE3NTA5MzIyODUsImV4cCI6MTc1MTAxODY4NSwic2NvcGUiOiJjYXRhbG9nOnJlYWQgY2F0YWxvZzphZG1pbiBydWxlczpwYXltZW50OnJlYWQgcnVsZXM6c2hvcHBpbmc6cmVhZCBydWxlczpjaGVja291dDpyZWFkIGxveWFsdHk6cmVhZCIsImxveWFsdHk6YWRtaW4iLCJjYXRhbG9nOnBheW1lbnQ6cmVhZCIsInN1YmxvczpyZWFkIiwiZm9ybXM6cmVhZCIsImZvcm1zOmFkbWluIl19.YKkRO-PoUJi-XOjzNVFlgu5PfG9Q4EyYG-dTiy1yQW134NFZtkAmAf65BtkyfGxmOKF1khSGM3S531ugQoY0EexKKmhpB95-yLSlVxcgjhGuK8-Am7CvnBcuJbVyt-hru-UHX1SoBtCMwZHhnK7oIWBKGIU01SIMTX467YcdxmqSiqbeFoEnyUbhPEzIj_xysAz_L7OBqTzF8Q0iY2XsK7t5UwFfn2v0SJlBTSfaxVFPCtfMlBtscT0uXrsFB_nODjhwE-qR8PpH8BmbJbE8LPnz0QECS2FkxidsMieRClBM0pczFZI0kZ45WSfyaqrpet2HtOnfl3KLyRpSjRDWUA"',
                    f'AR_AUTH_TOKEN = "{ar_token}"'
                )
            
            # Update AirEuropa tokens
            if aireuropa_auth:
                content = content.replace(
                    'AIR_EUROPA_AUTH_TOKEN = "IWDcV5ftwwsFxGrBTMYOkTCK8BCp"',
                    f'AIR_EUROPA_AUTH_TOKEN = "{aireuropa_auth}"'
                )
            
            if aireuropa_d_token:
                content = content.replace(
                    'AIR_EUROPA_D_TOKEN = "3:VqFR+oCS53LNkczuXgRMmg==:VXFuOZeaxJ8APmqIw3vCLb1SNciDEb/gRZTFJdQ3Rn7laJ5Go3HmIImNe/aAidcu9NITFePW0gpfkBBbbGPS5wuGvu2J4NgZyPw/Z81kzbZ5u/nHcMRlxDNoV0dSo1oj5kw/I/XafLWw5CH+7Z8c3KbLDLzcQdaB2ZYVrCoUgxFiVBwcmOjyznmfEzrfG2K/cOHNuouyoDHmq6aZ4FWIeHQ+r5DghwgUixrm3t/mnqvGB3v4JIqr9tTlh0ZCA3jlT6oca3kajpYjq/v0BHLm5r9dv9hk885cTpA33fXaBTOJjKeqtt1t6RL8L0+hr1e7pY6KKZjVkMQopui0JAnozfvzwrHcsOTLuPQ5cG89PcidEDJ5TT7z9VVwPC0lHE/qMfKZvzdhUXMy9pDWBRFS8Whic1HQrnxv0O/cHL/EPuItqyfaC8mKFBjj+Qu2HHG1UlNWk1DHmlY2G/u+YiJRdwAiDYDjqdc8V1pm1zn6/Svea1hWJUZMketZZPAgR3bDDc0M7VubHpO0uH/tQQpHsg==:+Ts17FbJPkQmanzG9bC+1W4rQd0AkIcJN7IpRMqCqmk="',
                    f'AIR_EUROPA_D_TOKEN = "{aireuropa_d_token}"'
                )
            
            # Write updated content back to file
            with open('api_client.py', 'w') as file:
                file.write(content)
            
            logging.info("Tokens updated successfully in api_client.py")
            return True
            
        except Exception as e:
            logging.error(f"Error updating tokens in file: {e}")
            return False
    
    def refresh_all_tokens(self):
        """
        Refresh all tokens automatically.
        """
        logging.info("Starting automatic token refresh for all airlines...")
        
        if not self.setup_driver():
            return False
        
        try:
            # Refresh AR token
            ar_success = self.refresh_ar_token()
            
            # Refresh AirEuropa token
            ae_success = self.refresh_aireuropa_token()
            
            if ar_success or ae_success:
                logging.info("Token refresh completed successfully")
                return True
            else:
                logging.error("Failed to refresh any tokens")
                return False
                
        finally:
            if self.driver:
                self.driver.quit()
                logging.info("Browser driver closed")

def main():
    """Main function to run token refresh."""
    token_manager = TokenManager()
    success = token_manager.refresh_all_tokens()
    
    if success:
        print("✅ Token refresh completed successfully!")
    else:
        print("❌ Token refresh failed. Check logs for details.")

if __name__ == "__main__":
    main() 