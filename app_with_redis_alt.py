#!/usr/bin/env python3
"""
Route Screenshot Generator with Python-based Redis Alternative
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
import json

# Create Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-super-secret-key-change-this-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///routes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Simple task queue (Redis alternative)
task_queue = queue.Queue()
worker_thread = None
worker_running = False

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def is_authenticated(self):
        return True
    
    def is_active(self):
        return True
    
    def is_anonymous(self):
        return False
    
    def get_id(self):
        return str(self.id)

# Job model
class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    job_id = db.Column(db.String(36), unique=True, nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(20), default='pending')
    progress = db.Column(db.Integer, default=0)
    total_routes = db.Column(db.Integer, default=0)
    completed_routes = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    result_file = db.Column(db.String(255))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def process_screenshots_worker():
    """Background worker for processing screenshots"""
    global worker_running
    
    while worker_running:
        try:
            # Get task from queue (non-blocking)
            try:
                task = task_queue.get_nowait()
            except queue.Empty:
                time.sleep(1)
                continue
            
            job_id, filepath = task
            
            try:
                # Update job status
                with app.app_context():
                    job = Job.query.filter_by(job_id=job_id).first()
                    if not job:
                        continue
                    
                    job.status = 'processing'
                    job.progress = 0
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
                
                # Update total routes
                with app.app_context():
                    job.total_routes = total_routes
                    db.session.commit()
                
                # Setup Chrome
                chrome_options = Options()
                chrome_options.add_argument("--headless")
                chrome_options.add_argument("--no-sandbox")
                chrome_options.add_argument("--disable-dev-shm-usage")
                chrome_options.add_argument("--window-size=1920,1080")
                
                driver = webdriver.Chrome(options=chrome_options)
                screenshots_dir = f"screenshots/{job_id}"
                os.makedirs(screenshots_dir, exist_ok=True)
                
                completed = 0
                
                try:
                    for index, row in transportation_df.iterrows():
                        try:
                            # Get coordinates
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
                            
                            # Generate Google Maps URL
                            url = f"https://www.google.com/maps/dir/{warehouse_lat},{warehouse_lng}/{lat},{lng}"
                            
                            # Navigate and take screenshot
                            driver.get(url)
                            time.sleep(3)  # Wait for page to load
                            
                            # Take screenshot
                            screenshot_path = os.path.join(screenshots_dir, f"route_{site_id}.png")
                            driver.save_screenshot(screenshot_path)
                            
                            completed += 1
                            
                            # Update progress
                            progress = int((completed / total_routes) * 100)
                            with app.app_context():
                                job.progress = progress
                                job.completed_routes = completed
                                db.session.commit()
                            
                        except Exception as e:
                            print(f"Error processing route {index}: {e}")
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
                        job.status = 'completed'
                        job.progress = 100
                        job.completed_at = datetime.utcnow()
                        job.result_file = zip_path
                        db.session.commit()
                    
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
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)
            
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)
            
            # Create job record
            job_id = str(uuid.uuid4())
            new_job = Job(
                user_id=current_user.id, 
                job_id=job_id,
                filename=filename, 
                status='pending'
            )
            db.session.add(new_job)
            db.session.commit()
            
            # Add task to queue
            task_queue.put((job_id, filepath))
            
            flash('File uploaded successfully! Processing will start soon.')
            return redirect(url_for('dashboard'))
        else:
            flash('Please upload an Excel (.xlsx) file')
    
    return render_template('upload.html')

@app.route('/status/<int:job_id>')
@login_required
def status(job_id):
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first()
    
    if job:
        return jsonify({
            'status': job.status, 
            'progress': job.progress or 0,
            'total_routes': job.total_routes,
            'completed_routes': job.completed_routes,
            'error_message': job.error_message
        })
    else:
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

if __name__ == '__main__':
    print("🚀 Starting Route Screenshot Generator (Alternative Version)")
    print("📝 Note: This version uses Python threading instead of Redis/Celery")
    print("🌐 Access the application at: http://localhost:5000")
    print("📊 Database: SQLite (routes.db)")
    print("🔑 Test credentials will be created on first registration")
    print()
    
    # Create tables if they don't exist
    with app.app_context():
        db.create_all()
        print("✅ Database tables created/verified")
    
    # Start background worker
    start_worker()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
