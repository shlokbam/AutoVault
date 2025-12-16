from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from models import db, File
from config import (
    NOTIFICATION_HOURS_BEFORE_EXPIRY,
    SMTP_SERVER,
    SMTP_PORT,
    SMTP_USERNAME,
    SMTP_PASSWORD,
    EMAIL_FROM
)
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

scheduler = BackgroundScheduler()
app = None  # Will be set from app.py


def send_email_notification(user_email, filename, expiry_time):
    """Send email notification to user about file expiry"""
    if not SMTP_USERNAME or not SMTP_PASSWORD:
        print(f"[Email] Skipping email to {user_email} - SMTP not configured")
        return False
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_FROM
        msg['To'] = user_email
        msg['Subject'] = f'AutoVault: File "{filename}" Expiring Soon'
        
        body = f"""
Hello,

This is an automated notification from AutoVault.

Your file "{filename}" will expire on {expiry_time.strftime('%Y-%m-%d %H:%M:%S UTC')}.

Please download it before it expires, as it will be automatically deleted.

Best regards,
AutoVault System
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        print(f"[Email] Notification sent to {user_email} for file {filename}")
        return True
    except Exception as e:
        print(f"[Email] Failed to send notification to {user_email}: {str(e)}")
        return False


def process_expired_files():
    """Check and process expired files"""
    if app is None:
        print("[Scheduler] App context not available")
        return
    
    with app.app_context():
        now = datetime.utcnow()
        notification_threshold = now + timedelta(hours=NOTIFICATION_HOURS_BEFORE_EXPIRY)
        
        # Get all files that need processing
        files_to_check = File.query.filter(
            File.expiry_time > now - timedelta(hours=NOTIFICATION_HOURS_BEFORE_EXPIRY + 1)
        ).all()
        
        deleted_count = 0
        notified_count = 0
        
        for file in files_to_check:
            try:
                # Check if file has expired
                if file.is_expired():
                    # Delete expired file
                    if os.path.exists(file.filepath):
                        os.remove(file.filepath)
                    
                    db.session.delete(file)
                    deleted_count += 1
                    print(f"[Scheduler] Deleted expired file: {file.filename} (ID: {file.id})")
                
                # Check if notification should be sent
                elif not file.email_sent and file.expiry_time <= notification_threshold:
                    # Send notification
                    user_email = file.user.email
                    if send_email_notification(user_email, file.filename, file.expiry_time):
                        file.email_sent = True
                        notified_count += 1
            
            except Exception as e:
                print(f"[Scheduler] Error processing file {file.id}: {str(e)}")
                continue
        
        # Commit all changes
        try:
            db.session.commit()
            if deleted_count > 0 or notified_count > 0:
                print(f"[Scheduler] Processed: {deleted_count} deleted, {notified_count} notified")
        except Exception as e:
            db.session.rollback()
            print(f"[Scheduler] Error committing changes: {str(e)}")


def start_scheduler(flask_app=None):
    """Start the background scheduler"""
    global app
    if flask_app:
        app = flask_app
    
    if not scheduler.running:
        scheduler.add_job(
            func=process_expired_files,
            trigger=IntervalTrigger(minutes=60),  # Run every hour
            id='process_expired_files',
            name='Process expired files and send notifications',
            replace_existing=True
        )
        scheduler.start()
        print("[Scheduler] Background scheduler started")


def stop_scheduler():
    """Stop the background scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        print("[Scheduler] Background scheduler stopped")

