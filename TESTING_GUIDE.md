# 🧪 AutoVault Scheduler Testing Guide

This guide explains how to test the scheduler functionality (email notifications and automatic file deletion).

## 📋 Testing Methods

### Method 1: Using the Test Script (Recommended)

The `test_scheduler.py` script provides several testing commands:

#### 1. Test Email Notification Directly
```bash
python3 test_scheduler.py test-email your-email@gmail.com
```
This will immediately send a test email to verify SMTP configuration.

#### 2. Create a Test File with Short Expiry
```bash
# Create a file that expires in 1 minute
python3 test_scheduler.py create your-email@gmail.com 1

# Create a file that expires in 5 minutes
python3 test_scheduler.py create your-email@gmail.com 5
```

#### 3. Manually Run the Scheduler
```bash
python3 test_scheduler.py run
```
This will immediately process all files (delete expired, send notifications).

#### 4. List All Files
```bash
python3 test_scheduler.py list
```
Shows all files in the database with their status.

### Method 2: Using the Web Interface

1. **Login to your account** at `http://127.0.0.1:5001`
2. **Click "🔄 Test Scheduler"** button on the dashboard
   - This manually triggers the scheduler
   - Shows how many files were deleted

### Method 3: Wait for Automatic Execution

The scheduler runs automatically every hour. To test:
1. Create a file with expiry time set to 1-2 minutes from now
2. Wait for the scheduler to run (or trigger manually)
3. Check if the file is deleted

## 🧪 Step-by-Step Testing

### Test 1: Email Notification

1. **Create a test file that expires in 25 hours** (to trigger notification):
   ```bash
   python3 test_scheduler.py create your-email@gmail.com 1500
   ```
   (1500 minutes = 25 hours, which is > 24 hours before expiry)

2. **Manually run the scheduler**:
   ```bash
   python3 test_scheduler.py run
   ```
   OR click "Test Scheduler" button in the web interface

3. **Check your email** - You should receive a notification

4. **Verify in database**:
   ```bash
   python3 test_scheduler.py list
   ```
   The file should show `email_sent: True`

### Test 2: File Deletion

1. **Create a test file that expires in 1 minute**:
   ```bash
   python3 test_scheduler.py create your-email@gmail.com 1
   ```

2. **Wait 2 minutes** (or manually set expiry time in database)

3. **Manually run the scheduler**:
   ```bash
   python3 test_scheduler.py run
   ```

4. **Verify deletion**:
   ```bash
   python3 test_scheduler.py list
   ```
   The expired file should be removed from the list

5. **Check filesystem**:
   ```bash
   ls -la uploads/user_*/
   ```
   The physical file should also be deleted

### Test 3: Full Workflow

1. **Create a file expiring in 2 minutes**:
   ```bash
   python3 test_scheduler.py create your-email@gmail.com 2
   ```

2. **Wait 3 minutes**

3. **Run scheduler**:
   ```bash
   python3 test_scheduler.py run
   ```

4. **Check results**:
   - File should be deleted from database
   - File should be deleted from filesystem
   - Check console output for deletion messages

## 🔍 Monitoring Scheduler Activity

### Check Console Output

When the scheduler runs, you'll see messages like:
```
[Scheduler] Deleted expired file: test_file.txt (ID: 1)
[Email] Notification sent to user@example.com for file example.pdf
[Scheduler] Processed: 1 deleted, 1 notified
```

### Check Database Directly

You can use Python to inspect the database:
```python
from app import app
from models import db, File, User

with app.app_context():
    files = File.query.all()
    for f in files:
        print(f"{f.filename}: expires {f.expiry_time}, email_sent: {f.email_sent}")
```

## ⚙️ Adjusting Scheduler Frequency for Testing

To test more quickly, you can temporarily change the scheduler interval in `scheduler.py`:

```python
# Change from 60 minutes to 1 minute for testing
trigger=IntervalTrigger(minutes=1)
```

**Remember to change it back to 60 minutes for production!**

## 🐛 Troubleshooting

### Email Not Sending

1. **Check SMTP credentials** in `config.py`
2. **Test email directly**:
   ```bash
   python3 test_scheduler.py test-email your-email@gmail.com
   ```
3. **Check console for errors** - Look for `[Email] Failed to send...` messages
4. **Verify Gmail App Password** - Make sure you're using an App Password, not your regular password

### Files Not Deleting

1. **Check if files are actually expired**:
   ```bash
   python3 test_scheduler.py list
   ```
2. **Manually trigger scheduler**:
   ```bash
   python3 test_scheduler.py run
   ```
3. **Check console output** for error messages
4. **Verify file paths** exist in the filesystem

### Scheduler Not Running

1. **Check if scheduler started** - Look for `[Scheduler] Background scheduler started` in console
2. **Verify app is running** - The scheduler only runs when the Flask app is running
3. **Check for errors** in the console output

## 📊 Expected Behavior

- **Email notifications**: Sent 24 hours before file expiry (if not already sent)
- **File deletion**: Happens immediately when file expires
- **Scheduler frequency**: Runs every hour automatically
- **Email sent flag**: Set to `True` after successful email send

## ✅ Success Criteria

Your scheduler is working correctly if:
1. ✅ Test emails are received
2. ✅ Expired files are automatically deleted from database
3. ✅ Expired files are automatically deleted from filesystem
4. ✅ Email notifications are sent 24 hours before expiry
5. ✅ Console shows scheduler activity messages

