# 🔐 AutoVault

**Secure File Storage with Automated Expiry Management**

AutoVault is a cloud-native file storage web application that provides secure, time-limited file storage with automated expiry notifications and cleanup. Built with Flask and AWS, it ensures complete data privacy through user authentication and automatic file lifecycle management.

---

## 🌟 Key Features

### Core Functionality
- **🔒 Secure Authentication**: User signup/login with password hashing
- **📁 File Management**: Upload, download, view, and delete files
- **⏰ Time-Limited Storage**: Set custom expiry times for each file (in days)
- **📧 Email Notifications**: Automatic alerts 24 hours before file expiry
- **🗑️ Auto-Cleanup**: Expired files are automatically deleted
- **👤 User Isolation**: Each user can only access their own files

### Technical Highlights
- **Dual Storage Mode**: Local filesystem or AWS S3
- **Flexible Database**: SQLite (local) or PostgreSQL/RDS (cloud)
- **Dual Scheduler**: Local APScheduler or AWS Lambda + EventBridge
- **Cloud-Ready**: Seamless migration path to AWS infrastructure

---

## 📸 AWS Deployment Overview

Based on your deployment, AutoVault is running with:

| Service | Status | Configuration |
|---------|--------|---------------|
| **AWS Lambda** | ✅ Active | `autovault-expiry-processor` (Python 3.11) |
| **EventBridge** | ✅ Enabled | Runs every 1 hour |
| **RDS PostgreSQL** | ✅ Running | `autovault-db` (db.t4g.micro, ap-south-1a) |
| **S3 Bucket** | ✅ Active | `autovault-files` (Mumbai region) |
| **IAM Role** | ✅ Configured | Full RDS, S3, SES permissions |

### AWS Lambda Function
![Lambda Function Overview](./docs/images/lambda-function.png)
*Image 3: Lambda function configuration showing Python 3.11 runtime and function code*

### EventBridge Scheduler
![EventBridge Rule](./docs/images/eventbridge-rule.png)
*Image 2: EventBridge rule configured to trigger Lambda every 1 hour*

### CloudWatch Logs
![CloudWatch Logs](./docs/images/cloudwatch-logs.png)
*Image 1: Recent Lambda execution logs showing file processing*

### Recent Lambda Execution (Dec 17, 2025)
```
[Lambda] Found 1 files to check
[Lambda] Processed: 0 deleted, 0 notified
Duration: 406.60 ms | Memory: 1386 ms
```

### RDS Database
![RDS Database](./docs/images/rds-database.png)
*Image 4: RDS PostgreSQL instance with VPC configuration and Lambda connection*

### S3 Bucket
![S3 Bucket](./docs/images/s3-bucket.png)
*Image 5: S3 bucket storing user files in Mumbai region*

### IAM Role Permissions
![IAM Role](./docs/images/iam-role.png)
*Image 6: IAM role with RDS, S3, and SES permissions for Lambda*

---

## 🏗️ Architecture

### System Architecture Diagram
![AutoVault Architecture](./docs/images/architecture-diagram.png)
*Complete system architecture showing all AWS services and their interactions*

### Text-based Architecture
```
┌─────────────┐
│   User      │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────┐
│     Flask Web Application       │
│  (Authentication & File Mgmt)   │
└────┬────────────────────┬───────┘
     │                    │
     ▼                    ▼
┌─────────┐        ┌──────────┐
│   RDS   │        │    S3    │
│PostgreSQL│        │  Bucket  │
└─────────┘        └──────────┘
     │                    │
     └────────┬───────────┘
              ▼
     ┌─────────────────┐
     │  Lambda Function │
     │  (Cron Scheduler)│
     └────────┬─────────┘
              ▼
         ┌─────────┐
         │   SES   │
         │ (Email) │
         └─────────┘
```

---

## 🚀 Quick Start

### Prerequisites
```bash
# Python 3.8+
python --version

# pip
pip --version

# AWS CLI (for cloud deployment)
aws --version
```

### Local Development Setup

1. **Clone the repository**
```bash
git clone https://github.com/shlokbam/AutoVault.git
cd AutoVault
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
# Create .env file
cp .env.example .env

# Edit .env with your settings
nano .env
```

4. **Run the application**
```bash
python app.py
```

5. **Access the app**
```
http://127.0.0.1:5001
```

---

## ⚙️ Configuration

### Environment Variables

#### Database Configuration
```bash
# Use RDS (set to 'true' for cloud, 'false' for local SQLite)
USE_RDS=true

# RDS Connection (when USE_RDS=true)
DATABASE_URL=postgresql://user:pass@host:5432/dbname
# OR individual components:
RDS_HOST=autovault-db.xxxxx.ap-south-1.rds.amazonaws.com
RDS_PORT=5432
RDS_DB_NAME=autovault
RDS_USERNAME=postgres
RDS_PASSWORD=your_password
```

#### Storage Configuration
```bash
# Use S3 (set to 'true' for cloud, 'false' for local filesystem)
USE_S3=true

# S3 Settings
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=ap-south-1
S3_BUCKET_NAME=autovault-files
S3_BUCKET_PREFIX=autovault
```

#### Scheduler Configuration
```bash
# Use Lambda scheduler (set to 'true' for cloud, 'false' for local)
USE_LAMBDA_SCHEDULER=true

# Local scheduler runs every hour when USE_LAMBDA_SCHEDULER=false
```

#### Email Configuration
```bash
# SMTP Settings (for local scheduler)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
EMAIL_FROM=your_email@gmail.com

# Notification timing
NOTIFICATION_HOURS_BEFORE_EXPIRY=24
```

#### Security
```bash
# Secret key for session management
SECRET_KEY=your-secret-key-change-in-production
```

---

## 📦 Project Structure

```
AutoVault/
├── app.py                      # Main Flask application
├── auth.py                     # Authentication routes (signup/login/logout)
├── files.py                    # File management routes (upload/download/delete)
├── models.py                   # Database models (User, File)
├── config.py                   # Configuration management
├── scheduler.py                # Local background scheduler
├── s3_storage.py              # AWS S3 integration
├── lambda_function.py         # AWS Lambda handler
├── requirements.txt           # Python dependencies
├── lambda_requirements.txt    # Lambda-specific dependencies
├── deploy_lambda.sh           # Lambda deployment script
│
├── templates/                 # HTML templates
│   ├── login.html
│   ├── signup.html
│   └── dashboard.html
│
├── static/                    # Static assets
│   ├── css/
│   └── js/
│
├── uploads/                   # Local file storage (when S3 disabled)
│
└── docs/                      # Documentation
    ├── S3_SETUP_GUIDE.md
    ├── RDS_SETUP_GUIDE.md
    ├── LAMBDA_SETUP_GUIDE.md
    └── TESTING_GUIDE.md
```

---

## 🔄 How It Works

### 1. User Registration & Login
- Users create accounts with email and password
- Passwords are hashed using Werkzeug's security functions
- Flask-Login manages session persistence

### 2. File Upload
- User selects file and sets expiry time (in days)
- File is uploaded to S3 (or local storage)
- Metadata stored in database (RDS or SQLite)
- `email_sent` flag initialized to `False`

### 3. Automated Processing
**Every hour**, the scheduler (Lambda or local) runs:

```python
# Check files
for each file:
    if file.expired:
        delete_from_s3()
        delete_from_database()
    
    elif file.expiring_within_24h and not file.email_sent:
        send_email_notification()
        mark_email_as_sent()
```

### 4. Email Notifications
- Sent 24 hours before expiry
- Uses AWS SES (cloud) or SMTP (local)
- Email marked as sent to avoid duplicates

### 5. File Deletion
- Expired files removed from S3/filesystem
- Database records deleted
- User no longer sees file in dashboard

---

## 🛠️ AWS Deployment Guide

### Step 1: RDS Database Setup

```bash
# 1. Create RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier autovault-db \
  --db-instance-class db.t4g.micro \
  --engine postgres \
  --master-username postgres \
  --master-user-password <password> \
  --allocated-storage 20

# 2. Update security group for inbound access
# 3. Run database initialization
python create_rds_database.py
```

### Step 2: S3 Bucket Setup

```bash
# 1. Create S3 bucket
aws s3 mb s3://autovault-files --region ap-south-1

# 2. Set bucket policy for private access
aws s3api put-bucket-versioning \
  --bucket autovault-files \
  --versioning-configuration Status=Enabled
```

### Step 3: Lambda Function Deployment

```bash
# 1. Package Lambda function
./deploy_lambda.sh

# 2. Create Lambda function
aws lambda create-function \
  --function-name autovault-expiry-processor \
  --runtime python3.11 \
  --handler lambda_function.lambda_handler \
  --zip-file fileb://lambda_function.zip \
  --role arn:aws:iam::ACCOUNT_ID:role/autovault-expiry-processor-role

# 3. Set environment variables
aws lambda update-function-configuration \
  --function-name autovault-expiry-processor \
  --environment Variables="{
    RDS_ENDPOINT=autovault-db.xxxxx.rds.amazonaws.com,
    RDS_DB_NAME=autovault,
    S3_BUCKET_NAME=autovault-files,
    ...
  }"
```

### Step 4: EventBridge Schedule

```bash
# Create EventBridge rule (runs every hour)
aws events put-rule \
  --name autovault-expiry-check \
  --schedule-expression "rate(1 hour)"

# Add Lambda as target
aws events put-targets \
  --rule autovault-expiry-check \
  --targets "Id"="1","Arn"="arn:aws:lambda:REGION:ACCOUNT:function:autovault-expiry-processor"
```

---

## 🧪 Testing

### Test Scheduler Manually
Click the **"Test Scheduler"** button in the dashboard to run the expiry check immediately.

```bash
# Or via command line
python test_scheduler.py
```

### Test File Upload/Download
1. Sign up and log in
2. Upload a test file with 1-day expiry
3. Verify file appears in dashboard
4. Download the file
5. Wait for expiry and check auto-deletion

### Test Email Notifications
1. Upload file with 1-day expiry
2. Manually set `expiry_time` to tomorrow in database
3. Run scheduler test
4. Check email inbox for notification

---

## 📊 Monitoring

### Lambda CloudWatch Logs
View execution logs in AWS CloudWatch:
```
/aws/lambda/autovault-expiry-processor
```

### Key Metrics to Monitor
- **Lambda Invocations**: Should run every hour
- **Lambda Duration**: Typical 400-500ms
- **Files Processed**: Deleted and notified counts
- **S3 Storage**: Monitor bucket size
- **RDS Connections**: Check connection pool health

### Latest Lambda Execution
```
2025-12-17 07:37:16.702Z - Found 1 files to check
2025-12-17 07:37:17.109Z - Processed: 0 deleted, 0 notified
Duration: 406.60 ms
Memory: 1386 ms
```

---

## 🔒 Security Best Practices

### Application Security
- ✅ Passwords hashed with Werkzeug's `generate_password_hash`
- ✅ SQL injection protection via SQLAlchemy ORM
- ✅ CSRF protection (Flask-WTF can be added)
- ✅ Secure session cookies with `SECRET_KEY`
- ✅ User isolation (each user sees only their files)

### AWS Security
- ✅ RDS in private subnet with security group restrictions
- ✅ S3 bucket with private ACL
- ✅ IAM role with least-privilege permissions
- ✅ Lambda VPC configuration for RDS access
- ✅ Environment variables for sensitive data (not hardcoded)

### Recommendations
- 🔐 Enable HTTPS in production (use ALB with SSL)
- 🔐 Use AWS Secrets Manager for credentials
- 🔐 Enable RDS encryption at rest
- 🔐 Enable S3 bucket encryption
- 🔐 Add rate limiting to prevent abuse
- 🔐 Implement MFA for user accounts

---

## 🐛 Troubleshooting

### Issue: Files not deleting automatically
**Solution**: 
1. Check Lambda logs in CloudWatch
2. Verify EventBridge rule is enabled
3. Ensure Lambda has S3 and RDS permissions
4. Check `USE_LAMBDA_SCHEDULER=true` in config

### Issue: Email notifications not sending
**Solution**:
1. For AWS SES: Verify sender email in SES console
2. For SMTP: Check credentials and app password
3. Verify `EMAIL_FROM` is set correctly
4. Check CloudWatch logs for email errors

### Issue: Database connection errors
**Solution**:
1. Verify RDS security group allows Lambda access
2. Check RDS endpoint and credentials
3. Ensure Lambda is in same VPC as RDS
4. Test connection: `python create_rds_database.py`

### Issue: S3 upload failures
**Solution**:
1. Verify S3 bucket exists and is in correct region
2. Check IAM permissions for S3 PutObject
3. Ensure bucket name matches config
4. Test with: `aws s3 ls s3://autovault-files`

---

## 📈 Performance Optimization

### Current Configuration
- **Lambda Memory**: 128 MB (sufficient for current load)
- **Lambda Timeout**: 30 seconds
- **RDS Instance**: db.t4g.micro (suitable for small-medium load)
- **Scheduler Frequency**: 1 hour

### Scaling Recommendations
| User Count | RDS Instance | Lambda Memory | S3 Strategy |
|------------|--------------|---------------|-------------|
| < 100 | db.t4g.micro | 128 MB | Single bucket |
| 100-1000 | db.t4g.small | 256 MB | Single bucket |
| 1000-10000 | db.t4g.medium | 512 MB | Sharded buckets |
| 10000+ | db.r6g.large | 1024 MB | Multi-region |

---

## 💰 Cost Estimation (AWS)

Based on my current setup in `ap-south-1` (Mumbai):

| Service | Usage | Monthly Cost (USD) |
|---------|-------|-------------------|
| RDS (db.t4g.micro) | 24/7 running | ~$15 |
| S3 Storage | 10 GB stored | ~$0.25 |
| S3 Requests | 10,000 requests | ~$0.05 |
| Lambda | 720 invocations/month | Free tier |
| EventBridge | 720 events/month | Free tier |
| SES | 1,000 emails/month | Free tier |
| **Total** | | **~$15.30/month** |

*Note: Actual costs depend on usage patterns*

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 👨‍💻 Author

**Shlok Bam**
- GitHub: [@shlokbam](https://github.com/shlokbam)
- AWS Account: 3959-3823-3260

---
