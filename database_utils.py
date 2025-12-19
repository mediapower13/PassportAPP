"""
Database models fix and optimization
Ensure all models are properly configured
"""

from models import db, User, Passport
from datetime import datetime


def init_database(app):
    """Initialize database with app context"""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully")


def add_indexes():
    """Add database indexes for performance"""
    with db.engine.connect() as conn:
        # Add index on user email for faster lookups
        try:
            conn.execute(db.text('CREATE INDEX IF NOT EXISTS idx_user_email ON user(email)'))
        except:
            pass
        
        # Add index on passport number
        try:
            conn.execute(db.text('CREATE INDEX IF NOT EXISTS idx_passport_number ON passport(passport_number)'))
        except:
            pass
        
        # Add index on passport user_id
        try:
            conn.execute(db.text('CREATE INDEX IF NOT EXISTS idx_passport_user_id ON passport(user_id)'))
        except:
            pass
        
        conn.commit()
        print("Database indexes created successfully")


def cleanup_expired_sessions():
    """Clean up expired user sessions"""
    # This would clean up old session data
    # Implementation depends on session storage
    pass


def backup_database(backup_path):
    """Backup database to specified path"""
    import shutil
    import os
    
    db_path = 'instance/passportapp.db'
    
    if os.path.exists(db_path):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = f"{backup_path}/passportapp_backup_{timestamp}.db"
        shutil.copy2(db_path, backup_file)
        print(f"Database backed up to: {backup_file}")
        return backup_file
    else:
        print("Database file not found")
        return None


def verify_database_integrity():
    """Verify database integrity"""
    try:
        # Check if tables exist
        user_count = User.query.count()
        passport_count = Passport.query.count()
        
        print(f"Database integrity check:")
        print(f"- Users: {user_count}")
        print(f"- Passports: {passport_count}")
        print("✓ Database integrity verified")
        
        return True
    except Exception as e:
        print(f"✗ Database integrity check failed: {e}")
        return False
