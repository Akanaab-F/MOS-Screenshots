import pandas as pd
import time
import os
import zipfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.parse
from models import db, Job

def setup_chrome_driver(headless=True, user_data_dir="chrome_profile"):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument(f'--user-data-dir={os.path.abspath(user_data_dir)}')
    return webdriver.Chrome(options=chrome_options)

def capture_route_screenshot_linear(driver, idx, row, warehouse_coords, job_id, max_retries=3):
    """Capture route screenshot with retry mechanism"""
    site_id = row.get('ID', f'site_{idx}')
    
    for attempt in range(max_retries):
        try:
            # SWAP: Use longitude as latitude and latitude as longitude
            site_lat = float(row['longitude'])
            site_lon = float(row['latitude'])
            warehouse_lat = float(warehouse_coords[1])
            warehouse_lon = float(warehouse_coords[0])
            
            # Validate coordinates
            if not (-90 <= site_lat <= 90) or not (-180 <= site_lon <= 180):
                return f"[ERR] Invalid coordinates for {site_id}: lat={site_lat}, lon={site_lon}"
            
            if not (-90 <= warehouse_lat <= 90) or not (-180 <= warehouse_lon <= 180):
                return f"[ERR] Invalid warehouse coordinates for {site_id}: lat={warehouse_lat}, lon={warehouse_lon}"
            
            url = f"https://www.google.com/maps/dir/{site_lat},{site_lon}/{warehouse_lat},{warehouse_lon}/data=!4m2!4m1!3e0"
            filename = f"{site_id}"
            
            driver.get(url)
            
            # Wait for the page to load with better error handling
            try:
                wait = WebDriverWait(driver, 10)
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.section-directions-trip-title, div[data-section-id='0']")))
            except Exception as e:
                if attempt < max_retries - 1:
                    print(f"Attempt {attempt + 1} failed for {site_id}, retrying... Error: {e}")
                    time.sleep(2)  # Wait before retry
                    continue
                else:
                    # Final attempt failed, try with shorter wait
                    time.sleep(3)
            
            # Create job-specific screenshots directory
            job_screenshots_dir = f"screenshots/{job_id}"
            if not os.path.exists(job_screenshots_dir):
                os.makedirs(job_screenshots_dir)
            
            screenshot_path = f"{job_screenshots_dir}/{filename}.png"
            driver.save_screenshot(screenshot_path)
            
            # Verify screenshot was created and has content
            if os.path.exists(screenshot_path) and os.path.getsize(screenshot_path) > 1000:
                # Update job progress
                with db.app.app_context():
                    job = Job.query.filter_by(job_id=job_id).first()
                    if job:
                        job.completed_routes += 1
                        job.progress = int((job.completed_routes / job.total_routes) * 100)
                        db.session.commit()
                
                return f"[OK] {filename}"
            else:
                if attempt < max_retries - 1:
                    print(f"Screenshot too small for {site_id}, retrying...")
                    continue
                else:
                    return f"[ERR] Failed to capture screenshot for {site_id} after {max_retries} attempts"
                    
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"Attempt {attempt + 1} failed for {site_id}, retrying... Error: {e}")
                time.sleep(2)
                continue
            else:
                return f"[ERR] Error for {site_id} after {max_retries} attempts: {e}"
    
    return f"[ERR] Failed to capture screenshot for {site_id} after {max_retries} attempts"

def process_material_excel_linear(excel_file, job_id):
    print(f"Loading Excel data for job {job_id}...")
    
    # Update job with total routes count
    with db.app.app_context():
        job = Job.query.filter_by(job_id=job_id).first()
        if not job:
            raise Exception("Job not found")
        
        # Count total routes
        transportation_df = pd.read_excel(excel_file, sheet_name="transportation", engine="openpyxl")
        job.total_routes = len(transportation_df)
        db.session.commit()
    
    warehouses_df = pd.read_excel(excel_file, sheet_name="warehouse", engine="openpyxl")
    region_map_df = pd.read_excel(excel_file, sheet_name="region", engine="openpyxl")
    region_to_warehouse = dict(zip(region_map_df["region"], region_map_df["warehouse"]))
    warehouse_to_coords = dict(zip(
        warehouses_df["Warehouse"],
        zip(warehouses_df["latitude"], warehouses_df["longitude"])
    ))
    transportation_df = pd.read_excel(excel_file, sheet_name="transportation", engine="openpyxl")
    total_routes = len(transportation_df)
    print(f"Processing {total_routes} routes linearly...")
    
    # Create a single Chrome instance that we'll reuse
    driver = setup_chrome_driver(headless=True, user_data_dir="chrome_profile")
    
    try:
        # First, navigate to Google Maps to accept consent
        print("Setting up browser and checking for consent dialog...")
        driver.get("https://www.google.com/maps")
        
        # Wait a few seconds to see if consent dialog appears
        time.sleep(3)
        
        # Check if there's a consent dialog by looking for common consent elements
        try:
            consent_elements = driver.find_elements(By.XPATH, "//button[contains(., 'Accept') or contains(., 'I agree') or contains(., 'Accept all')]")
            if consent_elements:
                print("Consent dialog detected. Clicking accept...")
                consent_elements[0].click()
                time.sleep(2)
        except:
            print("No consent dialog detected. Proceeding with screenshot capture...")
        
        results = []
        for idx, row in transportation_df.iterrows():
            warehouse_name = row["warehouse"]
            warehouse_coords = warehouse_to_coords.get(warehouse_name)
            if warehouse_coords:
                result = capture_route_screenshot_linear(driver, idx, row, warehouse_coords, job_id)
                results.append(result)
                print(f"[{len(results)}/{total_routes}] {result}")
            else:
                print(f"Missing warehouse: {warehouse_name}")
        
        print(f"\n[COMPLETE] Completed! {len(results)} screenshots saved.")
        
        # Create zip file with all screenshots
        job_screenshots_dir = f"screenshots/{job_id}"
        zip_filename = f"screenshots/{job_id}_screenshots.zip"
        
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for root, dirs, files in os.walk(job_screenshots_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, job_screenshots_dir)
                    zipf.write(file_path, arcname)
        
        return zip_filename
        
    finally:
        driver.quit()

def main():
    excel_file = "material.xlsx"
    print("[*] Linear Google Maps Screenshot Capture (with coordinate fix)")
    process_material_excel_linear(excel_file, "test_job")

if __name__ == "__main__":
    main() 