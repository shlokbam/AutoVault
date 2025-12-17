"""
S3 Storage Utility
Handles file upload, download, and deletion from Amazon S3
"""
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from config import (
    USE_S3,
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_REGION,
    S3_BUCKET_NAME,
    S3_BUCKET_PREFIX
)
import os
from werkzeug.utils import secure_filename
from io import BytesIO

# Initialize S3 client
s3_client = None
if USE_S3:
    try:
        if AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
            s3_client = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_REGION
            )
        else:
            # Try to use default credentials (from ~/.aws/credentials or IAM role)
            s3_client = boto3.client('s3', region_name=AWS_REGION)
        print("[S3] S3 client initialized successfully")
    except NoCredentialsError:
        print("[S3] Warning: AWS credentials not found. S3 functionality disabled.")
        s3_client = None
        USE_S3 = False
    except Exception as e:
        print(f"[S3] Error initializing S3 client: {str(e)}")
        s3_client = None
        USE_S3 = False


def get_s3_key(user_id, filename):
    """Generate S3 key (path) for a file"""
    safe_filename = secure_filename(filename)
    return f"{S3_BUCKET_PREFIX}/user_{user_id}/{safe_filename}"


def upload_file_to_s3(file_obj, user_id, filename):
    """
    Upload a file to S3
    
    Args:
        file_obj: File-like object (from Flask request.files)
        user_id: User ID
        filename: Original filename
    
    Returns:
        tuple: (success: bool, s3_key: str or error_message: str)
    """
    if not USE_S3 or not s3_client:
        return False, "S3 not configured"
    
    if not S3_BUCKET_NAME:
        return False, "S3 bucket name not configured"
    
    try:
        s3_key = get_s3_key(user_id, filename)
        
        # Reset file pointer to beginning
        file_obj.seek(0)
        
        # Upload to S3
        # Get content type if available
        content_type = 'application/octet-stream'
        if hasattr(file_obj, 'content_type') and file_obj.content_type:
            content_type = file_obj.content_type
        elif hasattr(file_obj, 'filename') and file_obj.filename:
            # Try to guess from filename
            import mimetypes
            guessed_type, _ = mimetypes.guess_type(file_obj.filename)
            if guessed_type:
                content_type = guessed_type
        
        s3_client.upload_fileobj(
            file_obj,
            S3_BUCKET_NAME,
            s3_key,
            ExtraArgs={'ContentType': content_type}
        )
        
        print(f"[S3] File uploaded: {s3_key}")
        return True, s3_key
    
    except ClientError as e:
        error_msg = f"AWS S3 error: {str(e)}"
        print(f"[S3] Upload failed: {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = f"Upload error: {str(e)}"
        print(f"[S3] Upload failed: {error_msg}")
        return False, error_msg


def download_file_from_s3(user_id, filename):
    """
    Download a file from S3
    
    Args:
        user_id: User ID
        filename: Filename
    
    Returns:
        tuple: (success: bool, file_data: BytesIO or error_message: str)
    """
    if not USE_S3 or not s3_client:
        return False, "S3 not configured"
    
    if not S3_BUCKET_NAME:
        return False, "S3 bucket name not configured"
    
    try:
        s3_key = get_s3_key(user_id, filename)
        
        # Download from S3
        file_obj = BytesIO()
        s3_client.download_fileobj(S3_BUCKET_NAME, s3_key, file_obj)
        file_obj.seek(0)
        
        print(f"[S3] File downloaded: {s3_key}")
        return True, file_obj
    
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            error_msg = "File not found in S3"
        else:
            error_msg = f"AWS S3 error: {str(e)}"
        print(f"[S3] Download failed: {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = f"Download error: {str(e)}"
        print(f"[S3] Download failed: {error_msg}")
        return False, error_msg


def delete_file_from_s3(user_id, filename):
    """
    Delete a file from S3
    
    Args:
        user_id: User ID
        filename: Filename
    
    Returns:
        tuple: (success: bool, message: str)
    """
    if not USE_S3 or not s3_client:
        return False, "S3 not configured"
    
    if not S3_BUCKET_NAME:
        return False, "S3 bucket name not configured"
    
    try:
        s3_key = get_s3_key(user_id, filename)
        
        # Delete from S3
        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        
        print(f"[S3] File deleted: {s3_key}")
        return True, "File deleted successfully"
    
    except ClientError as e:
        error_msg = f"AWS S3 error: {str(e)}"
        print(f"[S3] Delete failed: {error_msg}")
        return False, error_msg
    except Exception as e:
        error_msg = f"Delete error: {str(e)}"
        print(f"[S3] Delete failed: {error_msg}")
        return False, error_msg


def file_exists_in_s3(user_id, filename):
    """
    Check if a file exists in S3
    
    Args:
        user_id: User ID
        filename: Filename
    
    Returns:
        bool: True if file exists, False otherwise
    """
    if not USE_S3 or not s3_client:
        return False
    
    if not S3_BUCKET_NAME:
        return False
    
    try:
        s3_key = get_s3_key(user_id, filename)
        s3_client.head_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return False
        return False
    except Exception:
        return False


def ensure_unique_filename_in_s3(user_id, filename):
    """
    Ensure filename is unique in S3 by appending counter if needed
    
    Args:
        user_id: User ID
        filename: Original filename
    
    Returns:
        str: Unique filename
    """
    if not file_exists_in_s3(user_id, filename):
        return filename
    
    base_name, ext = os.path.splitext(filename)
    counter = 1
    while True:
        new_filename = f"{base_name}_{counter}{ext}"
        if not file_exists_in_s3(user_id, new_filename):
            return new_filename
        counter += 1

