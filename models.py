from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User model for authentication"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    files = db.relationship('File', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.email}>'


class File(db.Model):
    """File model for storing file metadata"""
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)  # Size in bytes
    upload_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expiry_time = db.Column(db.DateTime, nullable=False, index=True)
    email_sent = db.Column(db.Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f'<File {self.filename}>'
    
    def is_expired(self):
        """Check if file has expired"""
        return datetime.utcnow() > self.expiry_time
    
    def hours_until_expiry(self):
        """Calculate hours until expiry"""
        delta = self.expiry_time - datetime.utcnow()
        return delta.total_seconds() / 3600

