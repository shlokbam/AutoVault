# ⚡ Lambda Quick Start Guide

## 🚀 15-Minute Setup

### 1. Deploy Lambda Package

```bash
chmod +x deploy_lambda.sh
./deploy_lambda.sh
```

This creates `lambda_function.zip`

### 2. Create Lambda Function

1. **AWS Console → Lambda → Create function**
   - Name: `autovault-expiry-processor`
   - Runtime: Python 3.11
   - Click "Create"

2. **Upload code**:
   - Upload `lambda_function.zip`
   - Click "Save"

### 3. Configure Environment Variables

Go to **Configuration → Environment variables**, add:

```
RDS_ENDPOINT = your-rds-endpoint.rds.amazonaws.com
RDS_PORT = 5432
RDS_DB_NAME = autovault
RDS_USERNAME = autovault_admin
RDS_PASSWORD = your-password
S3_BUCKET_NAME = autovault-files
S3_BUCKET_PREFIX = autovault
NOTIFICATION_HOURS_BEFORE_EXPIRY = 24
EMAIL_FROM = your-email@gmail.com
```

### 4. Set Permissions

**Configuration → Permissions → Execution role**:
- Add policies:
  - `AmazonRDSFullAccess`
  - `AmazonS3FullAccess`
  - `AmazonSESFullAccess`

### 5. Configure Timeout

**Configuration → General configuration**:
- Timeout: 5 minutes
- Memory: 256 MB

### 6. Create EventBridge Rule

1. **EventBridge → Rules → Create rule**
   - Name: `autovault-expiry-check`
   - Schedule: `rate(1 hour)`
   - Target: Lambda function → `autovault-expiry-processor`

### 7. Test Lambda

1. **Lambda Console → Test**
2. Create test event (any JSON)
3. Click "Test"
4. Check CloudWatch Logs for results

### 8. Disable Local Scheduler (Optional)

Edit `config.py`:
```python
USE_LAMBDA_SCHEDULER = True
```

Or set environment variable:
```bash
export USE_LAMBDA_SCHEDULER="true"
```

## ✅ Success Checklist

- [ ] Lambda function created
- [ ] Code uploaded
- [ ] Environment variables set
- [ ] Permissions configured
- [ ] EventBridge rule created
- [ ] Test execution successful
- [ ] CloudWatch logs show activity

## 📖 Full Guide

See `LAMBDA_SETUP_GUIDE.md` for detailed instructions.

