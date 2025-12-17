from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file, abort, jsonify
from flask_login import login_required, current_user
from models import db, File
from config import UPLOAD_FOLDER, MAX_FILE_SIZE, ALLOWED_EXTENSIONS, USE_S3
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
from scheduler import process_expired_files
from s3_storage import (
    upload_file_to_s3,
    download_file_from_s3,
    delete_file_from_s3,
    ensure_unique_filename_in_s3,
    file_exists_in_s3
)
import os

files_bp = Blueprint('files', __name__)


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@files_bp.route('/')
@files_bp.route('/dashboard')
@login_required
def dashboard():
    """Display user's files"""
    user_files = File.query.filter_by(user_id=current_user.id).order_by(File.upload_time.desc()).all()
    
    # Add status information
    files_data = []
    for file in user_files:
        files_data.append({
            'id': file.id,
            'filename': file.filename,
            'upload_time': file.upload_time,
            'expiry_time': file.expiry_time,
            'file_size': file.file_size,
            'is_expired': file.is_expired(),
            'hours_until_expiry': file.hours_until_expiry() if not file.is_expired() else 0
        })
    
    return render_template('dashboard.html', files=files_data)


@files_bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """Handle file upload"""
    if 'file' not in request.files:
        flash('No file selected.', 'error')
        return redirect(url_for('files.dashboard'))
    
    file = request.files['file']
    expiry_days = request.form.get('expiry_days', type=int)
    
    if file.filename == '':
        flash('No file selected.', 'error')
        return redirect(url_for('files.dashboard'))
    
    if not expiry_days or expiry_days < 1:
        flash('Please specify a valid expiry time (at least 1 day).', 'error')
        return redirect(url_for('files.dashboard'))
    
    if not allowed_file(file.filename):
        flash('File type not allowed.', 'error')
        return redirect(url_for('files.dashboard'))
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        flash(f'File size exceeds maximum allowed size ({MAX_FILE_SIZE // (1024*1024)}MB).', 'error')
        return redirect(url_for('files.dashboard'))
    
    try:
        # Secure filename
        filename = secure_filename(file.filename)
        
        if USE_S3:
            # Use S3 storage
            # Ensure unique filename in S3
            filename = ensure_unique_filename_in_s3(current_user.id, filename)
            
            # Upload to S3
            success, result = upload_file_to_s3(file, current_user.id, filename)
            if not success:
                flash(f'Upload failed: {result}', 'error')
                return redirect(url_for('files.dashboard'))
            
            s3_key = result  # result is the S3 key
            filepath = s3_key  # Store S3 key as filepath
        else:
            # Use local storage (fallback)
            user_dir = os.path.join(UPLOAD_FOLDER, f'user_{current_user.id}')
            os.makedirs(user_dir, exist_ok=True)
            
            # Ensure unique filename
            base_name, ext = os.path.splitext(filename)
            counter = 1
            filepath = os.path.join(user_dir, filename)
            
            while os.path.exists(filepath):
                filename = f"{base_name}_{counter}{ext}"
                filepath = os.path.join(user_dir, filename)
                counter += 1
            
            # Save file locally
            file.save(filepath)
        
        # Calculate expiry time
        expiry_time = datetime.utcnow() + timedelta(days=expiry_days)
        
        # Save to database
        new_file = File(
            user_id=current_user.id,
            filename=filename,
            filepath=filepath,  # S3 key or local path
            file_size=file_size,
            expiry_time=expiry_time
        )
        db.session.add(new_file)
        db.session.commit()
        
        storage_type = "S3" if USE_S3 else "local"
        flash(f'File "{filename}" uploaded successfully to {storage_type}!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Upload failed: {str(e)}', 'error')
    
    return redirect(url_for('files.dashboard'))


@files_bp.route('/download/<int:file_id>')
@login_required
def download_file(file_id):
    """Download a file"""
    file_record = File.query.get_or_404(file_id)
    
    # Check ownership
    if file_record.user_id != current_user.id:
        abort(403)
    
    try:
        if USE_S3:
            # Download from S3
            success, result = download_file_from_s3(file_record.user_id, file_record.filename)
            if not success:
                flash(f'Download failed: {result}', 'error')
                return redirect(url_for('files.dashboard'))
            
            # result is a BytesIO object
            file_data = result
            return send_file(
                file_data,
                as_attachment=True,
                download_name=file_record.filename,
                mimetype='application/octet-stream'
            )
        else:
            # Download from local storage
            if not os.path.exists(file_record.filepath):
                flash('File not found on server.', 'error')
                return redirect(url_for('files.dashboard'))
            
            return send_file(
                file_record.filepath,
                as_attachment=True,
                download_name=file_record.filename
            )
    except Exception as e:
        flash(f'Download failed: {str(e)}', 'error')
        return redirect(url_for('files.dashboard'))


@files_bp.route('/delete/<int:file_id>', methods=['POST'])
@login_required
def delete_file(file_id):
    """Delete a file"""
    file_record = File.query.get_or_404(file_id)
    
    # Check ownership
    if file_record.user_id != current_user.id:
        abort(403)
    
    try:
        if USE_S3:
            # Delete from S3
            success, message = delete_file_from_s3(file_record.user_id, file_record.filename)
            if not success:
                flash(f'Delete failed: {message}', 'error')
                return redirect(url_for('files.dashboard'))
        else:
            # Delete from local filesystem
            if os.path.exists(file_record.filepath):
                os.remove(file_record.filepath)
        
        # Delete from database
        db.session.delete(file_record)
        db.session.commit()
        
        storage_type = "S3" if USE_S3 else "local"
        flash(f'File "{file_record.filename}" deleted successfully from {storage_type}.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Delete failed: {str(e)}', 'error')
    
    return redirect(url_for('files.dashboard'))


@files_bp.route('/test-scheduler', methods=['POST'])
@login_required
def test_scheduler():
    """Manually trigger scheduler for testing"""
    try:
        # Count files before
        files_before = File.query.count()
        
        # Run scheduler
        process_expired_files()
        
        # Count files after
        files_after = File.query.count()
        deleted = files_before - files_after
        
        flash(f'Scheduler test completed. {deleted} file(s) deleted.', 'success')
    except Exception as e:
        flash(f'Scheduler test failed: {str(e)}', 'error')
    
    return redirect(url_for('files.dashboard'))

