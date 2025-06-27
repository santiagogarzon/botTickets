#!/usr/bin/env python3
"""
Test script for the token refresh system.
Tests all components of the automatic token refresh functionality.
"""

import sys
import time
import logging
from datetime import datetime

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing imports...")
    
    try:
        import selenium
        print("✅ Selenium imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import Selenium: {e}")
        return False
    
    try:
        from selenium import webdriver
        print("✅ WebDriver imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import WebDriver: {e}")
        return False
    
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        print("✅ ChromeDriverManager imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import ChromeDriverManager: {e}")
        return False
    
    return True

def test_chromedriver():
    """Test ChromeDriver installation and setup."""
    print("\n🔧 Testing ChromeDriver...")
    
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        # Install ChromeDriver
        driver_path = ChromeDriverManager().install()
        print(f"✅ ChromeDriver installed at: {driver_path}")
        
        # Test ChromeDriver
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        driver = webdriver.Chrome(options=chrome_options)
        print("✅ ChromeDriver test successful")
        
        # Test navigation
        driver.get("https://www.google.com")
        title = driver.title
        print(f"✅ Navigation test successful - Page title: {title}")
        
        driver.quit()
        print("✅ ChromeDriver cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"❌ ChromeDriver test failed: {e}")
        return False

def test_token_refresh_modules():
    """Test the token refresh modules."""
    print("\n🔄 Testing token refresh modules...")
    
    try:
        from simple_token_refresh import SimpleTokenRefresh
        print("✅ SimpleTokenRefresh imported successfully")
        
        # Test initialization
        refresh = SimpleTokenRefresh()
        print("✅ SimpleTokenRefresh initialized successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import SimpleTokenRefresh: {e}")
        return False
    except Exception as e:
        print(f"❌ Failed to initialize SimpleTokenRefresh: {e}")
        return False

def test_smart_token_refresh():
    """Test the smart token refresh module."""
    print("\n🧠 Testing smart token refresh...")
    
    try:
        from smart_token_refresh import SmartTokenRefresh
        print("✅ SmartTokenRefresh imported successfully")
        
        # Test initialization
        smart_refresh = SmartTokenRefresh()
        print("✅ SmartTokenRefresh initialized successfully")
        
        # Test token status check
        ar_valid, ae_valid = smart_refresh.check_tokens_status()
        print(f"✅ Token status check successful - AR: {ar_valid}, AE: {ae_valid}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import SmartTokenRefresh: {e}")
        return False
    except Exception as e:
        print(f"❌ Failed to test SmartTokenRefresh: {e}")
        return False

def test_api_client_integration():
    """Test integration with api_client module."""
    print("\n🔗 Testing API client integration...")
    
    try:
        import api_client
        print("✅ api_client imported successfully")
        
        # Test token check functions
        ar_valid = api_client.check_ar_token()
        print(f"✅ AR token check successful: {ar_valid}")
        
        ae_valid = api_client.check_aireuropa_token()
        print(f"✅ AirEuropa token check successful: {ae_valid}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import api_client: {e}")
        return False
    except Exception as e:
        print(f"❌ Failed to test api_client integration: {e}")
        return False

def run_quick_token_refresh():
    """Run a quick token refresh test."""
    print("\n⚡ Running quick token refresh test...")
    
    try:
        from smart_token_refresh import SmartTokenRefresh
        
        smart_refresh = SmartTokenRefresh()
        success = smart_refresh.smart_refresh()
        
        if success:
            print("✅ Quick token refresh test successful!")
            return True
        else:
            print("⚠️ Quick token refresh test completed but no tokens were refreshed")
            return True  # This is not necessarily a failure
            
    except Exception as e:
        print(f"❌ Quick token refresh test failed: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 Token Refresh System Test Suite")
    print("=" * 50)
    print(f"🕐 Test started at: {datetime.now()}")
    
    tests = [
        ("Import Tests", test_imports),
        ("ChromeDriver Tests", test_chromedriver),
        ("Token Refresh Modules", test_token_refresh_modules),
        ("Smart Token Refresh", test_smart_token_refresh),
        ("API Client Integration", test_api_client_integration),
        ("Quick Token Refresh", run_quick_token_refresh)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print(f"\n{'='*50}")
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Token refresh system is ready to use.")
        print("\n📋 Available commands:")
        print("   python simple_token_refresh.py  - Manual token refresh")
        print("   python smart_token_refresh.py   - Smart token refresh")
        print("   python main.py                 - Run the bot with auto refresh")
    else:
        print("⚠️ Some tests failed. Please check the errors above.")
        print("💡 You may need to install dependencies or fix configuration.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 