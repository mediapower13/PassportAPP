"""
Backup and recovery utilities for PassportApp
Automated backup system for database and critical files
"""

import os
import shutil
import json
from datetime import datetime, timedelta
import tarfile
import gzip


class BackupManager:
    """Manage backups for database and files"""
    
    def __init__(self, backup_dir='backups'):
        self.backup_dir = backup_dir
        self.ensure_backup_dir()
    
    def ensure_backup_dir(self):
        """Ensure backup directory exists"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
        
        # Create subdirectories
        for subdir in ['database', 'files', 'full', 'contracts']:
            path = os.path.join(self.backup_dir, subdir)
            if not os.path.exists(path):
                os.makedirs(path)
    
    def backup_database(self, db_path='instance/passportapp.db'):
        """Backup database file"""
        if not os.path.exists(db_path):
            return False, 'Database file not found'
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        backup_name = f'database_backup_{timestamp}.db'
        backup_path = os.path.join(self.backup_dir, 'database', backup_name)
        
        try:
            shutil.copy2(db_path, backup_path)
            
            # Compress backup
            with open(backup_path, 'rb') as f_in:
                with gzip.open(f'{backup_path}.gz', 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove uncompressed backup
            os.remove(backup_path)
            
            backup_info = {
                'type': 'database',
                'timestamp': timestamp,
                'file': f'{backup_name}.gz',
                'size': os.path.getsize(f'{backup_path}.gz'),
                'original_path': db_path
            }
            
            self.save_backup_metadata(backup_info)
            
            return True, f'{backup_name}.gz'
        
        except Exception as e:
            return False, f'Backup failed: {str(e)}'
    
    def backup_uploads(self, uploads_dir='uploads'):
        """Backup uploaded files"""
        if not os.path.exists(uploads_dir):
            return False, 'Uploads directory not found'
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        backup_name = f'uploads_backup_{timestamp}.tar.gz'
        backup_path = os.path.join(self.backup_dir, 'files', backup_name)
        
        try:
            with tarfile.open(backup_path, 'w:gz') as tar:
                tar.add(uploads_dir, arcname=os.path.basename(uploads_dir))
            
            backup_info = {
                'type': 'uploads',
                'timestamp': timestamp,
                'file': backup_name,
                'size': os.path.getsize(backup_path),
                'original_path': uploads_dir
            }
            
            self.save_backup_metadata(backup_info)
            
            return True, backup_name
        
        except Exception as e:
            return False, f'Backup failed: {str(e)}'
    
    def backup_contracts(self, contracts_dir='contracts'):
        """Backup smart contract files"""
        if not os.path.exists(contracts_dir):
            return False, 'Contracts directory not found'
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        backup_name = f'contracts_backup_{timestamp}.tar.gz'
        backup_path = os.path.join(self.backup_dir, 'contracts', backup_name)
        
        try:
            with tarfile.open(backup_path, 'w:gz') as tar:
                tar.add(contracts_dir, arcname=os.path.basename(contracts_dir))
            
            backup_info = {
                'type': 'contracts',
                'timestamp': timestamp,
                'file': backup_name,
                'size': os.path.getsize(backup_path),
                'original_path': contracts_dir
            }
            
            self.save_backup_metadata(backup_info)
            
            return True, backup_name
        
        except Exception as e:
            return False, f'Backup failed: {str(e)}'
    
    def backup_full_system(self):
        """Create full system backup"""
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        backup_name = f'full_backup_{timestamp}.tar.gz'
        backup_path = os.path.join(self.backup_dir, 'full', backup_name)
        
        try:
            with tarfile.open(backup_path, 'w:gz') as tar:
                # Backup database
                if os.path.exists('instance'):
                    tar.add('instance', arcname='instance')
                
                # Backup uploads
                if os.path.exists('uploads'):
                    tar.add('uploads', arcname='uploads')
                
                # Backup contracts
                if os.path.exists('contracts'):
                    tar.add('contracts', arcname='contracts')
                
                # Backup config files
                config_files = ['.env', 'config.py', 'hardhat.config.js']
                for config_file in config_files:
                    if os.path.exists(config_file):
                        tar.add(config_file)
            
            backup_info = {
                'type': 'full',
                'timestamp': timestamp,
                'file': backup_name,
                'size': os.path.getsize(backup_path),
                'components': ['database', 'uploads', 'contracts', 'config']
            }
            
            self.save_backup_metadata(backup_info)
            
            return True, backup_name
        
        except Exception as e:
            return False, f'Full backup failed: {str(e)}'
    
    def restore_database(self, backup_file):
        """Restore database from backup"""
        backup_path = os.path.join(self.backup_dir, 'database', backup_file)
        
        if not os.path.exists(backup_path):
            return False, 'Backup file not found'
        
        try:
            # Extract compressed backup
            temp_path = backup_path.replace('.gz', '')
            
            with gzip.open(backup_path, 'rb') as f_in:
                with open(temp_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Restore database
            db_path = 'instance/passportapp.db'
            
            # Backup current database before restore
            if os.path.exists(db_path):
                current_backup = f'{db_path}.pre_restore_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}'
                shutil.copy2(db_path, current_backup)
            
            shutil.copy2(temp_path, db_path)
            
            # Remove temp file
            os.remove(temp_path)
            
            return True, 'Database restored successfully'
        
        except Exception as e:
            return False, f'Restore failed: {str(e)}'
    
    def list_backups(self, backup_type=None):
        """List available backups"""
        backups = []
        metadata_file = os.path.join(self.backup_dir, 'backup_metadata.json')
        
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                all_backups = json.load(f)
                
                if backup_type:
                    backups = [b for b in all_backups if b.get('type') == backup_type]
                else:
                    backups = all_backups
        
        return sorted(backups, key=lambda x: x['timestamp'], reverse=True)
    
    def cleanup_old_backups(self, days=30):
        """Remove backups older than specified days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        cutoff_str = cutoff_date.strftime('%Y%m%d')
        
        removed_count = 0
        
        for backup_type in ['database', 'files', 'full', 'contracts']:
            backup_dir = os.path.join(self.backup_dir, backup_type)
            
            if os.path.exists(backup_dir):
                for filename in os.listdir(backup_dir):
                    filepath = os.path.join(backup_dir, filename)
                    
                    # Extract timestamp from filename
                    try:
                        timestamp_part = filename.split('_')[2].split('.')[0]
                        if timestamp_part < cutoff_str:
                            os.remove(filepath)
                            removed_count += 1
                    except:
                        continue
        
        return removed_count
    
    def save_backup_metadata(self, backup_info):
        """Save backup metadata"""
        metadata_file = os.path.join(self.backup_dir, 'backup_metadata.json')
        
        metadata = []
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
        
        metadata.append(backup_info)
        
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    def get_backup_stats(self):
        """Get backup statistics"""
        stats = {
            'total_backups': 0,
            'total_size': 0,
            'by_type': {},
            'oldest': None,
            'newest': None
        }
        
        backups = self.list_backups()
        
        if backups:
            stats['total_backups'] = len(backups)
            stats['total_size'] = sum(b.get('size', 0) for b in backups)
            stats['oldest'] = backups[-1]['timestamp']
            stats['newest'] = backups[0]['timestamp']
            
            for backup in backups:
                backup_type = backup.get('type', 'unknown')
                if backup_type not in stats['by_type']:
                    stats['by_type'][backup_type] = {'count': 0, 'size': 0}
                
                stats['by_type'][backup_type]['count'] += 1
                stats['by_type'][backup_type]['size'] += backup.get('size', 0)
        
        return stats


# Global backup manager instance
backup_manager = BackupManager()


def create_automated_backup():
    """Create automated backup of all components"""
    results = {
        'timestamp': datetime.utcnow().isoformat(),
        'backups': []
    }
    
    # Backup database
    success, message = backup_manager.backup_database()
    results['backups'].append({
        'type': 'database',
        'success': success,
        'message': message
    })
    
    # Backup uploads
    success, message = backup_manager.backup_uploads()
    results['backups'].append({
        'type': 'uploads',
        'success': success,
        'message': message
    })
    
    # Backup contracts
    success, message = backup_manager.backup_contracts()
    results['backups'].append({
        'type': 'contracts',
        'success': success,
        'message': message
    })
    
    return results


def schedule_backup_cleanup(days=30):
    """Schedule cleanup of old backups"""
    removed = backup_manager.cleanup_old_backups(days)
    return f'Removed {removed} old backups'
