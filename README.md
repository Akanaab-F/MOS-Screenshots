# Route Screenshot Generator

A scalable web application that automatically generates Google Maps route screenshots from Excel data. Perfect for logistics, transportation planning, and route analysis.

## Features

- **Multi-user Support**: Each user has their own workspace and job history
- **Real-time Progress Tracking**: Monitor job progress with live updates
- **Background Processing**: Jobs run in the background using Celery
- **User-friendly Interface**: Modern, responsive web interface
- **File Validation**: Automatic validation of Excel file format and structure
- **Secure File Handling**: Files are processed securely with user isolation
- **Mobile-friendly**: Works on desktop and mobile devices

## Quick Start

### Option 1: Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd route-screenshot-generator
   ```

2. **Start the application**
   ```bash
   docker-compose up -d
   ```

3. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - Register a new account
   - Upload your Excel file and start processing

### Option 2: Local Development

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Chrome browser** (if not already installed)

3. **Set up environment variables**
   ```bash
   export SECRET_KEY="your-secret-key-here"
   export DATABASE_URL="sqlite:///routes.db"
   export REDIS_URL="redis://localhost:6379/0"
   ```

4. **Start Redis** (required for background processing)
   ```bash
   redis-server
   ```

5. **Start the application**
   ```bash
   python app.py
   ```

6. **Start Celery worker** (in a separate terminal)
   ```bash
   celery -A app.celery worker --loglevel=info
   ```

## Excel File Format

Your Excel file must contain the following sheets:

### Transportation Sheet
| Column | Description | Required |
|--------|-------------|----------|
| ID | Unique identifier for each site | Yes |
| latitude | Site latitude coordinate | Yes |
| longitude | Site longitude coordinate | Yes |
| warehouse | Warehouse name (must match warehouse sheet) | Yes |

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

1. **Use a production database** (PostgreSQL, MySQL) instead of SQLite
2. **Set up proper SSL/TLS certificates**
3. **Configure a reverse proxy** (Nginx, Apache)
4. **Use environment variables** for sensitive configuration
5. **Set up monitoring and logging**

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| SECRET_KEY | Flask secret key | `your-secret-key-here` |
| DATABASE_URL | Database connection string | `sqlite:///routes.db` |
| REDIS_URL | Redis connection string | `redis://localhost:6379/0` |
| FLASK_ENV | Flask environment | `production` |

### Scaling

To scale the application:

1. **Add more Celery workers**:
   ```bash
   celery -A app.celery worker --loglevel=info --concurrency=4
   ```

2. **Use multiple web servers** behind a load balancer

3. **Use a production database** with connection pooling

4. **Set up Redis clustering** for high availability

## Architecture

- **Flask**: Web framework
- **SQLAlchemy**: Database ORM
- **Celery**: Background task processing
- **Redis**: Message broker and cache
- **Selenium**: Web automation for screenshots
- **Bootstrap**: Frontend framework

## Security Features

- User authentication and authorization
- Secure file upload validation
- User data isolation
- CSRF protection
- Input sanitization

## Troubleshooting

### Common Issues

1. **Chrome not starting**: Ensure Chrome is installed and accessible
2. **Screenshots not generating**: Check internet connection and Google Maps accessibility
3. **Jobs stuck in processing**: Restart Celery workers
4. **Database errors**: Check database connection and permissions

### Logs

Check the following logs for debugging:
- Application logs: `docker-compose logs web`
- Celery logs: `docker-compose logs celery`
- Redis logs: `docker-compose logs redis`

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