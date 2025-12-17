"""
AWS Lambda function for AutoVault file expiry and deletion
This function runs on a schedule to check for expired files and delete them
"""
import json
import boto3
import os
from datetime import datetime, timedelta
from botocore.exceptions import ClientError

# Initialize AWS clients
rds_client = boto3.client('rds')
s3_client = boto3.client('s3')
ses_client = boto3.client('ses')  # For email notifications

# Configuration from environment variables
RDS_ENDPOINT = os.environ.get('RDS_ENDPOINT')
RDS_PORT = int(os.environ.get('RDS_PORT', 5432))
RDS_DB_NAME = os.environ.get('RDS_DB_NAME', 'autovault')
RDS_USERNAME = os.environ.get('RDS_USERNAME')
RDS_PASSWORD = os.environ.get('RDS_PASSWORD')
S3_BUCKET_NAME = os.environ.get('S3_BUCKET_NAME')
S3_BUCKET_PREFIX = os.environ.get('S3_BUCKET_PREFIX', 'autovault')
NOTIFICATION_HOURS_BEFORE_EXPIRY = int(os.environ.get('NOTIFICATION_HOURS_BEFORE_EXPIRY', 24))
EMAIL_FROM = os.environ.get('EMAIL_FROM', '')

# PostgreSQL connection (using psycopg2)
import psycopg2
from psycopg2.extras import RealDictCursor


def get_db_connection():
    """Create database connection"""
    try:
        conn = psycopg2.connect(
            host=RDS_ENDPOINT,
            port=RDS_PORT,
            database=RDS_DB_NAME,
            user=RDS_USERNAME,
            password=RDS_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        raise


def send_email_notification(user_email, filename, expiry_time):
    """Send email notification using SES"""
    if not EMAIL_FROM:
        print(f"[Email] Skipping - EMAIL_FROM not configured")
        return False
    
    try:
        subject = f'AutoVault: File "{filename}" Expiring Soon'
        body = f"""
Hello,

This is an automated notification from AutoVault.

Your file "{filename}" will expire on {expiry_time.strftime('%Y-%m-%d %H:%M:%S UTC')}.

Please download it before it expires, as it will be automatically deleted.

Best regards,
AutoVault System
        """
        
        ses_client.send_email(
            Source=EMAIL_FROM,
            Destination={'ToAddresses': [user_email]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Text': {'Data': body}}
            }
        )
        
        print(f"[Email] Notification sent to {user_email} for file {filename}")
        return True
    except Exception as e:
        print(f"[Email] Failed to send to {user_email}: {str(e)}")
        return False


def delete_file_from_s3(user_id, filename):
    """Delete file from S3"""
    try:
        s3_key = f"{S3_BUCKET_PREFIX}/user_{user_id}/{filename}"
        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        print(f"[S3] Deleted: {s3_key}")
        return True
    except Exception as e:
        print(f"[S3] Failed to delete {filename}: {str(e)}")
        return False


def process_expired_files():
    """Main function to process expired files"""
    now = datetime.utcnow()
    notification_threshold = now + timedelta(hours=NOTIFICATION_HOURS_BEFORE_EXPIRY)
    
    deleted_count = 0
    notified_count = 0
    errors = []
    
    try:
        # Connect to database
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Get all files that need processing
        # Files expiring within the next (NOTIFICATION_HOURS_BEFORE_EXPIRY + 1) hours
        query = """
            SELECT f.id, f.user_id, f.filename, f.filepath, f.expiry_time, f.email_sent,
                   u.email as user_email
            FROM files f
            JOIN users u ON f.user_id = u.id
            WHERE f.expiry_time > %s - INTERVAL '%s hours'
            ORDER BY f.expiry_time ASC
        """
        
        hours_back = NOTIFICATION_HOURS_BEFORE_EXPIRY + 1
        cursor.execute(query, (now, hours_back))
        files = cursor.fetchall()
        
        print(f"[Lambda] Found {len(files)} files to check")
        
        for file in files:
            try:
                file_id = file['id']
                user_id = file['user_id']
                filename = file['filename']
                expiry_time = file['expiry_time']
                email_sent = file['email_sent']
                user_email = file['user_email']
                
                # Check if file has expired
                if expiry_time < now:
                    # Delete expired file
                    if delete_file_from_s3(user_id, filename):
                        # Delete from database
                        cursor.execute("DELETE FROM files WHERE id = %s", (file_id,))
                        deleted_count += 1
                        print(f"[Lambda] Deleted expired file: {filename} (ID: {file_id})")
                    else:
                        errors.append(f"Failed to delete file {filename} from S3")
                
                # Check if notification should be sent
                elif not email_sent and expiry_time <= notification_threshold:
                    if send_email_notification(user_email, filename, expiry_time):
                        # Mark email as sent
                        cursor.execute(
                            "UPDATE files SET email_sent = TRUE WHERE id = %s",
                            (file_id,)
                        )
                        notified_count += 1
                        print(f"[Lambda] Sent notification for: {filename}")
            
            except Exception as e:
                error_msg = f"Error processing file {file.get('id', 'unknown')}: {str(e)}"
                print(f"[Lambda] {error_msg}")
                errors.append(error_msg)
                continue
        
        # Commit all changes
        conn.commit()
        cursor.close()
        conn.close()
        
        result = {
            'deleted': deleted_count,
            'notified': notified_count,
            'errors': len(errors),
            'error_details': errors[:5]  # Limit error details
        }
        
        print(f"[Lambda] Processed: {deleted_count} deleted, {notified_count} notified")
        return result
        
    except Exception as e:
        print(f"[Lambda] Fatal error: {str(e)}")
        raise


def lambda_handler(event, context):
    """
    AWS Lambda handler function
    Called by EventBridge on schedule
    """
    print("=" * 60)
    print("AutoVault Lambda - File Expiry Processor")
    print(f"Triggered at: {datetime.utcnow().isoformat()}")
    print("=" * 60)
    
    try:
        result = process_expired_files()
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'File expiry processing completed',
                'deleted': result['deleted'],
                'notified': result['notified'],
                'errors': result['errors']
            })
        }
    
    except Exception as e:
        print(f"[Lambda] Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': 'File expiry processing failed',
                'error': str(e)
            })
        }

