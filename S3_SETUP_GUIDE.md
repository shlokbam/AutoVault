# 🚀 Amazon S3 Setup Guide for AutoVault

This guide will walk you through setting up Amazon S3 for file storage in AutoVault.

## 📋 Prerequisites

1. **AWS Account**: You need an AWS account (free tier is fine)
2. **AWS CLI** (optional but recommended): For easier credential management
3. **Python boto3**: Already added to requirements.txt

## 🔧 Step-by-Step Setup

### Step 1: Create an S3 Bucket

1. **Log in to AWS Console**
   - Go to https://console.aws.amazon.com/
   - Sign in with your AWS account

2. **Navigate to S3**
   - Search for "S3" in the AWS services search bar
   - Click on "S3" service

3. **Create a New Bucket**
   - Click "Create bucket"
   - **Bucket name**: Choose a unique name (e.g., `autovault-files-2024`)
     - Must be globally unique across all AWS accounts
     - Use lowercase letters, numbers, and hyphens only
   - **AWS Region**: Choose a region close to you (e.g., `us-east-1`)
   - **Block Public Access**: Keep default settings (all blocked) ✅
   - Click "Create bucket"

### Step 2: Create IAM User and Access Keys

For security, create a dedicated IAM user with S3 permissions:

1. **Navigate to IAM**
   - Search for "IAM" in AWS services
   - Click on "IAM" service

2. **Create New User**
   - Click "Users" in the left sidebar
   - Click "Create user"
   - **User name**: `autovault-s3-user`
   - Click "Next"

3. **Set Permissions**
   - Select "Attach policies directly"
   - Search for and select: **`AmazonS3FullAccess`**
   - Click "Next" → "Create user"

4. **Create Access Keys**
   - Click on the newly created user
   - Go to "Security credentials" tab
   - Scroll to "Access keys" section
   - Click "Create access key"
   - Select "Application running outside AWS"
   - Click "Next"
   - Add description: "AutoVault S3 Access"
   - Click "Create access key"
   - **IMPORTANT**: Copy both:
     - **Access key ID** (starts with `AKIA...`)
     - **Secret access key** (click "Show" to reveal)
   - Save these securely - you won't see the secret key again!

### Step 3: Configure AutoVault

You have **two options** to configure S3 credentials:

#### Option A: Environment Variables (Recommended for Production)

Set these environment variables before running the app:

```bash
export AWS_ACCESS_KEY_ID="your-access-key-id"
export AWS_SECRET_ACCESS_KEY="your-secret-access-key"
export AWS_REGION="us-east-1"
export S3_BUCKET_NAME="your-bucket-name"
export USE_S3="true"
```

Then run your app:
```bash
python3 app.py
```

#### Option B: Edit config.py (Quick Testing)

Edit `config.py` and update these values:

```python
# AWS S3 Settings
USE_S3 = True
AWS_ACCESS_KEY_ID = 'your-access-key-id-here'
AWS_SECRET_ACCESS_KEY = 'your-secret-access-key-here'
AWS_REGION = 'us-east-1'  # Your bucket region
S3_BUCKET_NAME = 'your-bucket-name-here'
S3_BUCKET_PREFIX = 'autovault'  # Optional: folder prefix
```

**⚠️ Security Warning**: Don't commit credentials to git! Use environment variables for production.

### Step 4: Install Dependencies

Install the new boto3 package:

```bash
pip3 install -r requirements.txt
```

Or install boto3 directly:
```bash
pip3 install boto3
```

### Step 5: Test the Setup

1. **Start your app**:
   ```bash
   python3 app.py
   ```

2. **Check console output**:
   You should see:
   ```
   [S3] S3 client initialized successfully
   ```

3. **Test file upload**:
   - Log in to your app
   - Upload a test file
   - Check the console for: `[S3] File uploaded: autovault/user_X/filename.txt`

4. **Verify in S3**:
   - Go to AWS Console → S3 → Your bucket
   - You should see files in `autovault/user_X/` folders

## 🔍 Verification Checklist

- [ ] S3 bucket created successfully
- [ ] IAM user created with S3 permissions
- [ ] Access keys generated and saved
- [ ] Environment variables set (or config.py updated)
- [ ] boto3 installed (`pip3 install boto3`)
- [ ] App starts without S3 errors
- [ ] Test file upload works
- [ ] Test file download works
- [ ] Test file deletion works
- [ ] Files visible in S3 bucket

## 🐛 Troubleshooting

### Error: "NoCredentialsError"

**Problem**: AWS credentials not found

**Solution**:
- Verify environment variables are set: `echo $AWS_ACCESS_KEY_ID`
- Or check config.py has credentials
- Make sure you're using the correct access key ID and secret key

### Error: "AccessDenied" or "403 Forbidden"

**Problem**: IAM user doesn't have proper permissions

**Solution**:
- Go to IAM → Users → Your user → Permissions
- Ensure `AmazonS3FullAccess` policy is attached
- Wait a few minutes for permissions to propagate

### Error: "NoSuchBucket"

**Problem**: Bucket name is incorrect

**Solution**:
- Verify bucket name in config matches exactly (case-sensitive)
- Check bucket exists in the correct AWS region
- Ensure bucket name doesn't have typos

### Error: "InvalidAccessKeyId"

**Problem**: Access key ID is incorrect

**Solution**:
- Verify access key ID starts with `AKIA...`
- Check for typos or extra spaces
- Generate new access keys if needed

### Files Not Uploading

**Check**:
1. Console output for error messages
2. S3 bucket permissions
3. IAM user permissions
4. Network connectivity

### S3 Client Not Initializing

**Check**:
1. `USE_S3` is set to `True` in config
2. `S3_BUCKET_NAME` is set
3. Credentials are correct
4. boto3 is installed: `pip3 show boto3`

## 📊 S3 Bucket Structure

Your files will be stored like this in S3:

```
your-bucket-name/
└── autovault/
    ├── user_1/
    │   ├── file1.pdf
    │   └── file2.jpg
    ├── user_2/
    │   └── document.docx
    └── user_3/
        └── image.png
```

## 💰 Cost Considerations

**AWS S3 Free Tier** (First 12 months):
- 5 GB storage
- 20,000 GET requests
- 2,000 PUT requests

**After Free Tier**:
- Storage: ~$0.023 per GB/month
- Requests: Very cheap (pennies per 1000 requests)

For a small application, costs are typically **under $1/month**.

## 🔒 Security Best Practices

1. **Never commit credentials to git**
   - Use environment variables
   - Add `config.py` to `.gitignore` if storing credentials there

2. **Use IAM roles in production**
   - For EC2/ECS deployments, use IAM roles instead of access keys

3. **Limit IAM permissions**
   - Instead of `AmazonS3FullAccess`, create a custom policy that only allows:
     - `s3:PutObject` (upload)
     - `s3:GetObject` (download)
     - `s3:DeleteObject` (delete)
     - On your specific bucket only

4. **Enable bucket versioning** (optional)
   - Helps recover accidentally deleted files

5. **Set up lifecycle policies** (optional)
   - Automatically delete old files
   - Move to cheaper storage classes

## 🔄 Switching Back to Local Storage

If you want to temporarily use local storage:

1. Set environment variable:
   ```bash
   export USE_S3="false"
   ```

2. Or edit `config.py`:
   ```python
   USE_S3 = False
   ```

The app will automatically fall back to local storage in the `uploads/` directory.

## ✅ Success Indicators

Your S3 integration is working correctly if:

- ✅ Console shows: `[S3] S3 client initialized successfully`
- ✅ Files upload successfully
- ✅ Files download successfully
- ✅ Files delete successfully
- ✅ Files appear in S3 bucket
- ✅ Scheduler deletes expired files from S3
- ✅ No errors in console

## 📞 Need Help?

If you encounter issues:

1. Check the console output for error messages
2. Verify all configuration values
3. Test AWS credentials using AWS CLI:
   ```bash
   aws s3 ls s3://your-bucket-name
   ```
4. Review AWS CloudWatch logs (if enabled)

## 🎉 Next Steps

Once S3 is working:

1. **Test file upload/download**
2. **Test file deletion**
3. **Test scheduler with expired files**
4. **Monitor S3 bucket usage**
5. **Set up S3 lifecycle policies** (optional)
6. **Configure S3 bucket logging** (optional)

---

**Congratulations!** Your AutoVault now uses Amazon S3 for cloud storage! 🚀

