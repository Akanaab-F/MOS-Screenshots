#!/usr/bin/env python3
"""
Create a distribution package for Route Screenshot Generator
This script packages the executable and all necessary files for distribution
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
    
    # Define paths
    dist_dir = Path("dist_package")
    build_dir = Path("dist")
    package_name = "RouteScreenshotApp"
    
    # Clean and create distribution directory
    if dist_dir.exists():
        print("[1/6] Cleaning existing distribution directory...")
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(exist_ok=True)
    
    # Check if executable exists
    exe_path = build_dir / f"{package_name}.exe"
    if not exe_path.exists():
        print(f"[ERROR] Executable not found: {exe_path}")
        print("Please run: pyinstaller build_distribution.spec --clean")
        print("Then run this script again.")
        return False
    
    print(f"[2/6] Copying executable...")
    shutil.copy2(exe_path, dist_dir / f"{package_name}.exe")
    
    print(f"[3/6] Creating directory structure...")
    (dist_dir / "instance").mkdir(exist_ok=True)
    (dist_dir / "uploads").mkdir(exist_ok=True)
    (dist_dir / "screenshots").mkdir(exist_ok=True)
    
    # Create .gitkeep files to preserve directory structure
    for dir_name in ["instance", "uploads", "screenshots"]:
        (dist_dir / dir_name / ".gitkeep").touch()
    
    print(f"[4/6] Creating launcher script...")
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
    with open(dist_dir / "START_APP.bat", 'w') as f:
        f.write(launcher_content)
    
    print(f"[5/6] Creating README...")
    readme_content = """# Route Screenshot Generator - Distribution Package

## Quick Start

1. **Extract this ZIP file** to any folder on your computer
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

**Port already in use:**
- Close any other applications using port 5000
- Or contact your IT administrator

## Support

For help, contact your system administrator or IT support team.

## Notes

- The application runs locally on your computer
- All data is stored locally in the `instance/` folder
- Uploaded files are stored in the `uploads/` folder
- Screenshots are stored in the `screenshots/` folder
- You can safely delete these folders to reset the application
"""
    with open(dist_dir / "README.txt", 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"[6/6] Creating ZIP archive...")
    zip_path = dist_dir.parent / f"{package_name}_Distribution.zip"
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add all files in dist_package
        for root, dirs, files in os.walk(dist_dir):
            for file in files:
                if file.endswith('.zip'):
                    continue  # Skip the zip file itself
                file_path = Path(root) / file
                arc_name = file_path.relative_to(dist_dir)
                zipf.write(file_path, arc_name)
                print(f"        ✓ Added {arc_name}")
    
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
    print("  2. Tell your team to extract it and run START_APP.bat")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = create_distribution()
        if not success:
            exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to create package: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

