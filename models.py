from flask_login import UserMixin
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    profile_image = db.Column(db.String(255), default='default.jpg')
    bio = db.Column(db.Text, nullable=True)
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(32), nullable=True)
    wallet_address = db.Column(db.String(42), nullable=True, index=True)
    
    # Relationships
    passports = db.relationship('Passport', backref='owner', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        from werkzeug.security import generate_password_hash
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        from werkzeug.security import check_password_hash
        return check_password_hash(self.password, password)


class Passport(db.Model):
    __tablename__ = 'passports'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    # Encrypted passport data
    passport_number = db.Column(db.String(255), nullable=False)  # Encrypted
    full_name = db.Column(db.String(255), nullable=False)  # Encrypted
    nationality = db.Column(db.String(100), nullable=False)
    date_of_birth = db.Column(db.String(255), nullable=True)  # Encrypted
    place_of_birth = db.Column(db.String(255), nullable=True)
    gender = db.Column(db.String(10), nullable=True)
    issue_date = db.Column(db.Date, nullable=True)
    expiry_date = db.Column(db.Date, nullable=False)
    issuing_country = db.Column(db.String(100), nullable=False)
    
    # Encrypted photo data (base64 encoded)
    photo_data = db.Column(db.Text, nullable=True)  # Encrypted
    document_image = db.Column(db.Text, nullable=True)  # Encrypted full document image
    
    # Metadata
    document_type = db.Column(db.String(50), default='passport')  # passport, visa, id_card
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_primary = db.Column(db.Boolean, default=False)
    notes = db.Column(db.Text, nullable=True)
    
    # Reminder settings
    reminder_sent = db.Column(db.Boolean, default=False)
    reminder_days_before = db.Column(db.Integer, default=90)  # Days before expiry to remind
    
    def __repr__(self):
        return f'<Passport {self.passport_number[:4]}****>'
    
    def days_until_expiry(self):
        """Calculate days until passport expires"""
        if self.expiry_date:
            delta = self.expiry_date - datetime.utcnow().date()
            return delta.days
        return None
    
    def is_expired(self):
        """Check if passport is expired"""
        if self.expiry_date:
            return datetime.utcnow().date() > self.expiry_date
        return False
    
    def needs_renewal(self, months=6):
        """Check if passport needs renewal (within X months)"""
        if self.expiry_date:
            days = self.days_until_expiry()
            return days is not None and days < (months * 30)
        return False
