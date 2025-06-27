#!/usr/bin/env python3
"""
Simple and practical token refresh system.
Uses browser automation to capture fresh tokens from airline websites.
"""

import logging
import time
import json
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import requests

class SimpleTokenRefresh:
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
        
        # Enable performance logging to capture network requests
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            logging.info("Chrome driver initialized with network logging")
            return True
        except Exception as e:
            logging.error(f"Failed to initialize Chrome driver: {e}")
            return False
    
    def capture_ar_token(self):
        """Capture AR token by navigating to their website and triggering API calls."""
        logging.info("Capturing AR token...")
        
        try:
            # Navigate to AR website
            self.driver.get("https://www.aerolineas.com.ar")
            time.sleep(3)
            
            # Navigate to flight search page
            self.driver.get("https://www.aerolineas.com.ar/es-ar/vuelos/buscar")
            time.sleep(5)
            
            # Clear any existing logs
            self.driver.get_log('performance')
            
            # Try to trigger a flight search to generate API calls
            try:
                # Look for search form elements
                search_elements = self.driver.find_elements(By.CSS_SELECTOR, "input, button, select")
                
                # Try to fill in a simple search
                for element in search_elements:
                    try:
                        if element.get_attribute("placeholder") and "origen" in element.get_attribute("placeholder").lower():
                            element.clear()
                            element.send_keys("MAD")
                            time.sleep(1)
                        elif element.get_attribute("placeholder") and "destino" in element.get_attribute("placeholder").lower():
                            element.clear()
                            element.send_keys("COR")
                            time.sleep(1)
                        elif element.tag_name == "button" and ("buscar" in element.text.lower() or "search" in element.text.lower()):
                            element.click()
                            time.sleep(3)
                            break
                    except:
                        continue
                
            except Exception as e:
                logging.warning(f"Could not interact with search form: {e}")
            
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
                                logging.info(f"✅ Captured AR token: {self.ar_token[:50]}...")
                                return True
                
                except (json.JSONDecodeError, KeyError):
                    continue
            
            logging.warning("❌ No AR token found in network logs")
            return False
            
        except Exception as e:
            logging.error(f"Error capturing AR token: {e}")
            return False
    
    def capture_aireuropa_tokens(self):
        """Capture AirEuropa tokens by navigating to their website."""
        logging.info("Capturing AirEuropa tokens...")
        
        try:
            # Navigate to AirEuropa website
            self.driver.get("https://digital.aireuropa.com")
            time.sleep(3)
            
            # Navigate to flight search
            self.driver.get("https://digital.aireuropa.com/es/vuelos")
            time.sleep(5)
            
            # Clear any existing logs
            self.driver.get_log('performance')
            
            # Try to trigger a flight search
            try:
                search_elements = self.driver.find_elements(By.CSS_SELECTOR, "input, button, select")
                
                for element in search_elements:
                    try:
                        if element.get_attribute("placeholder") and "origen" in element.get_attribute("placeholder").lower():
                            element.clear()
                            element.send_keys("MAD")
                            time.sleep(1)
                        elif element.get_attribute("placeholder") and "destino" in element.get_attribute("placeholder").lower():
                            element.clear()
                            element.send_keys("COR")
                            time.sleep(1)
                        elif element.tag_name == "button" and ("buscar" in element.text.lower() or "search" in element.text.lower()):
                            element.click()
                            time.sleep(3)
                            break
                    except:
                        continue
                
            except Exception as e:
                logging.warning(f"Could not interact with AirEuropa search form: {e}")
            
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
                                logging.info(f"✅ Captured AirEuropa auth: {self.aireuropa_auth[:50]}...")
                            
                            if 'd-token' in headers:
                                self.aireuropa_d_token = headers['d-token']
                                logging.info(f"✅ Captured AirEuropa d-token: {self.aireuropa_d_token[:50]}...")
                
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
                # Find and replace the AR token
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
    
    def refresh_all_tokens(self):
        """Refresh all tokens using browser automation."""
        logging.info("🔄 Starting simple token refresh for all airlines...")
        
        if not self.setup_driver():
            return False
        
        try:
            # Capture AR token
            ar_success = self.capture_ar_token()
            
            # Capture AirEuropa tokens
            ae_success = self.capture_aireuropa_tokens()
            
            # Update tokens in file
            if ar_success or ae_success:
                file_success = self.update_tokens_in_file()
                return file_success
            else:
                logging.error("❌ Failed to capture any tokens")
                return False
                
        finally:
            if self.driver:
                self.driver.quit()
                logging.info("🔒 Browser driver closed")

def main():
    """Main function to run simple token refresh."""
    print("🔄 Starting simple automatic token refresh...")
    print("📱 This will open a browser in the background to capture fresh tokens...")
    
    token_refresh = SimpleTokenRefresh()
    success = token_refresh.refresh_all_tokens()
    
    if success:
        print("✅ Token refresh completed successfully!")
        print("📝 Tokens have been updated in api_client.py")
        print("🚀 You can now run your flight search bot!")
    else:
        print("❌ Token refresh failed.")
        print("💡 You may need to manually refresh tokens or check the logs for details.")
        print("🔧 Try running the individual check scripts:")
        print("   python check_ar_token.py")
        print("   python check_aireuropa_token.py")

if __name__ == "__main__":
    main() 