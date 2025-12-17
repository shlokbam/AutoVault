# ⚡ AWS Lambda Setup Guide for AutoVault

This guide shows you how to set up AWS Lambda to automatically check for expired files and send notifications, replacing the local scheduler.

## 📋 Overview

Instead of running the scheduler in your Flask app, AWS Lambda will:
- Run on a schedule (every hour via EventBridge)
- Check for expired files in RDS
- Send email notifications before expiry
- Delete expired files from S3
- Update database records

## 🔧 Step-by-Step Setup

### Step 1: Prepare Lambda Deployment Package

1. **Create a directory for Lambda package**:
   ```bash
   mkdir lambda_package
   cd lambda_package
   ```

2. **Copy Lambda function**:
   ```bash
   cp ../lambda_function.py .
   ```

3. **Install dependencies**:
   ```bash
   pip3 install -r ../lambda_requirements.txt -t .
   ```

4. **Create deployment package**:
   ```bash
   zip -r lambda_function.zip .
   ```

### Step 2: Create Lambda Function in AWS Console

1. **Go to AWS Lambda Console**
   - Navigate to: https://console.aws.amazon.com/lambda/
   - Click "Create function"

2. **Function Configuration**
   - **Function name**: `autovault-expiry-processor`
   - **Runtime**: Python 3.11 or 3.12
   - **Architecture**: x86_64
   - Click "Create function"

3. **Upload Code**
   - Scroll to "Code source"
   - Click "Upload from" → ".zip file"
   - Upload `lambda_function.zip`
   - Click "Save"

### Step 3: Configure Environment Variables

1. **Go to Configuration → Environment variables**
2. **Add these variables**:

   ```
   RDS_ENDPOINT = autovault-db.c522qq6g4niv.ap-south-1.rds.amazonaws.com
   RDS_PORT = 5432
   RDS_DB_NAME = autovault
   RDS_USERNAME = autovault_admin
   RDS_PASSWORD = your-rds-password
   S3_BUCKET_NAME = autovault-files
   S3_BUCKET_PREFIX = autovault
   NOTIFICATION_HOURS_BEFORE_EXPIRY = 24
   EMAIL_FROM = shlokbam19103@gmail.com
   ```

   **⚠️ Important**: For production, use AWS Secrets Manager instead of plain text passwords!

### Step 4: Configure Lambda Permissions

1. **Go to Configuration → Permissions**
2. **Click on Execution role**
3. **Add these policies**:
   - `AmazonRDSFullAccess` (or custom policy for RDS access)
   - `AmazonS3FullAccess` (or custom policy for your bucket only)
   - `AmazonSESFullAccess` (for email notifications)

### Step 5: Configure VPC (if RDS is in VPC)

If your RDS is in a VPC (not publicly accessible):

1. **Go to Configuration → VPC**
2. **Configure**:
   - VPC: Select your RDS VPC
   - Subnets: Select private subnets
   - Security groups: Create/select security group that allows Lambda to connect to RDS

### Step 6: Set Timeout and Memory

1. **Go to Configuration → General configuration**
2. **Edit**:
   - **Timeout**: 5 minutes (300 seconds)
   - **Memory**: 256 MB (or 512 MB for better performance)

### Step 7: Create EventBridge Rule (Scheduler)

1. **Go to EventBridge Console**
   - Navigate to: https://console.aws.amazon.com/events/
   - Click "Rules" → "Create rule"

2. **Rule Configuration**:
   - **Name**: `autovault-expiry-check`
   - **Description**: "Trigger Lambda to check expired files"
   - **Event bus**: default
   - **Rule type**: Schedule

3. **Schedule Pattern**:
   - **Schedule type**: Recurring schedule
   - **Schedule pattern**: Rate expression
   - **Rate expression**: `rate(1 hour)` (or `cron(0 * * * ? *)` for every hour)

4. **Target**:
   - **Target type**: AWS service
   - **Select a target**: Lambda function
   - **Function**: `autovault-expiry-processor`
   - Click "Create"

### Step 8: Test Lambda Function

1. **Go to Lambda Console → Your function**
2. **Click "Test"**
3. **Create test event**:
   ```json
   {
     "source": "test",
     "detail-type": "Scheduled Event"
   }
   ```
4. **Click "Test"**
5. **Check execution results**:
   - Should see logs showing files processed
   - Check CloudWatch Logs for details

### Step 9: Disable Local Scheduler (Optional)

If Lambda is working, you can disable the local scheduler:

1. **Edit `config.py`**:
   ```python
   USE_LAMBDA_SCHEDULER = True  # Use Lambda instead of local scheduler
   ```

2. **Update `app.py`** to check this flag before starting local scheduler

## 📊 Monitoring

### CloudWatch Logs

1. **Go to CloudWatch → Log groups**
2. **Find**: `/aws/lambda/autovault-expiry-processor`
3. **View logs** to see execution details

### CloudWatch Metrics

- **Invocations**: Number of times Lambda runs
- **Errors**: Failed executions
- **Duration**: Execution time
- **Throttles**: If Lambda is hitting limits

### Set Up Alarms (Optional)

1. **Go to CloudWatch → Alarms**
2. **Create alarm**:
   - Metric: Lambda Errors
   - Threshold: > 0
   - Action: Send SNS notification

## 🔒 Security Best Practices

1. **Use Secrets Manager**:
   - Store RDS password in AWS Secrets Manager
   - Lambda retrieves secrets at runtime
   - More secure than environment variables

2. **Least Privilege IAM**:
   - Create custom IAM policy with only needed permissions
   - Don't use `FullAccess` policies in production

3. **VPC Configuration**:
   - Put Lambda in same VPC as RDS
   - Use security groups to restrict access
   - Don't expose RDS publicly

4. **Encryption**:
   - Enable encryption at rest for Lambda
   - Use encrypted environment variables

## 💰 Cost Considerations

**Lambda Pricing**:
- **Free tier**: 1M requests/month, 400,000 GB-seconds/month
- **After free tier**: $0.20 per 1M requests, $0.0000166667 per GB-second

**EventBridge Pricing**:
- **Free tier**: 1M custom events/month
- **After free tier**: $1.00 per 1M events

**Estimated cost**: ~$0-1/month for hourly execution

## 🐛 Troubleshooting

### Lambda Can't Connect to RDS

**Problem**: Connection timeout or refused

**Solutions**:
1. Check Lambda is in same VPC as RDS
2. Verify security group allows Lambda → RDS
3. Check RDS endpoint is correct
4. Verify RDS is publicly accessible (if Lambda not in VPC)

### Lambda Can't Access S3

**Problem**: Access denied errors

**Solutions**:
1. Check IAM role has S3 permissions
2. Verify bucket name is correct
3. Check bucket policy allows Lambda role

### Lambda Timeout

**Problem**: Function times out

**Solutions**:
1. Increase timeout (up to 15 minutes)
2. Optimize database queries
3. Process files in batches

### Database Connection Errors

**Problem**: psycopg2 connection errors

**Solutions**:
1. Verify RDS credentials
2. Check RDS instance is running
3. Verify network connectivity
4. Check security groups

## ✅ Verification Checklist

- [ ] Lambda function created
- [ ] Code uploaded successfully
- [ ] Environment variables configured
- [ ] IAM permissions set
- [ ] VPC configured (if needed)
- [ ] EventBridge rule created
- [ ] Test execution successful
- [ ] CloudWatch logs showing activity
- [ ] Files being deleted correctly
- [ ] Email notifications working

## 🔄 Switching Back to Local Scheduler

If you want to use local scheduler instead:

1. **Disable EventBridge rule**:
   - Go to EventBridge → Rules
   - Select rule → Disable

2. **Enable local scheduler**:
   - Set `USE_LAMBDA_SCHEDULER = False` in config.py
   - Restart Flask app

## 📝 Next Steps

1. **Set up CloudWatch alarms** for errors
2. **Configure SES** for email sending (if not already done)
3. **Set up Secrets Manager** for credentials
4. **Create CloudWatch dashboard** for monitoring
5. **Set up X-Ray** for tracing (optional)

---

**Congratulations!** Your AutoVault now uses AWS Lambda for automated file expiry processing! 🚀

