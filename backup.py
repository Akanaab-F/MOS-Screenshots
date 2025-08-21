#!/usr/bin/env python3
"""
Backup script for Route Screenshot Generator
Handles database and file backups with S3 integration
"""

import os
import sys
import boto3
import subprocess
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/logs/backup.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class BackupManager:
    def __init__(self):
        self.backup_dir = "/app/backups"
        self.s3_bucket = os.getenv('BACKUP_S3_BUCKET')
        self.aws_access_key = os.getenv('AWS_ACCESS_KEY_ID')
        self.aws_secret_key = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.database_url = os.getenv('DATABASE_URL')
        
        # Create backup directory
        os.makedirs(self.backup_dir, exist_ok=True)
        
        # Initialize S3 client if credentials are provided
        if all([self.s3_bucket, self.aws_access_key, self.aws_secret_key]):
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key
            )
        else:
            self.s3_client = None
            logger.warning("S3 credentials not provided, backups will be local only")

    def backup_database(self):
        """Backup the database"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"{self.backup_dir}/database_backup_{timestamp}.sql"
            
            if self.database_url.startswith('postgresql://'):
                # PostgreSQL backup
                self._backup_postgresql(backup_file)
            elif self.database_url.startswith('mysql://'):
                # MySQL backup
                self._backup_mysql(backup_file)
            elif self.database_url.startswith('sqlite:///'):
                # SQLite backup
                self._backup_sqlite(backup_file)
            else:
                logger.error(f"Unsupported database type: {self.database_url}")
                return False
            
            logger.info(f"Database backup completed: {backup_file}")
            
            # Upload to S3 if available
            if self.s3_client:
                self._upload_to_s3(backup_file, f"database/{os.path.basename(backup_file)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            return False

    def _backup_postgresql(self, backup_file):
        """Backup PostgreSQL database"""
        # Extract connection details from DATABASE_URL
        # postgresql://user:pass@host:port/dbname
        url_parts = self.database_url.replace('postgresql://', '').split('@')
        auth = url_parts[0].split(':')
        host_db = url_parts[1].split('/')
        host_port = host_db[0].split(':')
        
        user = auth[0]
        password = auth[1] if len(auth) > 1 else ''
        host = host_port[0]
        port = host_port[1] if len(host_port) > 1 else '5432'
        dbname = host_db[1]
        
        # Set environment variables for pg_dump
        env = os.environ.copy()
        env['PGPASSWORD'] = password
        
        # Run pg_dump
        cmd = [
            'pg_dump',
            '-h', host,
            '-p', port,
            '-U', user,
            '-d', dbname,
            '-f', backup_file,
            '--no-password'
        ]
        
        subprocess.run(cmd, env=env, check=True)

    def _backup_mysql(self, backup_file):
        """Backup MySQL database"""
        # Extract connection details from DATABASE_URL
        # mysql://user:pass@host:port/dbname
        url_parts = self.database_url.replace('mysql://', '').split('@')
        auth = url_parts[0].split(':')
        host_db = url_parts[1].split('/')
        host_port = host_db[0].split(':')
        
        user = auth[0]
        password = auth[1] if len(auth) > 1 else ''
        host = host_port[0]
        port = host_port[1] if len(host_port) > 1 else '3306'
        dbname = host_db[1]
        
        # Run mysqldump
        cmd = [
            'mysqldump',
            '-h', host,
            '-P', port,
            '-u', user,
            f'-p{password}',
            dbname
        ]
        
        with open(backup_file, 'w') as f:
            subprocess.run(cmd, stdout=f, check=True)

    def _backup_sqlite(self, backup_file):
        """Backup SQLite database"""
        # Extract database file path
        db_path = self.database_url.replace('sqlite:///', '')
        if not os.path.isabs(db_path):
            db_path = os.path.join('/app', db_path)
        
        # Copy SQLite database file
        subprocess.run(['cp', db_path, backup_file], check=True)

    def backup_files(self):
        """Backup important files"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = f"{self.backup_dir}/files_backup_{timestamp}.tar.gz"
            
            # Create tar.gz of important directories
            cmd = [
                'tar', '-czf', backup_file,
                '-C', '/app',
                'uploads',
                'screenshots',
                'logs'
            ]
            
            subprocess.run(cmd, check=True)
            logger.info(f"Files backup completed: {backup_file}")
            
            # Upload to S3 if available
            if self.s3_client:
                self._upload_to_s3(backup_file, f"files/{os.path.basename(backup_file)}")
            
            return True
            
        except Exception as e:
            logger.error(f"Files backup failed: {e}")
            return False

    def _upload_to_s3(self, local_file, s3_key):
        """Upload file to S3"""
        try:
            self.s3_client.upload_file(local_file, self.s3_bucket, s3_key)
            logger.info(f"Uploaded {local_file} to S3: {s3_key}")
        except Exception as e:
            logger.error(f"S3 upload failed: {e}")

    def cleanup_old_backups(self, days_to_keep=7):
        """Clean up old backup files"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            
            for filename in os.listdir(self.backup_dir):
                file_path = os.path.join(self.backup_dir, filename)
                file_time = datetime.fromtimestamp(os.path.getctime(file_path))
                
                if file_time < cutoff_date:
                    os.remove(file_path)
                    logger.info(f"Removed old backup: {filename}")
            
            logger.info("Cleanup completed")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

    def run_full_backup(self):
        """Run a complete backup"""
        logger.info("Starting full backup")
        
        success = True
        
        # Backup database
        if not self.backup_database():
            success = False
        
        # Backup files
        if not self.backup_files():
            success = False
        
        # Cleanup old backups
        self.cleanup_old_backups()
        
        if success:
            logger.info("Full backup completed successfully")
        else:
            logger.error("Full backup completed with errors")
        
        return success

def main():
    """Main backup function"""
    backup_manager = BackupManager()
    backup_manager.run_full_backup()

if __name__ == "__main__":
    main()
