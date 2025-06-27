#!/usr/bin/env python3
"""
Setup script for automatic token refresh system.
Installs dependencies and configures ChromeDriver.
"""

import subprocess
import sys
import os
from webdriver_manager.chrome import ChromeDriverManager

def install_dependencies():
    """Install required Python packages."""
    print("📦 Installing Python dependencies...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_chromedriver():
    """Setup ChromeDriver for browser automation."""
    print("🔧 Setting up ChromeDriver...")
    
    try:
        # Install ChromeDriver using webdriver-manager
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver installed at: {driver_path}")
        
        # Set environment variable
        os.environ['CHROMEDRIVER_PATH'] = driver_path
        print("✅ ChromeDriver environment variable set")
        
        return True
    except Exception as e:
        print(f"❌ Failed to setup ChromeDriver: {e}")
        return False

def test_setup():
    """Test the setup by importing required modules."""
    print("🧪 Testing setup...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        print("✅ Selenium imported successfully")
        
        # Test ChromeDriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        driver.quit()
        print("✅ ChromeDriver test successful")
        
        return True
    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🚀 Setting up automatic token refresh system...")
    print("=" * 50)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Setup failed at dependency installation")
        return False
    
    # Setup ChromeDriver
    if not setup_chromedriver():
        print("❌ Setup failed at ChromeDriver setup")
        return False
    
    # Test setup
    if not test_setup():
        print("❌ Setup failed at testing")
        return False
    
    print("=" * 50)
    print("✅ Setup completed successfully!")
    print("🎉 You can now use automatic token refresh!")
    print("\n📋 Available commands:")
    print("   python simple_token_refresh.py  - Refresh all tokens")
    print("   python check_ar_token.py       - Check AR token status")
    print("   python check_aireuropa_token.py - Check AirEuropa token status")
    print("   python main.py                 - Run the flight search bot")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1) 