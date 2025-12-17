# ⚡ S3 Quick Start Guide

## 🚀 5-Minute Setup

### 1. Create S3 Bucket
- Go to AWS Console → S3
- Click "Create bucket"
- Name: `autovault-files-yourname` (must be unique)
- Region: Choose closest to you
- Click "Create bucket"

### 2. Create IAM User
- Go to AWS Console → IAM → Users
- Click "Create user" → Name: `autovault-s3-user`
- Attach policy: `AmazonS3FullAccess`
- Create user → Go to "Security credentials" tab
- Click "Create access key" → Copy both keys

### 3. Configure AutoVault

**Option A: Environment Variables (Recommended)**
```bash
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="your-secret-key"
export AWS_REGION="us-east-1"
export S3_BUCKET_NAME="autovault-files-yourname"
export USE_S3="true"
```

**Option B: Edit config.py**
```python
USE_S3 = True
AWS_ACCESS_KEY_ID = 'AKIA...'
AWS_SECRET_ACCESS_KEY = 'your-secret-key'
AWS_REGION = 'us-east-1'
S3_BUCKET_NAME = 'autovault-files-yourname'
```

### 4. Install & Run
```bash
pip3 install boto3
python3 app.py
```

### 5. Verify
- Check console: Should see `[S3] S3 client initialized successfully`
- Upload a test file
- Check S3 bucket: Files should appear in `autovault/user_X/` folders

## ✅ Success Checklist

- [ ] S3 bucket created
- [ ] IAM user with S3 permissions created
- [ ] Access keys copied
- [ ] Credentials configured
- [ ] boto3 installed
- [ ] App starts without errors
- [ ] Test upload works
- [ ] Files visible in S3 bucket

## 🔄 Switch Back to Local

```bash
export USE_S3="false"
# Or edit config.py: USE_S3 = False
```

## 📖 Full Guide

See `S3_SETUP_GUIDE.md` for detailed instructions and troubleshooting.

