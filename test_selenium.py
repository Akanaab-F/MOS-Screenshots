from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

def test_selenium():
    """Test if Selenium and Chrome are working"""
    try:
        print("Setting up Chrome driver...")
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in background
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        print("Starting Chrome...")
        driver = webdriver.Chrome(options=chrome_options)
        
        print("Navigating to Google Maps...")
        driver.get("https://www.google.com/maps")
        
        print("Waiting for page to load...")
        time.sleep(3)
        
        print("Taking screenshot...")
        driver.save_screenshot("test_screenshot.png")
        
        print("Closing browser...")
        driver.quit()
        
        print("✓ Test successful! Screenshot saved as 'test_screenshot.png'")
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        return False

if __name__ == "__main__":
    test_selenium() 