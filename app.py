#!/usr/bin/env python3
"""
Route Screenshot Generator - Fixed Version
This version handles cookie consent and fixes progress updates
"""

import os
import uuid
import zipfile
import threading
import time
import queue
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import json

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Use absolute path for database
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance', 'routes.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Database setup
db = SQLAlchemy(app)

# Login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Background processing
task_queue = queue.Queue()
worker_thread = None
worker_running = False

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    jobs = db.relationship('Job', backref='user', lazy=True)
    
    # Flask-Login required properties
    @property
    def is_active(self):
        return True
    
    @property
    def is_authenticated(self):
        return True
    
    @property
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.String(36), unique=True, nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, processing, completed, failed
    progress = db.Column(db.Integer, default=0)
    total_routes = db.Column(db.Integer, default=0)
    completed_routes = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    result_file = db.Column(db.String(255))

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def handle_cookie_consent(driver):
    """Handle Google cookie consent dialog"""
    try:
        # Wait for cookie consent dialog to appear
        wait = WebDriverWait(driver, 10)
        
        # Try to find and click "Accept all" button
        try:
            accept_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept all')]"))
            )
            accept_button.click()
            print("✅ Cookie consent accepted automatically")
            time.sleep(2)
            return True
        except TimeoutException:
            pass
        
        # Try alternative selectors for accept button
        try:
            accept_button = driver.find_element(By.XPATH, "//button[contains(@aria-label, 'Accept')]")
            accept_button.click()
            print("✅ Cookie consent accepted (alternative method)")
            time.sleep(2)
            return True
        except NoSuchElementException:
            pass
        
        # If no accept button found, try to find and click "Reject all"
        try:
            reject_button = driver.find_element(By.XPATH, "//button[contains(., 'Reject all')]")
            reject_button.click()
            print("✅ Cookie consent rejected")
            time.sleep(2)
            return True
        except NoSuchElementException:
            pass
        
        print("⚠️ No cookie consent dialog found or handled")
        return False
        
    except Exception as e:
        print(f"⚠️ Error handling cookie consent: {e}")
        return False

def process_screenshots_worker():
    """Background worker for processing screenshots"""
    global worker_running
    
    print("🔄 Background worker started and ready to process tasks")
    
    while worker_running:
        try:
            # Get task from queue
            task = task_queue.get(timeout=2)
            if task is None:
                break
            
            job_id, filepath = task
            print(f"🔄 Processing job: {job_id}")
            
            # Verify database connection
            try:
                with app.app_context():
                    # Test database connection
                    from sqlalchemy import text
                    db.session.execute(text("SELECT 1"))
                    print("✅ Database connection verified")
                    
                    # Test job retrieval
                    job = Job.query.filter_by(job_id=job_id).first()
                    if job:
                        print(f"✅ Found job: {job.job_id} - Status: {job.status}")
                    else:
                        print(f"❌ Job not found: {job_id}")
                        continue
                        
            except Exception as e:
                print(f"❌ Database connection failed: {e}")
                continue
            
            try:
                with app.app_context():
                    job = Job.query.filter_by(job_id=job_id).first()
                    if not job:
                        continue
                    
                    job.status = 'processing'
                    job.progress = 0
                    job.completed_routes = 0
                    db.session.commit()
                
                # Read Excel file
                excel_data = pd.read_excel(filepath, sheet_name=None)
                
                # Validate required sheets
                required_sheets = ['Transportation', 'Warehouse', 'Region']
                for sheet in required_sheets:
                    if sheet not in excel_data:
                        raise ValueError(f"Missing required sheet: {sheet}")
                
                # Process data
                transportation_df = excel_data['Transportation']
                warehouse_df = excel_data['Warehouse']
                region_df = excel_data['Region']
                
                total_routes = len(transportation_df)
                print(f"📊 Total routes to process: {total_routes}")
                
                # Update total routes immediately
                with app.app_context():
                    job = Job.query.filter_by(job_id=job_id).first()
                    if job:
                        job.total_routes = total_routes
                        db.session.commit()
                        print(f"✅ Updated total_routes to {total_routes}")
                    else:
                        print(f"❌ Could not find job {job_id} to update total_routes")
                
                # Small delay to ensure database is updated
                time.sleep(0.5)
                
                # Setup Chrome - NOT headless to handle cookie consent
                chrome_options = Options()
                # chrome_options.add_argument("--headless")  # REMOVED: Allow browser to show for cookie consent
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--window-size=1920,1080")
                chrome_options.add_argument("--disable-blink-features=AutomationControlled")
                chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
                chrome_options.add_experimental_option('useAutomationExtension', False)
                
                driver = webdriver.Chrome(options=chrome_options)
                driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                screenshots_dir = f"screenshots/{job_id}"
                os.makedirs(screenshots_dir, exist_ok=True)
                
                completed = 0
                
                try:
                    for index, row in transportation_df.iterrows():
                        try:
                            # Get coordinates (using correct column names from Excel)
                            lat = row['latitude']
                            lng = row['longitude']
                            site_id = row['ID']
                            warehouse_name = row['warehouse']
                            
                            # Find warehouse coordinates
                            warehouse_row = warehouse_df[warehouse_df['Warehouse'] == warehouse_name]
                            if warehouse_row.empty:
                                continue
                            
                            warehouse_lat = warehouse_row.iloc[0]['latitude']
                            warehouse_lng = warehouse_row.iloc[0]['longitude']
                            
                            # Generate Google Maps URL (latitude,longitude format)
                            url = f"https://www.google.com/maps/dir/{warehouse_lat},{warehouse_lng}/{lat},{lng}"
                            
                            print(f"📍 Processing route {completed + 1}/{total_routes}: {site_id}")
                            
                            # Navigate to page
                            driver.get(url)
                            time.sleep(3)  # Wait for page to load
                            
                            # Handle cookie consent on first page load
                            if completed == 0:
                                handle_cookie_consent(driver)
                                time.sleep(2)
                            
                            # Wait for maps to load
                            time.sleep(5)
                            
                            # Take screenshot
                            screenshot_path = os.path.join(screenshots_dir, f"route_{site_id}.png")
                            driver.save_screenshot(screenshot_path)
                            
                            completed += 1
                            
                            # Update progress more frequently
                            progress = int((completed / total_routes) * 100)
                            try:
                                with app.app_context():
                                    # Refresh job from database
                                    job = Job.query.filter_by(job_id=job_id).first()
                                    if job:
                                        job.progress = progress
                                        job.completed_routes = completed
                                        db.session.commit()
                                        print(f"📊 Progress: {progress}% ({completed}/{total_routes})")
                                    else:
                                        print(f"❌ Could not find job {job_id} for progress update")
                                
                                # Force a small delay to ensure database is updated
                                time.sleep(0.1)
                            except Exception as e:
                                print(f"❌ Error updating progress: {e}")
                            
                        except Exception as e:
                            print(f"❌ Error processing route {index}: {e}")
                            continue
                    
                    # Create ZIP file
                    zip_path = f"screenshots/{job_id}_routes.zip"
                    with zipfile.ZipFile(zip_path, 'w') as zipf:
                        for filename in os.listdir(screenshots_dir):
                            if filename.endswith('.png'):
                                filepath = os.path.join(screenshots_dir, filename)
                                zipf.write(filepath, filename)
                    
                    # Update job status
                    with app.app_context():
                        job = Job.query.filter_by(job_id=job_id).first()
                        if job:
                            job.status = 'completed'
                            job.progress = 100
                            job.completed_at = datetime.utcnow()
                            job.result_file = zip_path
                            db.session.commit()
                            print(f"✅ Job completed: {job_id}")
                        else:
                            print(f"❌ Could not find job {job_id} to mark as completed")
                    
                finally:
                    driver.quit()
                    
            except Exception as e:
                # Update job status on error
                with app.app_context():
                    job = Job.query.filter_by(job_id=job_id).first()
                    if job:
                        job.status = 'failed'
                        job.error_message = str(e)
                        db.session.commit()
                        print(f"❌ Job failed: {job_id} - {e}")
            
            # Mark task as done
            task_queue.task_done()
            
        except Exception as e:
            print(f"Worker error: {e}")
            continue

def start_worker():
    """Start the background worker"""
    global worker_thread, worker_running
    
    if worker_thread is None or not worker_thread.is_alive():
        worker_running = True
        worker_thread = threading.Thread(target=process_screenshots_worker, daemon=True)
        worker_thread.start()
        print("✅ Background worker started")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username or email already exists')
            return render_template('register.html')
        
        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
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
def upload():
    if request.method == 'POST':
        # Ensure database exists
        try:
            db.create_all()
        except Exception as e:
            print(f"Database creation error: {e}")
        
        if 'file' not in request.files:
            flash('No file selected')
            return render_template('upload.html')
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return render_template('upload.html')
        
        if file and file.filename.endswith('.xlsx'):
            filename = secure_filename(file.filename)
            
            # Save file
            upload_dir = 'uploads'
            os.makedirs(upload_dir, exist_ok=True)
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            
            # Create job
            job_id = str(uuid.uuid4())
            job = Job(
                user_id=current_user.id,
                job_id=job_id,
                filename=filename,
                status='pending'
            )
            db.session.add(job)
            db.session.commit()
            
            # Add to processing queue
            task_queue.put((job_id, filepath))
            
            flash('File uploaded successfully! Processing started.')
            return redirect(url_for('dashboard'))
        else:
            flash('Please upload an Excel (.xlsx) file')
    
    return render_template('upload.html')

@app.route('/status/<job_id>')
@login_required
def job_status(job_id):
    job = Job.query.filter_by(job_id=job_id, user_id=current_user.id).first()
    if job:
        return jsonify({
            'status': job.status,
            'progress': job.progress,
            'total_routes': job.total_routes,
            'completed_routes': job.completed_routes,
            'error_message': job.error_message
        })
    return jsonify({'error': 'Job not found'}), 404

@app.route('/download/<int:job_id>')
@login_required
def download(job_id):
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first()
    
    if job and job.result_file and os.path.exists(job.result_file):
        return send_file(job.result_file, as_attachment=True)
    else:
        flash('File not found or job not completed')
        return redirect(url_for('dashboard'))

@app.route('/debug')
@login_required
def debug_info():
    """Debug endpoint to check worker status"""
    return jsonify({
        'worker_running': worker_running,
        'worker_thread_alive': worker_thread.is_alive() if worker_thread else False,
        'queue_size': task_queue.qsize(),
        'worker_thread_id': worker_thread.ident if worker_thread else None,
        'jobs_count': Job.query.count(),
        'pending_jobs': Job.query.filter_by(status='pending').count(),
        'processing_jobs': Job.query.filter_by(status='processing').count(),
        'completed_jobs': Job.query.filter_by(status='completed').count(),
        'failed_jobs': Job.query.filter_by(status='failed').count()
    })

if __name__ == '__main__':
    # Create database tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables created successfully")
    
    # Start background worker
    start_worker()
    
    print("🚀 Starting Route Screenshot Generator (Fixed Version)")
    print("📝 Note: This version handles cookie consent and fixes progress updates")
    print("🌐 Access the application at: http://localhost:5000")
    print("📊 Database: SQLite (routes.db)")
    print("🔑 Test credentials will be created on first registration")
    print()
    print("⚠️ IMPORTANT: Chrome browser will open for cookie consent handling")
    print("   Please accept/reject cookies when prompted for the first route")
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
