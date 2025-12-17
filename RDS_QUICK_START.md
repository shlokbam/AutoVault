# ⚡ RDS Quick Start Guide

## 🚀 10-Minute Setup

### 1. Create RDS Instance
- Go to AWS Console → RDS
- Click "Create database"
- **Engine**: PostgreSQL
- **Template**: Free tier (or Dev/Test)
- **DB instance identifier**: `autovault-db`
- **Master username**: `autovault_admin`
- **Master password**: (create strong password)
- **DB instance class**: `db.t3.micro` (free tier)
- **Public access**: **Yes** ✅ (for local development)
- **VPC security group**: Create new `autovault-rds-sg`
- Click "Create database"
- Wait 5-10 minutes for creation

### 2. Configure Security Group
- Go to RDS → Your database → "Connectivity & security"
- Click on VPC security group
- Edit inbound rules → Add rule:
  - **Type**: PostgreSQL
  - **Port**: 5432
  - **Source**: My IP (or 0.0.0.0/0 for testing)
- Save rules

### 3. Get Connection Details
From RDS Console, note:
- **Endpoint**: `autovault-db.xxxxx.ap-south-1.rds.amazonaws.com`
- **Port**: `5432`
- **Database name**: `autovault` (or create it)
- **Username**: `autovault_admin`
- **Password**: (the one you created)

### 4. Create Database (if needed)
Connect and create:
```bash
psql -h your-endpoint.rds.amazonaws.com -U autovault_admin -d postgres
```
Then:
```sql
CREATE DATABASE autovault;
\q
```

### 5. Configure AutoVault

**Option A: Environment Variables**
```bash
export USE_RDS="true"
export RDS_HOST="autovault-db.xxxxx.rds.amazonaws.com"
export RDS_PORT="5432"
export RDS_DB_NAME="autovault"
export RDS_USERNAME="autovault_admin"
export RDS_PASSWORD="your-password"
```

**Option B: Edit config.py**
```python
USE_RDS = True
RDS_HOST = 'autovault-db.xxxxx.rds.amazonaws.com'
RDS_PORT = '5432'
RDS_DB_NAME = 'autovault'
RDS_USERNAME = 'autovault_admin'
RDS_PASSWORD = 'your-password'
```

### 6. Install & Run
```bash
pip3 install psycopg2-binary
python3 app.py
```

### 7. Verify
- Console should show: `[Database] Using RDS: ...`
- Console should show: `[App] Database initialized (RDS (PostgreSQL))`
- Test signup/login
- Test file upload

## 🔄 Migrate Existing Data

If you have SQLite data to migrate:

```bash
python3 migrate_to_rds.py
```

## ✅ Success Checklist

- [ ] RDS instance created and available
- [ ] Security group allows port 5432
- [ ] Database created
- [ ] Credentials configured
- [ ] psycopg2-binary installed
- [ ] App starts without errors
- [ ] Can create accounts
- [ ] Data persists

## 🔄 Switch Back to SQLite

```bash
export USE_RDS="false"
# Or edit config.py: USE_RDS = False
```

## 📖 Full Guide

See `RDS_SETUP_GUIDE.md` for detailed instructions and troubleshooting.

