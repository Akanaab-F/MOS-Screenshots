#!/usr/bin/env python3
"""
Monitoring and logging configuration for Route Screenshot Generator
Includes Prometheus metrics and structured logging
"""

import time
import structlog
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from flask import request, Response
from functools import wraps

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Prometheus metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_DURATION = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

ACTIVE_JOBS = Gauge(
    'active_jobs_total',
    'Total number of active jobs'
)

COMPLETED_JOBS = Counter(
    'completed_jobs_total',
    'Total number of completed jobs',
    ['status']
)

UPLOAD_SIZE = Histogram(
    'file_upload_size_bytes',
    'File upload size in bytes'
)

SCREENSHOT_DURATION = Histogram(
    'screenshot_capture_duration_seconds',
    'Screenshot capture duration in seconds'
)

def monitor_request(f):
    """Decorator to monitor HTTP requests"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        
        # Log request
        logger.info(
            "Request started",
            method=request.method,
            endpoint=request.endpoint,
            ip=request.remote_addr,
            user_agent=request.user_agent.string
        )
        
        try:
            response = f(*args, **kwargs)
            status_code = response.status_code if hasattr(response, 'status_code') else 200
            
            # Record metrics
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.endpoint,
                status=status_code
            ).inc()
            
            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=request.endpoint
            ).observe(time.time() - start_time)
            
            # Log successful request
            logger.info(
                "Request completed",
                method=request.method,
                endpoint=request.endpoint,
                status_code=status_code,
                duration=time.time() - start_time
            )
            
            return response
            
        except Exception as e:
            # Record error metrics
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.endpoint,
                status=500
            ).inc()
            
            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=request.endpoint
            ).observe(time.time() - start_time)
            
            # Log error
            logger.error(
                "Request failed",
                method=request.method,
                endpoint=request.endpoint,
                error=str(e),
                duration=time.time() - start_time
            )
            raise
    
    return decorated_function

def metrics_endpoint():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

def update_job_metrics():
    """Update job-related metrics"""
    from models import Job
    from app import db
    
    with db.app.app_context():
        # Count active jobs
        active_count = Job.query.filter_by(status='processing').count()
        ACTIVE_JOBS.set(active_count)
        
        # Count completed jobs by status
        completed_count = Job.query.filter_by(status='completed').count()
        failed_count = Job.query.filter_by(status='failed').count()
        
        COMPLETED_JOBS.labels(status='completed').inc(completed_count)
        COMPLETED_JOBS.labels(status='failed').inc(failed_count)

def log_job_event(job_id, event, **kwargs):
    """Log job-related events"""
    logger.info(
        f"Job {event}",
        job_id=job_id,
        **kwargs
    )

def log_screenshot_event(site_id, duration, success, error=None):
    """Log screenshot capture events"""
    if success:
        logger.info(
            "Screenshot captured",
            site_id=site_id,
            duration=duration
        )
        SCREENSHOT_DURATION.observe(duration)
    else:
        logger.error(
            "Screenshot failed",
            site_id=site_id,
            duration=duration,
            error=error
        )

def log_file_upload(filename, size, user_id):
    """Log file upload events"""
    logger.info(
        "File uploaded",
        filename=filename,
        size=size,
        user_id=user_id
    )
    UPLOAD_SIZE.observe(size)
