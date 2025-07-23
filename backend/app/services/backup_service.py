"""
Automated Backup Service for MEDHASAKTHI
Implements database backups, file backups, and backup encryption
"""

import os
import gzip
import shutil
import subprocess
import logging
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path
import boto3
from cryptography.fernet import Fernet
import schedule
import time

from app.core.config import settings
from app.core.database import get_db
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)

class BackupService:
    """Comprehensive backup service with encryption and cloud storage"""
    
    def __init__(self):
        self.backup_dir = Path(getattr(settings, 'BACKUP_DIR', '/app/backups'))
        self.backup_dir.mkdir(exist_ok=True)
        
        # Encryption setup
        self.encryption_key = getattr(settings, 'BACKUP_ENCRYPTION_KEY', Fernet.generate_key())
        self.cipher = Fernet(self.encryption_key)
        
        # Backup retention settings
        self.daily_retention = 7  # Keep 7 daily backups
        self.weekly_retention = 4  # Keep 4 weekly backups
        self.monthly_retention = 12  # Keep 12 monthly backups
        
        # Cloud storage settings
        self.use_cloud_storage = getattr(settings, 'USE_CLOUD_BACKUP', False)
        self.s3_bucket = getattr(settings, 'BACKUP_S3_BUCKET', None)
        
        # Email notifications
        self.email_service = EmailService()
        self.notify_on_failure = True
        self.notify_on_success = False  # Only for critical backups
        
        # Initialize cloud storage if configured
        if self.use_cloud_storage and self.s3_bucket:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=getattr(settings, 'AWS_ACCESS_KEY_ID', None),
                aws_secret_access_key=getattr(settings, 'AWS_SECRET_ACCESS_KEY', None),
                region_name=getattr(settings, 'AWS_REGION', 'us-east-1')
            )
    
    async def create_database_backup(self) -> Dict:
        """Create encrypted database backup"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"medhasakthi_db_{timestamp}.sql"
            backup_path = self.backup_dir / backup_filename
            
            # Create PostgreSQL dump
            db_url = settings.DATABASE_URL
            if db_url.startswith('postgresql://'):
                # Extract connection details
                import urllib.parse as urlparse
                parsed = urlparse.urlparse(db_url)
                
                env = os.environ.copy()
                env['PGPASSWORD'] = parsed.password
                
                cmd = [
                    'pg_dump',
                    '-h', parsed.hostname,
                    '-p', str(parsed.port or 5432),
                    '-U', parsed.username,
                    '-d', parsed.path[1:],  # Remove leading slash
                    '--no-password',
                    '--verbose',
                    '--clean',
                    '--if-exists',
                    '--create'
                ]
                
                # Execute backup
                with open(backup_path, 'w') as f:
                    result = subprocess.run(
                        cmd,
                        stdout=f,
                        stderr=subprocess.PIPE,
                        env=env,
                        text=True
                    )
                
                if result.returncode != 0:
                    raise Exception(f"pg_dump failed: {result.stderr}")
                
                # Encrypt backup
                encrypted_path = await self._encrypt_file(backup_path)
                
                # Compress encrypted backup
                compressed_path = await self._compress_file(encrypted_path)
                
                # Upload to cloud if configured
                cloud_url = None
                if self.use_cloud_storage:
                    cloud_url = await self._upload_to_cloud(compressed_path)
                
                # Clean up unencrypted file
                backup_path.unlink()
                encrypted_path.unlink()
                
                backup_info = {
                    'type': 'database',
                    'filename': compressed_path.name,
                    'path': str(compressed_path),
                    'size': compressed_path.stat().st_size,
                    'timestamp': timestamp,
                    'encrypted': True,
                    'compressed': True,
                    'cloud_url': cloud_url,
                    'status': 'success'
                }
                
                logger.info(f"Database backup created successfully: {compressed_path.name}")
                return backup_info
                
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            if self.notify_on_failure:
                await self._send_backup_notification('database', False, str(e))
            
            return {
                'type': 'database',
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S')
            }
    
    async def create_files_backup(self) -> Dict:
        """Create backup of uploaded files and logs"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"medhasakthi_files_{timestamp}.tar.gz"
            backup_path = self.backup_dir / backup_filename
            
            # Directories to backup
            backup_dirs = [
                '/app/uploads',
                '/app/logs',
                '/app/static',
                '/app/certificates'
            ]
            
            # Create tar archive
            import tarfile
            with tarfile.open(backup_path, 'w:gz') as tar:
                for dir_path in backup_dirs:
                    if os.path.exists(dir_path):
                        tar.add(dir_path, arcname=os.path.basename(dir_path))
            
            # Encrypt backup
            encrypted_path = await self._encrypt_file(backup_path)
            
            # Upload to cloud if configured
            cloud_url = None
            if self.use_cloud_storage:
                cloud_url = await self._upload_to_cloud(encrypted_path)
            
            # Clean up unencrypted file
            backup_path.unlink()
            
            backup_info = {
                'type': 'files',
                'filename': encrypted_path.name,
                'path': str(encrypted_path),
                'size': encrypted_path.stat().st_size,
                'timestamp': timestamp,
                'encrypted': True,
                'cloud_url': cloud_url,
                'status': 'success'
            }
            
            logger.info(f"Files backup created successfully: {encrypted_path.name}")
            return backup_info
            
        except Exception as e:
            logger.error(f"Files backup failed: {e}")
            if self.notify_on_failure:
                await self._send_backup_notification('files', False, str(e))
            
            return {
                'type': 'files',
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S')
            }
    
    async def create_full_backup(self) -> Dict:
        """Create complete system backup"""
        try:
            logger.info("Starting full system backup...")
            
            # Create database backup
            db_backup = await self.create_database_backup()
            
            # Create files backup
            files_backup = await self.create_files_backup()
            
            # Create configuration backup
            config_backup = await self._backup_configuration()
            
            full_backup_info = {
                'type': 'full',
                'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),
                'components': {
                    'database': db_backup,
                    'files': files_backup,
                    'configuration': config_backup
                },
                'status': 'success' if all(
                    backup.get('status') == 'success' 
                    for backup in [db_backup, files_backup, config_backup]
                ) else 'partial'
            }
            
            # Send success notification for full backups
            if self.notify_on_success:
                await self._send_backup_notification('full', True)
            
            logger.info("Full system backup completed")
            return full_backup_info
            
        except Exception as e:
            logger.error(f"Full backup failed: {e}")
            if self.notify_on_failure:
                await self._send_backup_notification('full', False, str(e))
            
            return {
                'type': 'full',
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S')
            }
    
    async def restore_database_backup(self, backup_path: str) -> bool:
        """Restore database from backup"""
        try:
            # Decrypt backup
            decrypted_path = await self._decrypt_file(backup_path)
            
            # Decompress if needed
            if backup_path.endswith('.gz'):
                decompressed_path = await self._decompress_file(decrypted_path)
                decrypted_path.unlink()
                decrypted_path = decompressed_path
            
            # Restore database
            db_url = settings.DATABASE_URL
            if db_url.startswith('postgresql://'):
                import urllib.parse as urlparse
                parsed = urlparse.urlparse(db_url)
                
                env = os.environ.copy()
                env['PGPASSWORD'] = parsed.password
                
                cmd = [
                    'psql',
                    '-h', parsed.hostname,
                    '-p', str(parsed.port or 5432),
                    '-U', parsed.username,
                    '-d', parsed.path[1:],
                    '-f', str(decrypted_path)
                ]
                
                result = subprocess.run(
                    cmd,
                    stderr=subprocess.PIPE,
                    env=env,
                    text=True
                )
                
                if result.returncode != 0:
                    raise Exception(f"Database restore failed: {result.stderr}")
                
                # Clean up decrypted file
                decrypted_path.unlink()
                
                logger.info("Database restored successfully")
                return True
                
        except Exception as e:
            logger.error(f"Database restore failed: {e}")
            return False
    
    async def cleanup_old_backups(self):
        """Clean up old backups based on retention policy"""
        try:
            now = datetime.now()
            
            for backup_file in self.backup_dir.glob('*.gz.enc'):
                file_date = datetime.fromtimestamp(backup_file.stat().st_mtime)
                age_days = (now - file_date).days
                
                should_delete = False
                
                # Daily backups - keep for 7 days
                if age_days > self.daily_retention:
                    # Weekly backups - keep for 4 weeks
                    if file_date.weekday() == 0 and age_days > (self.weekly_retention * 7):
                        # Monthly backups - keep for 12 months
                        if file_date.day == 1 and age_days > (self.monthly_retention * 30):
                            should_delete = True
                        elif file_date.day != 1:
                            should_delete = True
                    elif file_date.weekday() != 0:
                        should_delete = True
                
                if should_delete:
                    backup_file.unlink()
                    logger.info(f"Deleted old backup: {backup_file.name}")
                    
        except Exception as e:
            logger.error(f"Backup cleanup failed: {e}")
    
    # Private helper methods
    
    async def _encrypt_file(self, file_path: Path) -> Path:
        """Encrypt file using Fernet encryption"""
        encrypted_path = file_path.with_suffix(file_path.suffix + '.enc')
        
        with open(file_path, 'rb') as f:
            data = f.read()
        
        encrypted_data = self.cipher.encrypt(data)
        
        with open(encrypted_path, 'wb') as f:
            f.write(encrypted_data)
        
        return encrypted_path
    
    async def _decrypt_file(self, file_path: str) -> Path:
        """Decrypt file using Fernet encryption"""
        file_path = Path(file_path)
        decrypted_path = file_path.with_suffix('')
        
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()
        
        decrypted_data = self.cipher.decrypt(encrypted_data)
        
        with open(decrypted_path, 'wb') as f:
            f.write(decrypted_data)
        
        return decrypted_path
    
    async def _compress_file(self, file_path: Path) -> Path:
        """Compress file using gzip"""
        compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
        
        with open(file_path, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        return compressed_path
    
    async def _decompress_file(self, file_path: Path) -> Path:
        """Decompress gzip file"""
        decompressed_path = file_path.with_suffix('')
        
        with gzip.open(file_path, 'rb') as f_in:
            with open(decompressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        return decompressed_path
    
    async def _upload_to_cloud(self, file_path: Path) -> Optional[str]:
        """Upload backup to cloud storage"""
        if not self.use_cloud_storage or not self.s3_bucket:
            return None
        
        try:
            key = f"backups/{file_path.name}"
            self.s3_client.upload_file(str(file_path), self.s3_bucket, key)
            
            url = f"s3://{self.s3_bucket}/{key}"
            logger.info(f"Backup uploaded to cloud: {url}")
            return url
            
        except Exception as e:
            logger.error(f"Cloud upload failed: {e}")
            return None
    
    async def _backup_configuration(self) -> Dict:
        """Backup system configuration"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            config_filename = f"medhasakthi_config_{timestamp}.tar.gz"
            config_path = self.backup_dir / config_filename
            
            # Configuration files to backup
            config_files = [
                'docker-compose.yml',
                'nginx.conf',
                '.env.example',
                'requirements.txt',
                'package.json'
            ]
            
            import tarfile
            with tarfile.open(config_path, 'w:gz') as tar:
                for config_file in config_files:
                    if os.path.exists(config_file):
                        tar.add(config_file)
            
            # Encrypt configuration backup
            encrypted_path = await self._encrypt_file(config_path)
            config_path.unlink()
            
            return {
                'type': 'configuration',
                'filename': encrypted_path.name,
                'path': str(encrypted_path),
                'size': encrypted_path.stat().st_size,
                'timestamp': timestamp,
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Configuration backup failed: {e}")
            return {
                'type': 'configuration',
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S')
            }
    
    async def _send_backup_notification(self, backup_type: str, success: bool, error: str = None):
        """Send backup notification email"""
        try:
            admin_email = getattr(settings, 'ADMIN_EMAIL', None)
            if not admin_email:
                return
            
            subject = f"MEDHASAKTHI Backup {'Success' if success else 'Failed'}: {backup_type}"
            
            if success:
                message = f"Backup of type '{backup_type}' completed successfully at {datetime.now()}"
            else:
                message = f"Backup of type '{backup_type}' failed at {datetime.now()}\nError: {error}"
            
            await self.email_service.send_admin_notification(admin_email, subject, message)
            
        except Exception as e:
            logger.error(f"Failed to send backup notification: {e}")

# Global backup service instance
backup_service = BackupService()

# Backup scheduler
def schedule_backups():
    """Schedule automated backups"""
    # Daily database backup at 2 AM
    schedule.every().day.at("02:00").do(
        lambda: asyncio.create_task(backup_service.create_database_backup())
    )
    
    # Weekly full backup on Sunday at 3 AM
    schedule.every().sunday.at("03:00").do(
        lambda: asyncio.create_task(backup_service.create_full_backup())
    )
    
    # Daily cleanup at 4 AM
    schedule.every().day.at("04:00").do(
        lambda: asyncio.create_task(backup_service.cleanup_old_backups())
    )
