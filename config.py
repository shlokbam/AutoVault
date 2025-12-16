import os
from datetime import timedelta

# Base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Database
DATABASE_PATH = os.path.join(BASE_DIR, 'autovault.db')

# Upload settings
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'zip'}

# Session settings
SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
SESSION_COOKIE_HTTPONLY = True
PERMANENT_SESSION_LIFETIME = timedelta(days=7)

# Email settings (for notifications)
SMTP_SERVER = os.environ.get('SMTP_SERVER') or 'smtp.gmail.com'
SMTP_PORT = int(os.environ.get('SMTP_PORT') or 587)
SMTP_USERNAME = os.environ.get('SMTP_USERNAME') or ''
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD') or ''
EMAIL_FROM = os.environ.get('EMAIL_FROM') or SMTP_USERNAME

# Scheduler settings
NOTIFICATION_HOURS_BEFORE_EXPIRY = 24  # Send email 24 hours before expiry
SCHEDULER_INTERVAL_MINUTES = 60  # Check every hour

