import pandas as pd
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import urllib.parse

def setup_chrome_driver():
    """Setup Chrome driver with appropriate options for screenshots"""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")  # Start with maximized window
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Create screenshots directory if it doesn't exist
    if not os.path.exists("screenshots"):
        os.makedirs("screenshots")
    
    return webdriver.Chrome(options=chrome_options)

def capture_route_screenshot(driver, origin, destination, filename):
    """Capture screenshot of Google Maps route between two points"""
    try:
        # Encode coordinates for URL
        origin_encoded = urllib.parse.quote(origin)
        destination_encoded = urllib.parse.quote(destination)
        
        # Construct Google Maps URL with directions
        url = f"https://www.google.com/maps/dir/{origin_encoded}/{destination_encoded}/"
        print(f"Opening URL: {url}")
        
        driver.get(url)
        
        # Wait for the page to load and route to be displayed
        wait = WebDriverWait(driver, 20)
        
        # Wait for the route information to appear
        try:
            # Wait for the route summary to load
            route_element = wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-value='Directions']"))
            )
            print("Route loaded successfully")
        except TimeoutException:
            print("Route element not found, but continuing...")
        
        # Additional wait to ensure route is fully loaded
        time.sleep(5)
        
        # Take screenshot
        screenshot_path = f"screenshots/{filename}.png"
        driver.save_screenshot(screenshot_path)
        print(f"Screenshot saved: {screenshot_path}")
        
        return True
        
    except Exception as e:
        print(f"Error capturing screenshot for {filename}: {e}")
        return False

def process_material_excel_with_screenshots(excel_file, api_key):
    """Process Excel file and capture route screenshots"""
    
    # Load Excel sheets
    warehouses_df = pd.read_excel(excel_file, sheet_name="warehouse", engine="openpyxl")
    region_map_df = pd.read_excel(excel_file, sheet_name="region", engine="openpyxl")
    
    # Create mappings
    region_to_warehouse = dict(zip(region_map_df["region"], region_map_df["warehouse"]))
    warehouse_to_coords = dict(zip(
        warehouses_df["Warehouse"],
        zip(warehouses_df["latitude"], warehouses_df["longitude"])
    ))
    
    # Setup Chrome driver
    driver = setup_chrome_driver()
    
    try:
        # Process transportation sheet
        transportation_df = pd.read_excel(excel_file, sheet_name="transportation", engine="openpyxl")
        
        for idx, row in transportation_df.iterrows():
            try:
                # Get site coordinates
                site_lat = row['latitude']
                site_lon = row['longitude']
                site_coords = f"{site_lat},{site_lon}"
                
                # Get warehouse coordinates
                warehouse_name = row["warehouse"]
                warehouse_coords = warehouse_to_coords.get(warehouse_name)
                
                if not warehouse_coords:
                    print(f"Missing warehouse coordinates for '{warehouse_name}'")
                    continue
                
                warehouse_lat, warehouse_lon = warehouse_coords
                warehouse_coords_str = f"{warehouse_lat},{warehouse_lon}"
                
                # Create filename for screenshot
                site_id = row.get('ID', f'site_{idx}')
                warehouse_clean = warehouse_name.replace(' ', '_').replace('/', '_')
                filename = f"route_{site_id}_to_{warehouse_clean}"
                
                print(f"\nProcessing route {idx + 1}/{len(transportation_df)}:")
                print(f"Site: {site_coords} -> Warehouse: {warehouse_coords_str}")
                print(f"Filename: {filename}")
                
                # Capture screenshot
                success = capture_route_screenshot(
                    driver, 
                    site_coords, 
                    warehouse_coords_str, 
                    filename
                )
                
                if success:
                    print(f"✓ Screenshot captured successfully for {filename}")
                else:
                    print(f"✗ Failed to capture screenshot for {filename}")
                
                # Small delay between requests to avoid overwhelming Google Maps
                time.sleep(2)
                
            except Exception as e:
                print(f"Error processing row {idx}: {e}")
                continue
                
    except Exception as e:
        print(f"Error processing 'transportation' sheet: {e}")
    
    finally:
        # Close the browser
        driver.quit()
        print("\nBrowser closed. Screenshots saved in 'screenshots' folder.")

def main():
    """Main function to run the screenshot capture process"""
    excel_file = "material.xlsx"
    google_api_key = "AIzaSyCXALU_QOORu1Lwd9YSWV_ma636xOu7yWk"
    
    print("Starting Google Maps route screenshot capture...")
    print("Make sure you have Chrome browser installed.")
    print("Screenshots will be saved in the 'screenshots' folder.")
    
    process_material_excel_with_screenshots(excel_file, google_api_key)

if __name__ == "__main__":
    main() 