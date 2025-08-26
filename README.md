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
   git clone https://github.com/Akanaab-F/MOS-Screenshots.git
   cd MOS-Screenshots
   ```

2. **Start the application**
   ```bash
   # Windows
   start.bat
   
   # Linux/Mac
   docker-compose up -d
   ```

3. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - Register a new account
   - Upload your Excel file and start processing

### Option 2: Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/Akanaab-F/MOS-Screenshots.git
   cd MOS-Screenshots
   ```

2. **Start locally (Windows)**
   ```bash
   start_local.bat
   ```

3. **Or manually:**
   ```bash
   # Create virtual environment
   python -m venv .venv
   .venv\Scripts\activate     # Windows
   
   # Install dependencies
   pip install -r requirements.txt
   
   # Run the application
   python app.py
   ```

4. **Access the application**
   - Open your browser and go to `http://localhost:5000`
   - Register a new account
   - Upload your Excel file and start processing
   - **Note**: Chrome browser will open for cookie consent handling

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

The application is designed to scale horizontally. Here are the scaling options:

### Quick Scaling

1. **Scale web servers**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --scale web=5
   ```

2. **Scale Celery workers**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --scale celery=3
   ```

3. **Scale both**:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --scale web=5 --scale celery=3
   ```

### Production Scaling

For production deployment with full scaling capabilities:

1. **Run the production deployment script**:
   ```bash
   ./deploy.sh
   ```

2. **Manual scaling with resource limits**:
   ```bash
   # Scale web servers with resource limits
   docker-compose -f docker-compose.prod.yml up -d --scale web=3
   
   # Scale Celery workers with resource limits
   docker-compose -f docker-compose.prod.yml up -d --scale celery=2
   ```

3. **Database scaling**:
   - Use PostgreSQL with connection pooling
   - Set up read replicas for read-heavy workloads
   - Use Redis clustering for high availability

4. **Load balancer scaling**:
   - Nginx automatically load balances between web instances
   - Configure additional Nginx instances for high availability
   - Use external load balancers (AWS ALB, GCP LB, etc.)

### Monitoring Scaling

Monitor your scaling with:

- **Grafana Dashboard**: http://localhost:3000 (admin/admin)
- **Prometheus Metrics**: http://localhost:9090
- **Application Metrics**: https://localhost/metrics

### Auto-scaling

For automatic scaling based on load:

1. **Set up monitoring alerts** in Grafana
2. **Use Kubernetes** for container orchestration
3. **Implement horizontal pod autoscaling** (HPA)
4. **Use cloud auto-scaling groups** (AWS, GCP, Azure)

## Architecture

- **Flask**: Web framework
- **SQLAlchemy**: Database ORM
- **Celery**: Background task processing
- **Redis**: Message broker and cache
- **Selenium**: Web automation for screenshots
- **Bootstrap**: Frontend framework

## Security Features

- User authentication and authorization
- Secure file upload validation with comprehensive checks
- User data isolation
- CSRF protection
- Input sanitization
- Rate limiting (5 uploads per hour per user)
- Environment variable configuration for secrets
- File type and structure validation
- Automatic cleanup of uploaded files after processing

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