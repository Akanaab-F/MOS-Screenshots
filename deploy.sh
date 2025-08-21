#!/bin/bash

# Production Deployment Script for Route Screenshot Generator
# This script sets up the application for production scaling

set -e

echo "🚀 Starting production deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker and Docker Compose are installed
check_dependencies() {
    print_status "Checking dependencies..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_status "Dependencies check passed ✓"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p logs/{nginx,redis,postgres}
    mkdir -p backups
    mkdir -p nginx/ssl
    mkdir -p monitoring/grafana/{dashboards,datasources}
    mkdir -p redis
    
    print_status "Directories created ✓"
}

# Setup environment variables
setup_environment() {
    print_status "Setting up environment variables..."
    
    if [ ! -f .env ]; then
        if [ -f env.example ]; then
            cp env.example .env
            print_warning "Created .env file from template. Please edit it with your production values."
        else
            print_error "env.example not found. Please create a .env file manually."
            exit 1
        fi
    else
        print_status ".env file already exists"
    fi
    
    # Check if SECRET_KEY is set
    if grep -q "your-super-secret-key-change-this" .env; then
        print_warning "Please update SECRET_KEY in .env file with a secure value"
    fi
}

# Generate SSL certificates (self-signed for development)
generate_ssl_certificates() {
    print_status "Generating SSL certificates..."
    
    if [ ! -f nginx/ssl/cert.pem ] || [ ! -f nginx/ssl/key.pem ]; then
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/ssl/key.pem \
            -out nginx/ssl/cert.pem \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"
        
        print_status "SSL certificates generated ✓"
        print_warning "Using self-signed certificates. For production, use proper SSL certificates."
    else
        print_status "SSL certificates already exist"
    fi
}

# Create Redis Sentinel configuration
create_redis_sentinel_config() {
    print_status "Creating Redis Sentinel configuration..."
    
    cat > redis/sentinel.conf << EOF
port 26379
sentinel monitor mymaster redis 6379 2
sentinel down-after-milliseconds mymaster 5000
sentinel failover-timeout mymaster 10000
sentinel parallel-syncs mymaster 1
EOF
    
    print_status "Redis Sentinel configuration created ✓"
}

# Create Prometheus configuration
create_prometheus_config() {
    print_status "Creating Prometheus configuration..."
    
    if [ ! -f monitoring/prometheus.yml ]; then
        print_error "Prometheus configuration not found. Please create monitoring/prometheus.yml"
        exit 1
    fi
    
    print_status "Prometheus configuration exists ✓"
}

# Initialize database
initialize_database() {
    print_status "Initializing database..."
    
    # Check if we're using PostgreSQL
    if grep -q "postgresql://" .env; then
        print_status "Using PostgreSQL database"
        # Database will be initialized by the PostgreSQL container
    else
        print_status "Using SQLite database"
        # SQLite database will be created automatically
    fi
}

# Build and start services
start_services() {
    print_status "Building and starting services..."
    
    # Build images
    docker-compose -f docker-compose.prod.yml build
    
    # Start services
    docker-compose -f docker-compose.prod.yml up -d
    
    print_status "Services started ✓"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."
    
    # Wait for PostgreSQL
    if grep -q "postgresql://" .env; then
        print_status "Waiting for PostgreSQL..."
        sleep 10
    fi
    
    # Wait for Redis
    print_status "Waiting for Redis..."
    sleep 5
    
    # Wait for web application
    print_status "Waiting for web application..."
    sleep 10
    
    print_status "Services are ready ✓"
}

# Run database migrations
run_migrations() {
    print_status "Running database migrations..."
    
    # Initialize migrations if needed
    docker-compose -f docker-compose.prod.yml exec web python migrations.py init 2>/dev/null || true
    
    # Run migrations
    docker-compose -f docker-compose.prod.yml exec web python migrations.py upgrade
    
    print_status "Database migrations completed ✓"
}

# Setup monitoring
setup_monitoring() {
    print_status "Setting up monitoring..."
    
    # Create Grafana datasource
    cat > monitoring/grafana/datasources/prometheus.yml << EOF
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF
    
    print_status "Monitoring setup completed ✓"
}

# Health check
health_check() {
    print_status "Performing health check..."
    
    # Check if web application is responding
    if curl -f -s http://localhost/health > /dev/null; then
        print_status "Web application health check passed ✓"
    else
        print_warning "Web application health check failed. Check logs with: docker-compose -f docker-compose.prod.yml logs web"
    fi
    
    # Check if Prometheus is responding
    if curl -f -s http://localhost:9090 > /dev/null; then
        print_status "Prometheus health check passed ✓"
    else
        print_warning "Prometheus health check failed"
    fi
    
    # Check if Grafana is responding
    if curl -f -s http://localhost:3000 > /dev/null; then
        print_status "Grafana health check passed ✓"
    else
        print_warning "Grafana health check failed"
    fi
}

# Display deployment information
display_info() {
    echo ""
    echo "🎉 Deployment completed successfully!"
    echo ""
    echo "📋 Service URLs:"
    echo "   Web Application: https://localhost"
    echo "   Grafana Dashboard: http://localhost:3000 (admin/admin)"
    echo "   Prometheus: http://localhost:9090"
    echo ""
    echo "📊 Monitoring:"
    echo "   - Grafana: http://localhost:3000"
    echo "   - Prometheus: http://localhost:9090"
    echo ""
    echo "🔧 Useful commands:"
    echo "   View logs: docker-compose -f docker-compose.prod.yml logs -f"
    echo "   Scale web: docker-compose -f docker-compose.prod.yml up -d --scale web=5"
    echo "   Scale celery: docker-compose -f docker-compose.prod.yml up -d --scale celery=3"
    echo "   Backup: docker-compose -f docker-compose.prod.yml exec backup python backup.py"
    echo "   Cleanup: python cleanup.py --all"
    echo ""
    echo "⚠️  Important:"
    echo "   - Update .env file with production values"
    echo "   - Replace self-signed SSL certificates with proper ones"
    echo "   - Set up proper backup strategy"
    echo "   - Configure monitoring alerts"
    echo ""
}

# Main deployment function
main() {
    check_dependencies
    create_directories
    setup_environment
    generate_ssl_certificates
    create_redis_sentinel_config
    create_prometheus_config
    initialize_database
    start_services
    wait_for_services
    run_migrations
    setup_monitoring
    health_check
    display_info
}

# Run main function
main "$@"
