@echo off
echo ========================================
echo Building Route Screenshot App Executable
echo ========================================
echo.
echo This will take 5-15 minutes. Please be patient!
echo.
echo Building executable...
echo.

pyinstaller --onefile ^
    --name RouteScreenshotApp ^
    --add-data "templates;templates" ^
    --hidden-import flask ^
    --hidden-import flask_login ^
    --hidden-import flask_sqlalchemy ^
    --hidden-import werkzeug.security ^
    --hidden-import werkzeug.utils ^
    --hidden-import pandas ^
    --hidden-import openpyxl ^
    --hidden-import selenium ^
    --hidden-import selenium.webdriver ^
    --hidden-import selenium.webdriver.chrome ^
    --hidden-import selenium.webdriver.chrome.options ^
    --hidden-import selenium.webdriver.common.by ^
    --hidden-import selenium.webdriver.support.ui ^
    --hidden-import selenium.webdriver.support.expected_conditions ^
    --hidden-import selenium.common.exceptions ^
    --hidden-import webdriver_manager ^
    --hidden-import sqlalchemy ^
    --hidden-import jinja2 ^
    --console ^
    --clean ^
    app.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Build completed successfully!
    echo ========================================
    echo.
    echo Executable location: dist\RouteScreenshotApp.exe
    echo.
    echo You can now run: python create_distribution.py
    echo to create the distribution package.
    echo.
) else (
    echo.
    echo ========================================
    echo Build failed!
    echo ========================================
    echo.
    echo Please check the error messages above.
    echo.
)

pause

