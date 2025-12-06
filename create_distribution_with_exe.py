#!/usr/bin/env python3
"""
Create a distribution package with executable (if available)
"""

import os
import shutil
import zipfile
from pathlib import Path

def create_distribution():
    """Create the distribution package"""
    
    print("=" * 60)
    print("Creating Route Screenshot Generator Distribution Package")
    print("=" * 60)
    print()
    
    dist_dir = Path("dist_package")
    build_dir = Path("dist")
    package_name = "RouteScreenshotApp"
    exe_path = build_dir / f"{package_name}.exe"
    
    # Clean and create distribution directory
    if dist_dir.exists():
        print("[1/7] Cleaning existing distribution directory...")
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(exist_ok=True)
    
    # Check if executable exists
    has_exe = exe_path.exists()
    
    if has_exe:
        print(f"[2/7] Copying executable...")
        shutil.copy2(exe_path, dist_dir / f"{package_name}.exe")
        print(f"        ✓ Executable found: {exe_path.name}")
    else:
        print(f"[2/7] Executable not found, creating portable package...")
        print(f"        ℹ️  Will include Python scripts instead")
        shutil.copy2("app.py", dist_dir / "app.py")
        shutil.copytree("templates", dist_dir / "templates")
        
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
    
    print(f"[3/7] Creating directory structure...")
    (dist_dir / "instance").mkdir(exist_ok=True)
    (dist_dir / "uploads").mkdir(exist_ok=True)
    (dist_dir / "screenshots").mkdir(exist_ok=True)
    
    print(f"[4/7] Creating launcher script...")
    if has_exe:
        launcher_content = """@echo off
echo ========================================
echo Route Screenshot Generator
echo ========================================
echo.
echo Starting application...
echo.
echo The application will open in your browser at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the application
echo.
RouteScreenshotApp.exe
pause
"""
    else:
        launcher_content = """@echo off
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
        f.write(launcher_content)
    
    if not has_exe:
        print(f"[5/7] Creating setup script...")
        setup_bat = """@echo off
echo ========================================
echo Route Screenshot Generator - Setup
echo ========================================
echo.
echo This will install Python dependencies.
echo.
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo.
    echo Please install Python 3.8 or higher from:
    echo https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo Setup complete! You can now run START_APP.bat
pause
"""
        with open(dist_dir / "SETUP.bat", 'w') as f:
            f.write(setup_bat)
    
    print(f"[6/7] Creating README...")
    if has_exe:
        readme_content = """# Route Screenshot Generator - Standalone Application

## Quick Start

1. **Extract this ZIP file** to any folder
2. **Double-click** `START_APP.bat` to launch the application
3. **Open your browser** and go to: http://localhost:5000
4. **Register** a new account or log in
5. **Upload** your Excel file and start processing

## Requirements

- **Windows 10 or later**
- **Google Chrome browser** (must be installed)
- **Internet connection** (for Google Maps)

## Excel File Format

Your Excel file must have 3 sheets:

### Sheet 1: "Transportation"
- `ID` - Unique identifier for each site
- `latitude` - Site latitude coordinate
- `longitude` - Site longitude coordinate  
- `warehouse` - Warehouse name (must match warehouse sheet)
- `intermediate_warehouse` - (Optional) For 3-point routes

### Sheet 2: "Warehouse"
- `Warehouse` - Warehouse name
- `latitude` - Warehouse latitude coordinate
- `longitude` - Warehouse longitude coordinate

### Sheet 3: "Region"
- `region` - Region name
- `warehouse` - Associated warehouse name

## Usage

1. Register/Login to create an account
2. Upload your Excel file (.xlsx format)
3. Monitor progress on your dashboard
4. Download the ZIP file with all route screenshots when complete

## Troubleshooting

**Application won't start:**
- Make sure Google Chrome is installed
- Check that no other application is using port 5000
- Try running as Administrator

**Screenshots not generating:**
- Check your internet connection
- Verify coordinates in your Excel file are valid
- Check that warehouse names match exactly

## Support

For help, contact your system administrator or IT support team.
"""
    else:
        readme_content = """# Route Screenshot Generator - Portable Package

## Quick Start

### First Time Setup

1. **Extract this ZIP file** to any folder
2. **Install Python** (if not already installed) from python.org
3. **Run SETUP.bat** (one-time setup)
4. **Run START_APP.bat** to launch the application
5. **Open your browser** at http://localhost:5000

### Daily Use

After setup, just run `START_APP.bat` each time.

## Requirements

- **Windows 10 or later**
- **Python 3.8 or higher**
- **Google Chrome browser**
- **Internet connection**

See README.txt for full instructions.
"""
    
    with open(dist_dir / "README.txt", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"[7/7] Creating ZIP archive...")
    zip_name = f"{package_name}_Standalone.zip" if has_exe else f"{package_name}_Portable.zip"
    zip_path = dist_dir.parent / zip_name
    
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
    print(f"📦 Package: {zip_path.name}")
    print(f"📁 Location: {zip_path.absolute()}")
    print()
    if has_exe:
        print("✅ Standalone executable included - no Python needed!")
    else:
        print("ℹ️  Portable package - requires Python installation")
    print()
    print("Ready to share with your team! 🚀")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = create_distribution()
        if not success:
            exit(1)
    except Exception as e:
        print(f"[ERROR] Failed: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

