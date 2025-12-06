#!/usr/bin/env python3
"""
Create a simple portable distribution package
This creates a self-contained package that includes Python scripts and a launcher
"""

import os
import shutil
import zipfile
from pathlib import Path

def create_simple_distribution():
    """Create a simple portable distribution"""
    
    print("=" * 60)
    print("Creating Simple Portable Distribution Package")
    print("=" * 60)
    print()
    
    dist_dir = Path("dist_package")
    
    # Clean and create distribution directory
    if dist_dir.exists():
        print("[1/5] Cleaning existing distribution directory...")
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(exist_ok=True)
    
    print(f"[2/5] Copying application files...")
    # Copy main application
    shutil.copy2("app.py", dist_dir / "app.py")
    
    # Copy templates
    shutil.copytree("templates", dist_dir / "templates")
    
    print(f"[3/5] Creating directory structure...")
    (dist_dir / "instance").mkdir(exist_ok=True)
    (dist_dir / "uploads").mkdir(exist_ok=True)
    (dist_dir / "screenshots").mkdir(exist_ok=True)
    
    print(f"[4/5] Creating launcher and setup files...")
    
    # Create requirements.txt
    with open(dist_dir / "requirements.txt", 'w') as f:
        f.write("""Flask>=2.3.3
Flask-Login>=0.6.3
Flask-SQLAlchemy>=3.0.5
Werkzeug>=2.3.7
pandas>=2.2.0
openpyxl>=3.1.2
selenium>=4.15.2
webdriver-manager>=4.0.1
""")
    
    # Create setup script
    setup_bat = """@echo off
echo ========================================
echo Route Screenshot Generator - Setup
echo ========================================
echo.
echo This will install Python dependencies.
echo.
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo Python found!
echo.
echo Installing dependencies (this may take a few minutes)...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies!
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup complete!
echo ========================================
echo.
echo You can now run START_APP.bat to start the application.
echo.
pause
"""
    with open(dist_dir / "SETUP.bat", 'w') as f:
        f.write(setup_bat)
    
    # Create launcher
    launcher_bat = """@echo off
echo ========================================
echo Route Screenshot Generator
echo ========================================
echo.
echo Checking if dependencies are installed...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Dependencies not installed!
    echo.
    echo Please run SETUP.bat first to install dependencies.
    echo.
    pause
    exit /b 1
)

echo Dependencies OK!
echo.
echo Starting application...
echo.
echo The application will open in your browser at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the application
echo.
python app.py
pause
"""
    with open(dist_dir / "START_APP.bat", 'w') as f:
        f.write(launcher_bat)
    
    # Create comprehensive README
    readme_content = """# Route Screenshot Generator - Distribution Package

## Quick Start Guide

### First Time Setup (One-time only)

1. **Extract this ZIP file** to any folder on your computer
2. **Install Python** (if not already installed):
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"
   - Install Python 3.8 or higher
3. **Run SETUP.bat** (double-click it)
   - This will install all required dependencies
   - Wait for it to complete (may take a few minutes)
4. **Run START_APP.bat** to launch the application
5. **Open your browser** and go to: http://localhost:5000

### Daily Use

After the first setup, you only need to:
1. **Double-click START_APP.bat**
2. **Open your browser** at http://localhost:5000
3. **Use the application!**

## Requirements

- **Windows 10 or later**
- **Python 3.8 or higher** (download from python.org)
- **Google Chrome browser** (must be installed)
- **Internet connection** (for Google Maps)

## Excel File Format

Your Excel file must have exactly 3 sheets with these exact names:

### Sheet 1: "Transportation"
Required columns:
- `ID` - Unique identifier for each site
- `latitude` - Site latitude coordinate (decimal format)
- `longitude` - Site longitude coordinate (decimal format)
- `warehouse` - Warehouse name (must match warehouse sheet exactly)

Optional column:
- `intermediate_warehouse` - For 3-point routes (warehouse → intermediate → site)

### Sheet 2: "Warehouse"
Required columns:
- `Warehouse` - Warehouse name
- `latitude` - Warehouse latitude coordinate
- `longitude` - Warehouse longitude coordinate

### Sheet 3: "Region"
Required columns:
- `region` - Region name
- `warehouse` - Associated warehouse name

## Usage Steps

1. **Register/Login**: Create an account or log in
2. **Upload File**: Go to Upload page and select your Excel file (.xlsx)
3. **Monitor Progress**: Watch the progress bar on your dashboard
4. **Download Results**: When complete, download the ZIP file with all screenshots

## Troubleshooting

**"Python is not recognized" error:**
- Install Python from python.org
- Make sure to check "Add Python to PATH" during installation
- Restart your computer after installing Python

**"Dependencies not installed" error:**
- Run SETUP.bat first
- Make sure you have internet connection
- Try running as Administrator

**Application won't start:**
- Make sure Google Chrome is installed
- Check that no other application is using port 5000
- Try running START_APP.bat as Administrator

**Screenshots not generating:**
- Check your internet connection
- Verify coordinates in your Excel file are valid (test on Google Maps)
- Check that warehouse names match exactly (case-sensitive)
- Look at the console window for error messages

**Port already in use:**
- Close any other applications using port 5000
- Or contact your IT administrator

**"Module not found" errors:**
- Run SETUP.bat again to reinstall dependencies
- Make sure you're running START_APP.bat from the extracted folder

## File Locations

- Application files: In the extracted folder
- Database: `instance/routes.db` (user accounts and job history)
- Uploaded files: `uploads/` folder
- Screenshots: `screenshots/` folder

You can safely delete `instance/`, `uploads/`, and `screenshots/` folders to reset the application (this will delete all user data).

## Support

For technical help, contact your system administrator or IT support team.

## Notes

- The application runs locally on your computer
- All data is stored locally (no cloud storage)
- You need internet connection for Google Maps screenshots
- The application uses Chrome in headless mode (no visible browser window)
"""
    with open(dist_dir / "README.txt", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"[5/5] Creating ZIP archive...")
    zip_path = dist_dir.parent / "RouteScreenshotApp_Portable.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                if file.endswith('.zip'):
                    continue
                file_path = Path(root) / file
                arc_name = file_path.relative_to(dist_dir)
                zipf.write(file_path, arc_name)
    
    print()
    print("=" * 60)
    print("Distribution Package Created Successfully!")
    print("=" * 60)
    print()
    print(f"📦 Package location: {zip_path.absolute()}")
    print(f"📁 Unpacked location: {dist_dir.absolute()}")
    print()
    print("Ready to share with your team! 🚀")
    print()
    print("To share:")
    print(f"  1. Send the file: {zip_path.name}")
    print("  2. Tell your team to:")
    print("     - Extract the ZIP file")
    print("     - Install Python (if needed)")
    print("     - Run SETUP.bat (first time only)")
    print("     - Run START_APP.bat to use the app")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = create_simple_distribution()
        if not success:
            exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to create package: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

