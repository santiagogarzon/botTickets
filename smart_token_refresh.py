#!/usr/bin/env python3
"""
Smart token refresh system that integrates with the main bot.
Automatically detects expired tokens and refreshes them before running searches.
"""

import logging
import time
import json
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import requests
from api_client import check_ar_token, check_aireuropa_token

class SmartTokenRefresh:
    def __init__(self):
        self.driver = None
        self.ar_token = None
        self.aireuropa_auth = None
        self.aireuropa_d_token = None
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for smart token refresh."""
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
            logging.info("Chrome driver initialized for smart token refresh")
            return True
        except Exception as e:
            logging.error(f"Failed to initialize Chrome driver: {e}")
            return False
    
    def check_tokens_status(self):
        """Check if current tokens are valid."""
        logging.info("🔍 Checking current token status...")
        
        ar_valid = check_ar_token()
        ae_valid = check_aireuropa_token()
        
        logging.info(f"AR token valid: {ar_valid}")
        logging.info(f"AirEuropa token valid: {ae_valid}")
        
        return ar_valid, ae_valid
    
    def capture_ar_token(self):
        """Capture AR token using browser automation."""
        logging.info("🔄 Capturing fresh AR token...")
        
        try:
            # Navigate to AR website
            self.driver.get("https://www.aerolineas.com.ar")
            time.sleep(3)
            
            # Navigate to flight search page
            self.driver.get("https://www.aerolineas.com.ar/es-ar/vuelos/buscar")
            time.sleep(5)
            
            # Clear existing logs
            self.driver.get_log('performance')
            
            # Try to trigger API calls by interacting with the page
            try:
                # Look for any clickable elements that might trigger API calls
                elements = self.driver.find_elements(By.CSS_SELECTOR, "button, input, select, a")
                
                for element in elements:
                    try:
                        if element.is_displayed() and element.is_enabled():
                            # Try clicking on buttons or filling inputs
                            if element.tag_name == "button":
                                element.click()
                                time.sleep(2)
                            elif element.tag_name == "input" and element.get_attribute("placeholder"):
                                element.clear()
                                element.send_keys("MAD")
                                time.sleep(1)
                    except:
                        continue
                
            except Exception as e:
                logging.warning(f"Could not interact with AR page: {e}")
            
            # Extract tokens from network logs
            logs = self.driver.get_log('performance')
            
            for log in logs:
                try:
                    log_entry = json.loads(log['message'])
                    
                    if 'message' in log_entry and log_entry['message']['method'] == 'Network.requestWillBeSent':
                        request = log_entry['message']['params']['request']
                        url = request['url']
                        headers = request.get('headers', {})
                        
                        # Look for AR API calls
                        if 'api.aerolineas.com.ar' in url and 'authorization' in headers:
                            auth_header = headers['authorization']
                            if auth_header.startswith('Bearer '):
                                self.ar_token = auth_header.replace('Bearer ', '')
                                logging.info(f"✅ Captured fresh AR token: {self.ar_token[:50]}...")
                                return True
                
                except (json.JSONDecodeError, KeyError):
                    continue
            
            logging.warning("❌ No AR token found in network logs")
            return False
            
        except Exception as e:
            logging.error(f"Error capturing AR token: {e}")
            return False
    
    def capture_aireuropa_tokens(self):
        """Capture AirEuropa tokens using browser automation."""
        logging.info("🔄 Capturing fresh AirEuropa tokens...")
        
        try:
            # Navigate to AirEuropa website
            self.driver.get("https://digital.aireuropa.com")
            time.sleep(3)
            
            # Navigate to flight search
            self.driver.get("https://digital.aireuropa.com/es/vuelos")
            time.sleep(5)
            
            # Clear existing logs
            self.driver.get_log('performance')
            
            # Try to trigger API calls
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, "button, input, select, a")
                
                for element in elements:
                    try:
                        if element.is_displayed() and element.is_enabled():
                            if element.tag_name == "button":
                                element.click()
                                time.sleep(2)
                            elif element.tag_name == "input" and element.get_attribute("placeholder"):
                                element.clear()
                                element.send_keys("MAD")
                                time.sleep(1)
                    except:
                        continue
                
            except Exception as e:
                logging.warning(f"Could not interact with AirEuropa page: {e}")
            
            # Extract tokens from network logs
            logs = self.driver.get_log('performance')
            
            for log in logs:
                try:
                    log_entry = json.loads(log['message'])
                    
                    if 'message' in log_entry and log_entry['message']['method'] == 'Network.requestWillBeSent':
                        request = log_entry['message']['params']['request']
                        url = request['url']
                        headers = request.get('headers', {})
                        
                        # Look for AirEuropa API calls
                        if 'digital.aireuropa.com' in url:
                            if 'authorization' in headers:
                                self.aireuropa_auth = headers['authorization']
                                logging.info(f"✅ Captured fresh AirEuropa auth: {self.aireuropa_auth[:50]}...")
                            
                            if 'd-token' in headers:
                                self.aireuropa_d_token = headers['d-token']
                                logging.info(f"✅ Captured fresh AirEuropa d-token: {self.aireuropa_d_token[:50]}...")
                
                except (json.JSONDecodeError, KeyError):
                    continue
            
            if self.aireuropa_auth or self.aireuropa_d_token:
                return True
            else:
                logging.warning("❌ No AirEuropa tokens found in network logs")
                return False
            
        except Exception as e:
            logging.error(f"Error capturing AirEuropa tokens: {e}")
            return False
    
    def update_tokens_in_file(self):
        """Update tokens in the api_client.py file."""
        try:
            with open('api_client.py', 'r') as file:
                content = file.read()
            
            updated = False
            
            # Update AR token
            if self.ar_token:
                ar_pattern = r'AR_AUTH_TOKEN = "[^"]*"'
                new_ar_token = f'AR_AUTH_TOKEN = "{self.ar_token}"'
                content = re.sub(ar_pattern, new_ar_token, content)
                updated = True
                logging.info("✅ AR token updated in api_client.py")
            
            # Update AirEuropa tokens
            if self.aireuropa_auth:
                ae_auth_pattern = r'AIR_EUROPA_AUTH_TOKEN = "[^"]*"'
                new_ae_auth = f'AIR_EUROPA_AUTH_TOKEN = "{self.aireuropa_auth}"'
                content = re.sub(ae_auth_pattern, new_ae_auth, content)
                updated = True
                logging.info("✅ AirEuropa auth token updated in api_client.py")
            
            if self.aireuropa_d_token:
                ae_d_pattern = r'AIR_EUROPA_D_TOKEN = "[^"]*"'
                new_ae_d = f'AIR_EUROPA_D_TOKEN = "{self.aireuropa_d_token}"'
                content = re.sub(ae_d_pattern, new_ae_d, content)
                updated = True
                logging.info("✅ AirEuropa d-token updated in api_client.py")
            
            if updated:
                with open('api_client.py', 'w') as file:
                    file.write(content)
                logging.info("✅ All tokens updated successfully in api_client.py")
                return True
            else:
                logging.warning("⚠️ No tokens were captured to update")
                return False
            
        except Exception as e:
            logging.error(f"❌ Error updating tokens in file: {e}")
            return False
    
    def smart_refresh(self):
        """Smart token refresh that only refreshes expired tokens."""
        logging.info("🧠 Starting smart token refresh...")
        
        # Check current token status
        ar_valid, ae_valid = self.check_tokens_status()
        
        # Only refresh tokens that are expired
        needs_refresh = not ar_valid or not ae_valid
        
        if not needs_refresh:
            logging.info("✅ All tokens are valid! No refresh needed.")
            return True
        
        logging.info("🔄 Some tokens are expired, refreshing...")
        
        if not self.setup_driver():
            return False
        
        try:
            success = False
            
            # Refresh AR token if needed
            if not ar_valid:
                ar_success = self.capture_ar_token()
                if ar_success:
                    success = True
            
            # Refresh AirEuropa tokens if needed
            if not ae_valid:
                ae_success = self.capture_aireuropa_tokens()
                if ae_success:
                    success = True
            
            # Update tokens in file if any were captured
            if success:
                file_success = self.update_tokens_in_file()
                if file_success:
                    logging.info("✅ Smart token refresh completed successfully!")
                    return True
            
            logging.error("❌ Smart token refresh failed")
            return False
                
        finally:
            if self.driver:
                self.driver.quit()
                logging.info("🔒 Browser driver closed")

def main():
    """Main function for smart token refresh."""
    print("🧠 Smart Token Refresh System")
    print("=" * 40)
    
    smart_refresh = SmartTokenRefresh()
    success = smart_refresh.smart_refresh()
    
    if success:
        print("✅ Smart token refresh completed!")
        print("🚀 Your bot is ready to run!")
    else:
        print("❌ Smart token refresh failed.")
        print("💡 You may need to manually refresh tokens.")

if __name__ == "__main__":
    main() 