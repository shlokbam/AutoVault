from flask import Flask, redirect, url_for
from flask_login import LoginManager
from models import db, User
from config import (
    DATABASE_PATH, SECRET_KEY, UPLOAD_FOLDER,
    USE_RDS, DATABASE_URL, RDS_HOST, RDS_PORT,
    RDS_DB_NAME, RDS_USERNAME, RDS_PASSWORD,
    USE_LAMBDA_SCHEDULER
)
from auth import auth_bp
from files import files_bp
from scheduler import start_scheduler, stop_scheduler
import os
import atexit
from urllib.parse import quote_plus

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY

# Configure database connection
if USE_RDS and DATABASE_URL:
    # Use provided DATABASE_URL (e.g., from Heroku, AWS RDS Proxy, etc.)
    app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
    print("[Database] Using RDS via DATABASE_URL")
elif USE_RDS and RDS_HOST and RDS_USERNAME and RDS_PASSWORD:
    # Build connection string from individual components
    # URL encode password to handle special characters
    encoded_password = quote_plus(RDS_PASSWORD)
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'postgresql://{RDS_USERNAME}:{encoded_password}@'
        f'{RDS_HOST}:{RDS_PORT}/{RDS_DB_NAME}'
    )
    print(f"[Database] Using RDS: {RDS_HOST}:{RDS_PORT}/{RDS_DB_NAME}")
else:
    # Fallback to SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
    print(f"[Database] Using SQLite: {DATABASE_PATH}")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,  # Verify connections before using
    'pool_recycle': 300,    # Recycle connections after 5 minutes
}

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(files_bp)


@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return User.query.get(int(user_id))


@app.route('/')
def index():
    """Redirect to dashboard or login"""
    return redirect(url_for('files.dashboard'))


def init_db():
    """Initialize database and create tables"""
    with app.app_context():
        # Create uploads directory (for local fallback)
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        try:
            # Create database tables
            db.create_all()
            db_type = "RDS (PostgreSQL)" if USE_RDS else "SQLite"
            print(f"[App] Database initialized ({db_type})")
        except Exception as e:
            print(f"[App] Database initialization error: {str(e)}")
            if USE_RDS:
                print("[App] Make sure RDS instance is running and credentials are correct")
            raise


if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Start scheduler (only if Lambda scheduler is not enabled)
    if not USE_LAMBDA_SCHEDULER:
        start_scheduler(app)
        atexit.register(stop_scheduler)
        print("[App] Local scheduler enabled")
    else:
        print("[App] Lambda scheduler enabled - local scheduler disabled")
    
    # Run app
    port = int(os.environ.get('PORT', 5001))  # Use 5001 to avoid AirPlay conflict on macOS
    print("[App] Starting AutoVault...")
    print(f"[App] Access the application at http://127.0.0.1:{port}")
    app.run(debug=True, host='127.0.0.1', port=port)

