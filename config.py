import os
from datetime import timedelta

# Base directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Database Configuration
DATABASE_URL = os.environ.get('DATABASE_URL') or ''

# RDS Configuration (if using RDS)
RDS_HOST = os.environ.get('RDS_HOST') or ''
RDS_PORT = os.environ.get('RDS_PORT') or '5432'
RDS_DB_NAME = os.environ.get('RDS_DB_NAME') or ''
RDS_USERNAME = os.environ.get('RDS_USERNAME') or ''
RDS_PASSWORD = os.environ.get('RDS_PASSWORD') or ''

# Use RDS if DATABASE_URL is provided or RDS credentials are set
USE_RDS = os.environ.get('USE_RDS', 'true').lower() == 'true'  # Set to True to use RDS

# SQLite Configuration (fallback)
DATABASE_PATH = os.path.join(BASE_DIR, '')

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

# Lambda Scheduler (Cloud automation)
USE_LAMBDA_SCHEDULER = os.environ.get('USE_LAMBDA_SCHEDULER', 'false').lower() == 'true'  # Use Lambda instead of local scheduler

# AWS S3 Settings
USE_S3 = os.environ.get('USE_S3', 'true').lower() == 'true'  # Enable S3 by default
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID') or ''
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY') or ''
AWS_REGION = os.environ.get('AWS_REGION') or ''
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME') or ''
S3_BUCKET_PREFIX = os.environ.get('S3_BUCKET_PREFIX') or ''  # Folder prefix in bucket
