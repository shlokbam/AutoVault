"""
Test script for scheduler functionality
This script helps test email notifications and file deletion
"""
from app import app
from models import db, User, File
from scheduler import process_expired_files, send_email_notification
from datetime import datetime, timedelta
import os

def create_test_file(user_email, filename="test_file.txt", expiry_minutes=2):
    """Create a test file that expires in specified minutes"""
    with app.app_context():
        # Find or create test user
        user = User.query.filter_by(email=user_email).first()
        if not user:
            print(f"User {user_email} not found. Please create an account first.")
            return None
        
        # Create test file content
        test_content = f"Test file created at {datetime.utcnow()}\nExpires in {expiry_minutes} minutes"
        user_dir = os.path.join('uploads', f'user_{user.id}')
        os.makedirs(user_dir, exist_ok=True)
        
        filepath = os.path.join(user_dir, filename)
        with open(filepath, 'w') as f:
            f.write(test_content)
        
        # Calculate expiry time
        expiry_time = datetime.utcnow() + timedelta(minutes=expiry_minutes)
        
        # Create file record
        test_file = File(
            user_id=user.id,
            filename=filename,
            filepath=filepath,
            file_size=len(test_content),
            expiry_time=expiry_time,
            email_sent=False
        )
        
        db.session.add(test_file)
        db.session.commit()
        
        print(f"✅ Created test file: {filename}")
        print(f"   Expires at: {expiry_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
        print(f"   File path: {filepath}")
        return test_file


def test_email_notification(user_email):
    """Test email notification function directly"""
    print("\n📧 Testing email notification...")
    filename = "test_notification.txt"
    expiry_time = datetime.utcnow() + timedelta(hours=1)
    
    result = send_email_notification(user_email, filename, expiry_time)
    if result:
        print(f"✅ Email sent successfully to {user_email}")
    else:
        print(f"❌ Failed to send email to {user_email}")
    return result


def test_scheduler_manually():
    """Manually trigger the scheduler to test it"""
    print("\n🔄 Running scheduler manually...")
    with app.app_context():
        # Get all files
        all_files = File.query.all()
        print(f"Found {len(all_files)} files in database")
        
        for file in all_files:
            print(f"\n  File: {file.filename}")
            print(f"    Expiry: {file.expiry_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            print(f"    Expired: {file.is_expired()}")
            print(f"    Email sent: {file.email_sent}")
            print(f"    File exists: {os.path.exists(file.filepath)}")
        
        # Run scheduler
        process_expired_files()
        
        # Check results
        remaining_files = File.query.all()
        print(f"\n✅ Scheduler completed. {len(remaining_files)} files remaining")


def list_all_files():
    """List all files in the database"""
    with app.app_context():
        files = File.query.all()
        if not files:
            print("No files in database")
            return
        
        print("\n📁 All files in database:")
        print("-" * 80)
        for file in files:
            user = User.query.get(file.user_id)
            status = "EXPIRED" if file.is_expired() else "ACTIVE"
            print(f"ID: {file.id} | {file.filename} | User: {user.email}")
            print(f"  Expiry: {file.expiry_time.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            print(f"  Status: {status} | Email sent: {file.email_sent}")
            print(f"  File exists: {os.path.exists(file.filepath)}")
            print("-" * 80)


if __name__ == '__main__':
    import sys
    
    print("=" * 80)
    print("AutoVault Scheduler Test Tool")
    print("=" * 80)
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python3 test_scheduler.py create <email> [expiry_minutes]")
        print("    - Create a test file that expires in specified minutes (default: 2)")
        print("\n  python3 test_scheduler.py test-email <email>")
        print("    - Test email notification directly")
        print("\n  python3 test_scheduler.py run")
        print("    - Manually trigger the scheduler")
        print("\n  python3 test_scheduler.py list")
        print("    - List all files in database")
        print("\nExamples:")
        print("  python3 test_scheduler.py create test@example.com 1")
        print("  python3 test_scheduler.py test-email test@example.com")
        print("  python3 test_scheduler.py run")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'create':
        if len(sys.argv) < 3:
            print("Error: Email required")
            sys.exit(1)
        email = sys.argv[2]
        expiry_minutes = int(sys.argv[3]) if len(sys.argv) > 3 else 2
        create_test_file(email, f"test_expires_in_{expiry_minutes}min.txt", expiry_minutes)
    
    elif command == 'test-email':
        if len(sys.argv) < 3:
            print("Error: Email required")
            sys.exit(1)
        email = sys.argv[2]
        test_email_notification(email)
    
    elif command == 'run':
        test_scheduler_manually()
    
    elif command == 'list':
        list_all_files()
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

