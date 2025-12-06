# Route Screenshot Generator

A scalable web application that automatically generates Google Maps route screenshots from Excel data. Perfect for logistics, transportation planning, and route analysis.

## Features

- **Multi-user Support**: Each user has their own workspace and job history
- **Real-time Progress Tracking**: Monitor job progress with live updates
- **Background Processing**: Jobs run in the background using threading
- **User-friendly Interface**: Modern, responsive web interface
- **File Validation**: Automatic validation of Excel file format and structure
- **Secure File Handling**: Files are processed securely with user isolation
- **Mobile-friendly**: Works on desktop and mobile devices

## Quick Start

### Prerequisites

- Python 3.8 or higher
- Google Chrome browser installed
- ChromeDriver (automatically managed by webdriver-manager)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Akanaab-F/MOS-Screenshots.git
   cd MOS-Screenshots
   ```

2. **Create virtual environment** (recommended)
   ```bash
   # Windows
   python -m venv .venv
   .venv\Scripts\activate
   
   # Linux/Mac
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   # Windows
   start.bat
   
   # Or manually
   python app.py
   ```

5. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - Register a new account
   - Upload your Excel file and start processing
   - **Note**: Chrome browser will be used in headless mode for screenshot generation

## Excel File Format

Your Excel file must contain the following sheets:

### Transportation Sheet
| Column | Description | Required |
|--------|-------------|----------|
| ID | Unique identifier for each site | Yes |
| latitude | Site latitude coordinate | Yes |
| longitude | Site longitude coordinate | Yes |
| warehouse | Warehouse name (must match warehouse sheet) | Yes |
| intermediate_warehouse | Optional intermediate warehouse name for 3-point routes (warehouse → intermediate_warehouse → site) | No |

### Warehouse Sheet
| Column | Description | Required |
|--------|-------------|----------|
| Warehouse | Warehouse name | Yes |
| latitude | Warehouse latitude coordinate | Yes |
| longitude | Warehouse longitude coordinate | Yes |

### Region Sheet
| Column | Description | Required |
|--------|-------------|----------|
| region | Region name | Yes |
| warehouse | Associated warehouse name | Yes |

## Usage

1. **Register/Login**: Create an account or log in to your existing account
2. **Upload File**: Go to the upload page and select your Excel file
3. **Monitor Progress**: Track the processing progress on your dashboard
4. **Download Results**: Once complete, download the ZIP file containing all route screenshots

## Deployment

### Production Deployment

For production deployment, consider the following:

1. **Set a strong SECRET_KEY** using environment variables
2. **Use a production WSGI server** like Gunicorn or Waitress
3. **Set up proper SSL/TLS certificates**
4. **Configure a reverse proxy** (Nginx, Apache) if needed
5. **Set up monitoring and logging**

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| SECRET_KEY | Flask secret key | `your-secret-key-here` |

Set the secret key before running in production:
```bash
# Windows
set SECRET_KEY=your-super-secret-key-here
python app.py

# Linux/Mac
export SECRET_KEY=your-super-secret-key-here
python app.py
```

### Running with a Production WSGI Server

For production, use a proper WSGI server instead of Flask's development server:

**Using Waitress (Windows-friendly):**
```bash
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 app:app
```

**Using Gunicorn (Linux/Mac):**
```bash
pip install gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

## Architecture

- **Flask**: Web framework
- **SQLAlchemy**: Database ORM (SQLite)
- **Threading**: Background task processing
- **Selenium**: Web automation for screenshots
- **Bootstrap**: Frontend framework

## Security Features

- User authentication and authorization
- Secure file upload validation with comprehensive checks
- User data isolation
- Input sanitization
- Environment variable configuration for secrets
- File type and structure validation

## Troubleshooting

### Common Issues

1. **Chrome not starting**: 
   - Ensure Chrome is installed and accessible
   - Check that ChromeDriver is compatible with your Chrome version
   - The webdriver-manager package should handle this automatically

2. **Screenshots not generating**: 
   - Check internet connection and Google Maps accessibility
   - Verify that coordinates in your Excel file are valid
   - Check the application console for error messages

3. **Jobs stuck in processing**: 
   - Restart the application
   - Check the console for error messages
   - Verify that Chrome is not blocked by firewall

4. **Database errors**: 
   - Check that the `instance/` directory exists and is writable
   - Delete `instance/routes.db` to reset the database (this will delete all user data)

5. **Port already in use**: 
   - Change the port in `app.py` (line 549) from 5000 to another port
   - Or stop the process using port 5000

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the documentation

## Roadmap

- [ ] Add support for multiple map providers
- [ ] Implement batch processing optimization
- [ ] Add API endpoints for integration
- [ ] Support for custom map styles
- [ ] Advanced reporting features 