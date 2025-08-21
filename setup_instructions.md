# Google Maps Route Screenshot Capture Setup

## What You Need to Complete This Task:

### 1. **Python Dependencies**
Install the required packages:
```bash
pip install -r requirements.txt
```

### 2. **Chrome Browser**
- Make sure Google Chrome is installed on your system
- The script will automatically use Chrome to capture screenshots

### 3. **ChromeDriver** (Automatic Installation)
- Selenium will automatically download the appropriate ChromeDriver version
- No manual installation needed

### 4. **Your Data**
- Ensure your `material.xlsx` file is in the same directory
- The script will process the transportation sheet and capture screenshots for each route

## How It Works:

1. **Reads your Excel data** - Same as your original script
2. **Opens Chrome browser** - Automatically controlled by Selenium
3. **Navigates to Google Maps** - For each site-to-warehouse route
4. **Waits for route to load** - Ensures the map shows the complete route
5. **Captures screenshot** - Saves as PNG file in `screenshots/` folder
6. **Repeats for all routes** - Processes every row in your transportation sheet

## Screenshot Features:

- **Route visualization** - Shows the actual driving route on the map
- **Distance information** - Displays total distance and travel time
- **Turn-by-turn directions** - Shows the route details in the sidebar
- **High-quality images** - Full browser window screenshots

## File Naming:
Screenshots will be named: `route_[SITE_ID]_to_[WAREHOUSE_NAME].png`

## Running the Script:
```bash
python map_screenshot.py
```

## Output:
- Screenshots saved in `screenshots/` folder
- Console output showing progress for each route
- Error handling for failed captures

## Troubleshooting:
- If Chrome doesn't open, make sure Chrome browser is installed
- If screenshots are blank, try increasing the wait time in the script
- If routes don't load, check your internet connection 