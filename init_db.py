#!/usr/bin/env python3
"""
Simple database initialization script
"""

from app import app, db
from models import User, Job

def init_database():
    """Initialize the database with tables"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database initialized successfully!")
        print("📊 Tables created: User, Job")

if __name__ == "__main__":
    init_database()
