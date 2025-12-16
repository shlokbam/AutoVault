from flask import Flask, redirect, url_for
from flask_login import LoginManager
from models import db, User
from config import DATABASE_PATH, SECRET_KEY, UPLOAD_FOLDER
from auth import auth_bp
from files import files_bp
from scheduler import start_scheduler, stop_scheduler
import os
import atexit

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DATABASE_PATH}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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
        # Create uploads directory
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Create database tables
        db.create_all()
        print("[App] Database initialized")


if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Start scheduler with app context
    start_scheduler(app)
    
    # Register cleanup function
    atexit.register(stop_scheduler)
    
    # Run app
    print("[App] Starting AutoVault...")
    print("[App] Access the application at http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

