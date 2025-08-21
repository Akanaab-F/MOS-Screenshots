#!/usr/bin/env python3
"""
Database migration script for Route Screenshot Generator
Handles schema changes and data migrations
"""

import os
import sys
from datetime import datetime
from flask_migrate import Migrate, upgrade, downgrade
from app import app, db
from models import User, Job

# Initialize Flask-Migrate
migrate = Migrate(app, db)

def create_migration(message):
    """Create a new migration"""
    try:
        os.system(f'flask db migrate -m "{message}"')
        print(f"Migration created: {message}")
    except Exception as e:
        print(f"Error creating migration: {e}")

def apply_migrations():
    """Apply pending migrations"""
    try:
        upgrade()
        print("Migrations applied successfully")
    except Exception as e:
        print(f"Error applying migrations: {e}")

def rollback_migration():
    """Rollback the last migration"""
    try:
        downgrade()
        print("Migration rolled back successfully")
    except Exception as e:
        print(f"Error rolling back migration: {e}")

def show_migration_history():
    """Show migration history"""
    try:
        os.system('flask db history')
    except Exception as e:
        print(f"Error showing migration history: {e}")

def init_migrations():
    """Initialize migrations for the first time"""
    try:
        os.system('flask db init')
        print("Migrations initialized successfully")
    except Exception as e:
        print(f"Error initializing migrations: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python migrations.py init          # Initialize migrations")
        print("  python migrations.py migrate <msg> # Create migration")
        print("  python migrations.py upgrade       # Apply migrations")
        print("  python migrations.py downgrade     # Rollback migration")
        print("  python migrations.py history       # Show history")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "init":
        init_migrations()
    elif command == "migrate":
        if len(sys.argv) < 3:
            print("Please provide a migration message")
            sys.exit(1)
        create_migration(sys.argv[2])
    elif command == "upgrade":
        apply_migrations()
    elif command == "downgrade":
        rollback_migration()
    elif command == "history":
        show_migration_history()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
