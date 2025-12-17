# 🗄️ Amazon RDS Setup Guide for AutoVault

This guide will walk you through setting up Amazon RDS (PostgreSQL) for your AutoVault database.

## 📋 Prerequisites

1. **AWS Account**: You need an AWS account
2. **AWS Credentials**: Same credentials used for S3 (or IAM user with RDS permissions)
3. **Python psycopg2**: Already added to requirements.txt

## 🔧 Step-by-Step Setup

### Step 1: Create RDS PostgreSQL Instance

1. **Log in to AWS Console**
   - Go to https://console.aws.amazon.com/
   - Sign in with your AWS account

2. **Navigate to RDS**
   - Search for "RDS" in the AWS services search bar
   - Click on "RDS" service

3. **Create Database**
   - Click "Create database"
   - **Database creation method**: Choose "Standard create"
   - **Engine options**: Select **PostgreSQL**
   - **Version**: Choose latest stable version (e.g., PostgreSQL 15.4)
   - **Templates**: 
     - For testing: **Free tier** (if eligible)
     - For production: **Production** or **Dev/Test**

4. **Settings**
   - **DB instance identifier**: `autovault-db`
   - **Master username**: `autovault_admin` (or your choice)
   - **Master password**: Create a strong password (save it!)
   - **Confirm password**: Re-enter password

5. **Instance configuration**
   - **DB instance class**: 
     - Free tier: `db.t3.micro` or `db.t4g.micro`
     - Production: `db.t3.small` or larger
   - **Storage**: 
     - **Storage type**: General Purpose SSD (gp3)
     - **Allocated storage**: 20 GB (minimum, can increase later)
     - **Storage autoscaling**: Enable (optional, recommended)

6. **Connectivity**
   - **VPC**: Default VPC (or your custom VPC)
   - **Subnet group**: Default (or create custom)
   - **Public access**: 
     - **For local development**: Yes ✅
     - **For production**: No (use VPC/security groups)
   - **VPC security group**: Create new or choose existing
     - **Security group name**: `autovault-rds-sg`
   - **Availability Zone**: No preference (or choose specific)
   - **Database port**: `5432` (PostgreSQL default)

7. **Database authentication**
   - **Database authentication**: Password authentication

8. **Additional configuration** (optional)
   - **Initial database name**: `autovault` (optional, can create later)
   - **DB parameter group**: Default
   - **Backup**: Enable automated backups (recommended)
   - **Backup retention period**: 7 days (free tier: 1 day)
   - **Encryption**: Enable (recommended for production)

9. **Monitoring**
   - **Enable Enhanced monitoring**: Optional (costs extra)

10. **Click "Create database"**
    - Wait 5-10 minutes for database to be created
    - Status will change from "Creating" to "Available"

### Step 2: Configure Security Group

Your RDS instance needs to allow connections from your application:

1. **Go to RDS Console**
   - Click on your database instance
   - Go to "Connectivity & security" tab
   - Note the **Endpoint** (e.g., `autovault-db.xxxxx.ap-south-1.rds.amazonaws.com`)
   - Click on the **VPC security group** link

2. **Edit Inbound Rules**
   - Click "Edit inbound rules"
   - Click "Add rule"
   - **Type**: PostgreSQL
   - **Port**: 5432
   - **Source**: 
     - For local testing: `My IP` (your current IP)
     - For EC2 deployment: Security group of your EC2 instance
     - For production: Specific IP ranges only
   - Click "Save rules"

### Step 3: Get Connection Details

From RDS Console, note down:

- **Endpoint**: `autovault-db.xxxxx.ap-south-1.rds.amazonaws.com`
- **Port**: `5432`
- **Database name**: `autovault` (or `postgres` if you didn't create one)
- **Username**: `autovault_admin` (or what you set)
- **Password**: (the one you created)

### Step 4: Create Database (if not created)

If you didn't create the database during setup:

1. **Connect to RDS** using a PostgreSQL client:
   ```bash
   psql -h autovault-db.xxxxx.ap-south-1.rds.amazonaws.com \
        -U autovault_admin \
        -d postgres
   ```

2. **Create database**:
   ```sql
   CREATE DATABASE autovault;
   \q
   ```

Or use AWS RDS Query Editor (in AWS Console) if available.

### Step 5: Configure AutoVault

You have **two options** to configure RDS:

#### Option A: Environment Variables (Recommended)

Set these environment variables:

```bash
export USE_RDS="true"
export RDS_HOST="autovault-db.xxxxx.ap-south-1.rds.amazonaws.com"
export RDS_PORT="5432"
export RDS_DB_NAME="autovault"
export RDS_USERNAME="autovault_admin"
export RDS_PASSWORD="your-password-here"
```

Or use a single DATABASE_URL:

```bash
export USE_RDS="true"
export DATABASE_URL="postgresql://autovault_admin:your-password@autovault-db.xxxxx.ap-south-1.rds.amazonaws.com:5432/autovault"
```

#### Option B: Edit config.py

Edit `config.py`:

```python
USE_RDS = True
RDS_HOST = 'autovault-db.xxxxx.ap-south-1.rds.amazonaws.com'
RDS_PORT = '5432'
RDS_DB_NAME = 'autovault'
RDS_USERNAME = 'autovault_admin'
RDS_PASSWORD = 'your-password-here'
```

**⚠️ Security Warning**: Don't commit credentials to git! Use environment variables for production.

### Step 6: Install Dependencies

Install PostgreSQL driver:

```bash
pip3 install -r requirements.txt
```

Or install directly:
```bash
pip3 install psycopg2-binary
```

### Step 7: Test Connection

1. **Start your app**:
   ```bash
   python3 app.py
   ```

2. **Check console output**:
   You should see:
   ```
   [Database] Using RDS: autovault-db.xxxxx.ap-south-1.rds.amazonaws.com:5432/autovault
   [App] Database initialized (RDS (PostgreSQL))
   ```

3. **Test the application**:
   - Sign up for a new account
   - Upload a file
   - Check if data persists

### Step 8: Migrate Existing Data (Optional)

If you have existing SQLite data to migrate:

See `RDS_MIGRATION_GUIDE.md` for detailed migration instructions.

## 🔍 Verification Checklist

- [ ] RDS PostgreSQL instance created
- [ ] Security group configured (port 5432 open)
- [ ] Database created (if not done during setup)
- [ ] Connection details saved
- [ ] Environment variables set (or config.py updated)
- [ ] psycopg2-binary installed
- [ ] App starts without database errors
- [ ] Can create user account
- [ ] Can upload files
- [ ] Data persists after app restart

## 🐛 Troubleshooting

### Error: "could not connect to server"

**Problem**: Cannot reach RDS instance

**Solutions**:
1. **Check security group**: Ensure port 5432 is open to your IP
2. **Check public access**: RDS instance must have "Publicly accessible" = Yes
3. **Check endpoint**: Verify endpoint is correct
4. **Check network**: Ensure you're not behind a restrictive firewall

### Error: "password authentication failed"

**Problem**: Wrong username or password

**Solutions**:
1. Verify username and password in config
2. Check for special characters in password (may need URL encoding)
3. Reset RDS master password if needed (RDS Console → Modify → Change master password)

### Error: "database does not exist"

**Problem**: Database name incorrect

**Solutions**:
1. Check database name in config matches RDS
2. Connect to `postgres` database and list databases:
   ```sql
   \l
   ```
3. Create database if missing:
   ```sql
   CREATE DATABASE autovault;
   ```

### Error: "connection timeout"

**Problem**: Network/firewall blocking connection

**Solutions**:
1. Check security group allows your IP
2. Verify RDS is in "Available" state
3. Check if you're behind corporate firewall/VPN
4. Try from different network

### Error: "psycopg2 not found"

**Problem**: PostgreSQL driver not installed

**Solution**:
```bash
pip3 install psycopg2-binary
```

### Connection Pool Errors

**Problem**: Too many connections or connection issues

**Solutions**:
1. Check RDS instance size (may need larger instance)
2. Verify connection pool settings in app.py
3. Check RDS monitoring for connection count

## 📊 RDS Instance Sizing

### Free Tier (First 12 months)
- **Instance**: db.t3.micro or db.t4g.micro
- **Storage**: 20 GB
- **Suitable for**: Development, testing, small apps

### Production Recommendations
- **Small app** (< 100 users): db.t3.small
- **Medium app** (100-1000 users): db.t3.medium
- **Large app** (> 1000 users): db.t3.large or db.r5.large

### Cost Estimates
- **Free tier**: $0/month (first 12 months)
- **db.t3.small**: ~$15-20/month
- **db.t3.medium**: ~$30-40/month
- Storage: ~$0.115/GB/month

## 🔒 Security Best Practices

1. **Never commit credentials to git**
   - Use environment variables
   - Use AWS Secrets Manager for production

2. **Use VPC and Security Groups**
   - Don't expose RDS publicly in production
   - Use private subnets
   - Restrict access to specific IPs/security groups

3. **Enable encryption**
   - Enable encryption at rest
   - Use SSL/TLS for connections (optional but recommended)

4. **Regular backups**
   - Enable automated backups
   - Test restore procedures

5. **Strong passwords**
   - Use complex passwords
   - Rotate passwords regularly

6. **IAM Database Authentication** (Advanced)
   - Use IAM roles instead of passwords
   - More secure but requires additional setup

## 🔄 Switching Back to SQLite

If you want to temporarily use SQLite:

1. Set environment variable:
   ```bash
   export USE_RDS="false"
   ```

2. Or edit `config.py`:
   ```python
   USE_RDS = False
   ```

The app will automatically fall back to SQLite.

## 📈 Monitoring

### CloudWatch Metrics
- **CPU Utilization**: Should be < 80%
- **Database Connections**: Monitor active connections
- **Freeable Memory**: Ensure sufficient memory
- **Read/Write IOPS**: Monitor disk performance

### Enable Enhanced Monitoring
- Provides more detailed metrics
- Costs extra but useful for production

## ✅ Success Indicators

Your RDS integration is working correctly if:

- ✅ Console shows: `[Database] Using RDS: ...`
- ✅ Console shows: `[App] Database initialized (RDS (PostgreSQL))`
- ✅ App starts without errors
- ✅ Can create user accounts
- ✅ Can upload/download files
- ✅ Data persists after restart
- ✅ No connection errors in console

## 🎉 Next Steps

Once RDS is working:

1. **Migrate existing data** (if any)
2. **Set up automated backups**
3. **Configure monitoring alerts**
4. **Set up read replicas** (for high availability)
5. **Enable encryption** (if not already)
6. **Set up connection pooling** (for high traffic)

## 📞 Need Help?

If you encounter issues:

1. Check AWS RDS Console for instance status
2. Review CloudWatch logs
3. Check security group rules
4. Verify connection details
5. Test connection with psql:
   ```bash
   psql -h your-endpoint.rds.amazonaws.com -U username -d database_name
   ```

---

**Congratulations!** Your AutoVault now uses Amazon RDS for cloud database! 🚀

