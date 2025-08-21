#!/usr/bin/env python3
"""
Cleanup script for the Route Screenshot Generator
Removes old screenshot files and temporary data
"""

import os
import shutil
from datetime import datetime, timedelta
from models import db, Job
from app import app

def cleanup_old_files(days_old=7):
    """Remove screenshot files older than specified days"""
    cutoff_date = datetime.utcnow() - timedelta(days=days_old)
    
    with app.app_context():
        # Get old completed jobs
        old_jobs = Job.query.filter(
            Job.status.in_(['completed', 'failed']),
            Job.created_at < cutoff_date
        ).all()
        
        cleaned_count = 0
        for job in old_jobs:
            # Remove screenshot directory
            job_screenshots_dir = f"screenshots/{job.job_id}"
            if os.path.exists(job_screenshots_dir):
                try:
                    shutil.rmtree(job_screenshots_dir)
                    cleaned_count += 1
                    print(f"Removed screenshots for job {job.job_id}")
                except Exception as e:
                    print(f"Error removing screenshots for job {job.job_id}: {e}")
            
            # Remove result file
            if job.result_file and os.path.exists(job.result_file):
                try:
                    os.remove(job.result_file)
                    print(f"Removed result file for job {job.job_id}")
                except Exception as e:
                    print(f"Error removing result file for job {job.job_id}: {e}")
        
        print(f"Cleaned up {cleaned_count} old job directories")

def cleanup_empty_directories():
    """Remove empty screenshot directories"""
    screenshots_dir = "screenshots"
    if not os.path.exists(screenshots_dir):
        return
    
    cleaned_count = 0
    for root, dirs, files in os.walk(screenshots_dir, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                if not os.listdir(dir_path):  # Directory is empty
                    os.rmdir(dir_path)
                    cleaned_count += 1
                    print(f"Removed empty directory: {dir_path}")
            except Exception as e:
                print(f"Error removing directory {dir_path}: {e}")
    
    print(f"Cleaned up {cleaned_count} empty directories")

def cleanup_orphaned_files():
    """Remove screenshot files that don't correspond to any job"""
    screenshots_dir = "screenshots"
    if not os.path.exists(screenshots_dir):
        return
    
    with app.app_context():
        # Get all job IDs from database
        job_ids = {job.job_id for job in Job.query.all()}
        
        cleaned_count = 0
        for item in os.listdir(screenshots_dir):
            item_path = os.path.join(screenshots_dir, item)
            
            # Check if it's a directory and doesn't correspond to a job
            if os.path.isdir(item_path) and item not in job_ids:
                try:
                    shutil.rmtree(item_path)
                    cleaned_count += 1
                    print(f"Removed orphaned directory: {item_path}")
                except Exception as e:
                    print(f"Error removing orphaned directory {item_path}: {e}")
        
        print(f"Cleaned up {cleaned_count} orphaned directories")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Cleanup old files from Route Screenshot Generator")
    parser.add_argument("--days", type=int, default=7, help="Remove files older than N days (default: 7)")
    parser.add_argument("--empty-dirs", action="store_true", help="Remove empty directories")
    parser.add_argument("--orphaned", action="store_true", help="Remove orphaned files")
    parser.add_argument("--all", action="store_true", help="Run all cleanup operations")
    
    args = parser.parse_args()
    
    if args.all or not any([args.empty_dirs, args.orphaned]):
        print("Cleaning up old files...")
        cleanup_old_files(args.days)
    
    if args.all or args.empty_dirs:
        print("Cleaning up empty directories...")
        cleanup_empty_directories()
    
    if args.all or args.orphaned:
        print("Cleaning up orphaned files...")
        cleanup_orphaned_files()
    
    print("Cleanup completed!")
