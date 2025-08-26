#!/usr/bin/env python3
"""
Heroku Deployment Configuration for Route Screenshot Generator
"""

import os
import subprocess
import sys

def create_heroku_files():
    """Create Heroku deployment files"""
    
    # Create Procfile
    with open('Procfile', 'w') as f:
        f.write('web: gunicorn app_with_redis_alt:app\n')
    
    # Create runtime.txt
    with open('runtime.txt', 'w') as f:
        f.write('python-3.11.7\n')
    
    # Create requirements.txt (if not exists)
    if not os.path.exists('requirements.txt'):
        requirements = [
            'Flask==2.3.3',
            'Flask-Login==0.6.3',
            'Flask-SQLAlchemy==3.0.5',
            'Flask-WTF==1.1.1',
            'Werkzeug==2.3.7',
            'pandas==2.1.1',
            'selenium==4.15.2',
            'openpyxl==3.1.2',
            'gunicorn==21.2.0',
            'psycopg2-binary==2.9.7',  # For PostgreSQL
            'redis==5.0.1',
            'celery==5.3.4'
        ]
        
        with open('requirements.txt', 'w') as f:
            f.write('\n'.join(requirements))
    
    # Create app.json for Heroku
    app_json = {
        "name": "Route Screenshot Generator",
        "description": "Automated Google Maps route screenshot generator",
        "repository": "https://github.com/Akanaab-F/MOS-Screenshots.git",
        "logo": "",
        "keywords": ["python", "flask", "selenium", "maps", "screenshots"],
        "env": {
            "SECRET_KEY": {
                "description": "Flask secret key",
                "generator": "secret"
            },
            "DATABASE_URL": {
                "description": "PostgreSQL database URL",
                "value": "postgresql://localhost/route_screenshots"
            },
            "REDIS_URL": {
                "description": "Redis URL for Celery",
                "value": "redis://localhost:6379/0"
            }
        },
        "addons": [
            "heroku-postgresql:mini",
            "heroku-redis:mini"
        ],
        "buildpacks": [
            {
                "url": "heroku/python"
            },
            {
                "url": "heroku/google-chrome"
            }
        ]
    }
    
    import json
    with open('app.json', 'w') as f:
        json.dump(app_json, f, indent=2)
    
    print("✅ Heroku deployment files created!")

def deploy_to_heroku():
    """Deploy to Heroku"""
    print("🚀 Deploying to Heroku...")
    
    # Check if Heroku CLI is installed
    try:
        subprocess.run(['heroku', '--version'], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Heroku CLI not found. Please install it first:")
        print("   https://devcenter.heroku.com/articles/heroku-cli")
        return
    
    # Create Heroku app
    app_name = input("Enter Heroku app name (or press Enter for auto-generated): ").strip()
    
    if app_name:
        subprocess.run(['heroku', 'create', app_name])
    else:
        subprocess.run(['heroku', 'create'])
    
    # Add PostgreSQL and Redis
    subprocess.run(['heroku', 'addons:create', 'heroku-postgresql:mini'])
    subprocess.run(['heroku', 'addons:create', 'heroku-redis:mini'])
    
    # Deploy
    subprocess.run(['git', 'add', '.'])
    subprocess.run(['git', 'commit', '-m', 'Deploy to Heroku'])
    subprocess.run(['git', 'push', 'heroku', 'main'])
    
    # Open the app
    subprocess.run(['heroku', 'open'])
    
    print("✅ Deployment complete!")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == 'deploy':
        deploy_to_heroku()
    else:
        create_heroku_files()
        print("\n📋 To deploy to Heroku:")
        print("   1. Install Heroku CLI")
        print("   2. Run: python deploy_heroku.py deploy")
        print("   3. Follow the prompts")
