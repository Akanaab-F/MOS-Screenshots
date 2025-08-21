import os
import uuid
import zipfile
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import pandas as pd
from celery import Celery
import redis
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-here')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///routes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['SCREENSHOTS_FOLDER'] = 'screenshots'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['SCREENSHOTS_FOLDER'], exist_ok=True)

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Celery configuration
celery = Celery('routes', broker=os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
celery.conf.update(app.config)

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    jobs = db.relationship('Job', backref='user', lazy=True)

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
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
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
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{current_user.id}_{filename}")
            file.save(filepath)
            
            # Create job
            job = Job(
                user_id=current_user.id,
                job_id=str(uuid.uuid4()),
                filename=filename
            )
            db.session.add(job)
            db.session.commit()
            
            # Start background processing
            process_routes.delay(job.job_id, filepath)
            
            flash('File uploaded successfully! Processing started.')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid file type. Please upload an Excel file (.xlsx)')
    
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
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'xlsx', 'xls'}

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
        
    except Exception as e:
        job.status = 'failed'
        job.error_message = str(e)
        db.session.commit()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000) 