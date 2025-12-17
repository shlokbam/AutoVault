# 🔄 Migrating from SQLite to RDS

This guide helps you migrate existing data from SQLite to Amazon RDS PostgreSQL.

## 📋 Prerequisites

- RDS instance created and configured (see `RDS_SETUP_GUIDE.md`)
- Existing SQLite database with data
- Python with required packages installed

## 🔧 Migration Methods

### Method 1: Using Python Script (Recommended)

I'll create a migration script for you:

```python
# migrate_to_rds.py
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys

# SQLite connection
sqlite_engine = create_engine('sqlite:///autovault.db')
sqlite_session = sessionmaker(bind=sqlite_engine)()

# RDS connection (update with your credentials)
rds_engine = create_engine(
    'postgresql://username:password@host:5432/autovault'
)
rds_session = sessionmaker(bind=rds_engine)()

# Import models
from models import User, File
from app import app

def migrate_users():
    """Migrate users from SQLite to RDS"""
    users = sqlite_session.query(User).all()
    migrated = 0
    
    for user in users:
        # Check if user already exists
        existing = rds_session.query(User).filter_by(email=user.email).first()
        if not existing:
            new_user = User(
                email=user.email,
                password_hash=user.password_hash,
                created_at=user.created_at
            )
            rds_session.add(new_user)
            migrated += 1
            print(f"Migrating user: {user.email}")
    
    rds_session.commit()
    print(f"✅ Migrated {migrated} users")
    return migrated

def migrate_files():
    """Migrate files from SQLite to RDS"""
    files = sqlite_session.query(File).all()
    migrated = 0
    
    for file in files:
        # Get user ID in RDS (by email lookup)
        user = rds_session.query(User).filter_by(
            email=file.user.email
        ).first()
        
        if user:
            new_file = File(
                user_id=user.id,
                filename=file.filename,
                filepath=file.filepath,
                file_size=file.file_size,
                upload_time=file.upload_time,
                expiry_time=file.expiry_time,
                email_sent=file.email_sent
            )
            rds_session.add(new_file)
            migrated += 1
            print(f"Migrating file: {file.filename}")
    
    rds_session.commit()
    print(f"✅ Migrated {migrated} files")
    return migrated

if __name__ == '__main__':
    with app.app_context():
        # Create tables in RDS
        from models import db
        db.create_all()
        
        print("Starting migration...")
        users_count = migrate_users()
        files_count = migrate_files()
        print(f"\n✅ Migration complete!")
        print(f"   Users: {users_count}")
        print(f"   Files: {files_count}")
```

**Usage**:
1. Update RDS connection string in script
2. Run: `python3 migrate_to_rds.py`

### Method 2: Using pgloader (Advanced)

pgloader can migrate directly from SQLite to PostgreSQL:

1. **Install pgloader**:
   ```bash
   # macOS
   brew install pgloader
   
   # Linux
   sudo apt-get install pgloader
   ```

2. **Create migration script** (`migrate.load`):
   ```
   LOAD DATABASE
       FROM sqlite:///path/to/autovault.db
       INTO postgresql://username:password@host:5432/autovault
   
   WITH include drop, create tables, create indexes, reset sequences
   
   SET work_mem to '16MB', maintenance_work_mem to '512 MB';
   ```

3. **Run migration**:
   ```bash
   pgloader migrate.load
   ```

### Method 3: Manual SQL Export/Import

1. **Export from SQLite**:
   ```bash
   sqlite3 autovault.db .dump > dump.sql
   ```

2. **Convert SQL** (SQLite to PostgreSQL):
   - Replace `INTEGER PRIMARY KEY` with `SERIAL PRIMARY KEY`
   - Remove SQLite-specific syntax
   - Adjust data types

3. **Import to PostgreSQL**:
   ```bash
   psql -h your-rds-endpoint -U username -d autovault < converted_dump.sql
   ```

## ⚠️ Important Notes

1. **Backup First**: Always backup your SQLite database before migration
   ```bash
   cp autovault.db autovault.db.backup
   ```

2. **Test Migration**: Test on a copy first, not production data

3. **Data Types**: SQLite and PostgreSQL have different data types:
   - SQLite `INTEGER` → PostgreSQL `INTEGER` or `SERIAL`
   - SQLite `TEXT` → PostgreSQL `VARCHAR` or `TEXT`
   - SQLite `BLOB` → PostgreSQL `BYTEA`

4. **Foreign Keys**: Ensure foreign key constraints are maintained

5. **Timestamps**: SQLite and PostgreSQL handle timestamps similarly, but verify

## 🔍 Verification

After migration, verify data:

1. **Count records**:
   ```sql
   SELECT COUNT(*) FROM users;
   SELECT COUNT(*) FROM files;
   ```

2. **Check sample data**:
   ```sql
   SELECT * FROM users LIMIT 5;
   SELECT * FROM files LIMIT 5;
   ```

3. **Test application**:
   - Log in with existing accounts
   - Verify files are accessible
   - Test file operations

## 🐛 Common Issues

### Issue: Foreign Key Violations

**Solution**: Migrate users before files, maintain user IDs

### Issue: Data Type Mismatches

**Solution**: Review and adjust column types in models if needed

### Issue: Timestamp Format

**Solution**: SQLAlchemy handles this automatically, but verify

## ✅ Post-Migration Checklist

- [ ] All users migrated
- [ ] All files migrated
- [ ] User authentication works
- [ ] File upload/download works
- [ ] File deletion works
- [ ] Scheduler works with RDS
- [ ] Data integrity verified
- [ ] Backup SQLite database (keep as backup)

## 🔄 Rollback Plan

If migration fails:

1. Keep SQLite database as backup
2. Set `USE_RDS = False` in config
3. App will use SQLite again
4. Fix issues and retry migration

---

**Note**: For production migrations, consider:
- Performing during maintenance window
- Using database replication
- Testing thoroughly before switching

