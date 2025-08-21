import os
import uuid
import zipfile
import re
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import pandas as pd
from celery import Celery
import redis
from dotenv import load_dotenv
from models import db, User, Job
from monitoring import monitor_request, metrics_endpoint, log_file_upload, log_job_event

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
if not app.config['SECRET_KEY']:
    raise ValueError("SECRET_KEY environment variable is required")

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///routes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SCREENSHOTS_FOLDER'] = 'screenshots'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SCREENSHOTS_FOLDER'], exist_ok=True)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Celery configuration
celery = Celery('routes', broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
celery.conf.update(app.config)

# Rate limiting configuration
RATE_LIMIT_UPLOADS = 5  # Max uploads per hour per user
RATE_LIMIT_WINDOW = 3600  # 1 hour in seconds

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
@monitor_request
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return metrics_endpoint()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # Input validation
        if not username or len(username) < 3 or len(username) > 20:
            flash('Username must be between 3 and 20 characters')
            return render_template('register.html')
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            flash('Username can only contain letters, numbers, and underscores')
            return render_template('register.html')
        
        if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            flash('Please enter a valid email address')
            return render_template('register.html')
        
        if not password or len(password) < 6:
            flash('Password must be at least 6 characters long')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered')
            return render_template('register.html')
        
        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        
        # Input validation
        if not username or not password:
            flash('Please enter both username and password')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    jobs = Job.query.filter_by(user_id=current_user.id).order_by(Job.created_at.desc()).all()
    return render_template('dashboard.html', jobs=jobs)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
@monitor_request
def upload():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        # Check rate limit
        if not check_rate_limit(current_user.id):
            flash(f'Upload rate limit exceeded. You can upload up to {RATE_LIMIT_UPLOADS} files per hour.')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{current_user.id}_{filename}")
            file.save(filepath)
            
            # Log file upload
            log_file_upload(filename, file.content_length or 0, current_user.id)
            
            # Validate Excel file structure
            is_valid, message = validate_excel_structure(filepath)
            if not is_valid:
                # Clean up invalid file
                try:
                    os.remove(filepath)
                except:
                    pass
                flash(f'Invalid file structure: {message}')
                return redirect(request.url)
            
            # Create job
            job = Job(
                user_id=current_user.id,
                job_id=str(uuid.uuid4()),
                filename=filename
            )
            db.session.add(job)
            db.session.commit()
            
            # Log job creation
            log_job_event(job.job_id, 'created', user_id=current_user.id, filename=filename)
            
            # Start background processing
            process_routes.delay(job.job_id, filepath)
            
            flash('File uploaded successfully! Processing started.')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid file type or filename. Please upload a valid Excel file (.xlsx or .xls)')
    
    return render_template('upload.html')

@app.route('/job/<job_id>')
@login_required
def job_status(job_id):
    job = Job.query.filter_by(job_id=job_id, user_id=current_user.id).first()
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    
    return jsonify({
        'status': job.status,
        'progress': job.progress,
        'total_routes': job.total_routes,
        'completed_routes': job.completed_routes,
        'error_message': job.error_message
    })

@app.route('/download/<job_id>')
@login_required
def download_results(job_id):
    job = Job.query.filter_by(job_id=job_id, user_id=current_user.id).first()
    if not job or job.status != 'completed':
        flash('Results not ready or job not found')
        return redirect(url_for('dashboard'))
    
    if job.result_file and os.path.exists(job.result_file):
        return send_file(job.result_file, as_attachment=True)
    else:
        flash('Result file not found')
        return redirect(url_for('dashboard'))

def allowed_file(filename):
    """Validate file type and name for security"""
    if not filename or '.' not in filename:
        return False
    
    # Check file extension
    allowed_extensions = {'xlsx', 'xls'}
    extension = filename.rsplit('.', 1)[1].lower()
    if extension not in allowed_extensions:
        return False
    
    # Validate filename (no path traversal, reasonable length)
    if len(filename) > 255 or '/' in filename or '\\' in filename:
        return False
    
    # Check for suspicious patterns
    suspicious_patterns = ['..', '~', ';', '|', '&', '>', '<']
    for pattern in suspicious_patterns:
        if pattern in filename:
            return False
    
    return True

def validate_excel_structure(filepath):
    """Validate that the Excel file has the required sheets and columns"""
    try:
        # Check if file exists and is readable
        if not os.path.exists(filepath):
            return False, "File not found"
        
        # Try to read the Excel file
        excel_file = pd.ExcelFile(filepath)
        
        # Check required sheets
        required_sheets = ['transportation', 'warehouse', 'region']
        missing_sheets = [sheet for sheet in required_sheets if sheet not in excel_file.sheet_names]
        if missing_sheets:
            return False, f"Missing required sheets: {', '.join(missing_sheets)}"
        
        # Check transportation sheet columns
        try:
            transportation_df = pd.read_excel(filepath, sheet_name="transportation", engine="openpyxl")
            required_columns = ['ID', 'latitude', 'longitude', 'warehouse']
            missing_columns = [col for col in required_columns if col not in transportation_df.columns]
            if missing_columns:
                return False, f"Missing required columns in transportation sheet: {', '.join(missing_columns)}"
        except Exception as e:
            return False, f"Error reading transportation sheet: {str(e)}"
        
        # Check warehouse sheet columns
        try:
            warehouse_df = pd.read_excel(filepath, sheet_name="warehouse", engine="openpyxl")
            required_columns = ['Warehouse', 'latitude', 'longitude']
            missing_columns = [col for col in required_columns if col not in warehouse_df.columns]
            if missing_columns:
                return False, f"Missing required columns in warehouse sheet: {', '.join(missing_columns)}"
        except Exception as e:
            return False, f"Error reading warehouse sheet: {str(e)}"
        
        # Check region sheet columns
        try:
            region_df = pd.read_excel(filepath, sheet_name="region", engine="openpyxl")
            required_columns = ['region', 'warehouse']
            missing_columns = [col for col in required_columns if col not in region_df.columns]
            if missing_columns:
                return False, f"Missing required columns in region sheet: {', '.join(missing_columns)}"
        except Exception as e:
            return False, f"Error reading region sheet: {str(e)}"
        
        return True, "File structure is valid"
        
    except Exception as e:
        return False, f"Error validating file: {str(e)}"

def check_rate_limit(user_id):
    """Check if user has exceeded upload rate limit"""
    try:
        # Get recent uploads for this user
        one_hour_ago = datetime.utcnow() - timedelta(seconds=RATE_LIMIT_WINDOW)
        recent_uploads = Job.query.filter(
            Job.user_id == user_id,
            Job.created_at >= one_hour_ago
        ).count()
        
        return recent_uploads < RATE_LIMIT_UPLOADS
    except Exception:
        # If there's an error checking rate limit, allow the upload
        return True

# Celery task for background processing
@celery.task
def process_routes(job_id, filepath):
    from map_screenshot_parallel import process_material_excel_linear
    
    job = Job.query.filter_by(job_id=job_id).first()
    if not job:
        return
    
    try:
        job.status = 'processing'
        db.session.commit()
        
        # Process the file
        result_file = process_material_excel_linear(filepath, job_id)
        
        job.status = 'completed'
        job.completed_at = datetime.utcnow()
        job.result_file = result_file
        db.session.commit()
        
        # Clean up uploaded file after processing
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as cleanup_error:
            print(f"Warning: Could not clean up file {filepath}: {cleanup_error}")
        
    except Exception as e:
        job.status = 'failed'
        job.error_message = str(e)
        db.session.commit()
        
        # Clean up uploaded file even if processing failed
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as cleanup_error:
            print(f"Warning: Could not clean up file {filepath}: {cleanup_error}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000) 