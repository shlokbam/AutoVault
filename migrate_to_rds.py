"""
Migration script to move data from SQLite to RDS PostgreSQL
Usage: python3 migrate_to_rds.py
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, File
from config import (
    DATABASE_PATH,
    USE_RDS,
    DATABASE_URL,
    RDS_HOST,
    RDS_PORT,
    RDS_DB_NAME,
    RDS_USERNAME,
    RDS_PASSWORD
)
from urllib.parse import quote_plus
from app import app

def get_rds_connection_string():
    """Build RDS connection string"""
    if DATABASE_URL:
        return DATABASE_URL
    
    if RDS_HOST and RDS_USERNAME and RDS_PASSWORD:
        encoded_password = quote_plus(RDS_PASSWORD)
        return (
            f'postgresql://{RDS_USERNAME}:{encoded_password}@'
            f'{RDS_HOST}:{RDS_PORT}/{RDS_DB_NAME}'
        )
    
    return None

def migrate_data():
    """Migrate data from SQLite to RDS"""
    print("=" * 60)
    print("AutoVault SQLite to RDS Migration")
    print("=" * 60)
    
    # Check RDS configuration
    if not USE_RDS:
        print("❌ Error: USE_RDS is not enabled in config.py")
        print("   Set USE_RDS = True before running migration")
        return False
    
    rds_conn_string = get_rds_connection_string()
    if not rds_conn_string:
        print("❌ Error: RDS connection details not configured")
        print("   Please set RDS_HOST, RDS_USERNAME, RDS_PASSWORD in config.py")
        return False
    
    # SQLite connection
    sqlite_conn_string = f'sqlite:///{DATABASE_PATH}'
    print(f"\n📦 Source: SQLite ({DATABASE_PATH})")
    print(f"☁️  Destination: RDS ({RDS_HOST}:{RDS_PORT}/{RDS_DB_NAME})")
    
    try:
        # Create connections
        sqlite_engine = create_engine(sqlite_conn_string)
        rds_engine = create_engine(rds_conn_string)
        
        sqlite_session = sessionmaker(bind=sqlite_engine)()
        rds_session = sessionmaker(bind=rds_engine)()
        
        # Test connections
        print("\n🔌 Testing connections...")
        sqlite_session.execute("SELECT 1")
        print("   ✅ SQLite connection OK")
        
        rds_session.execute("SELECT 1")
        print("   ✅ RDS connection OK")
        
        # Create tables in RDS
        print("\n📋 Creating tables in RDS...")
        with app.app_context():
            from models import db
            db.create_all()
        print("   ✅ Tables created")
        
        # Migrate users
        print("\n👥 Migrating users...")
        sqlite_users = sqlite_session.query(User).all()
        users_migrated = 0
        users_skipped = 0
        
        for user in sqlite_users:
            # Check if user already exists
            existing = rds_session.query(User).filter_by(email=user.email).first()
            if existing:
                users_skipped += 1
                print(f"   ⏭️  Skipped (exists): {user.email}")
            else:
                new_user = User(
                    email=user.email,
                    password_hash=user.password_hash,
                    created_at=user.created_at
                )
                rds_session.add(new_user)
                users_migrated += 1
                print(f"   ✅ Migrating: {user.email}")
        
        rds_session.commit()
        print(f"\n   📊 Users: {users_migrated} migrated, {users_skipped} skipped")
        
        # Migrate files
        print("\n📁 Migrating files...")
        sqlite_files = sqlite_session.query(File).all()
        files_migrated = 0
        files_skipped = 0
        
        for file in sqlite_files:
            # Get user in RDS
            rds_user = rds_session.query(User).filter_by(
                email=file.user.email
            ).first()
            
            if not rds_user:
                files_skipped += 1
                print(f"   ⚠️  Skipped (user not found): {file.filename}")
                continue
            
            # Check if file already exists
            existing = rds_session.query(File).filter_by(
                user_id=rds_user.id,
                filename=file.filename,
                filepath=file.filepath
            ).first()
            
            if existing:
                files_skipped += 1
                print(f"   ⏭️  Skipped (exists): {file.filename}")
            else:
                new_file = File(
                    user_id=rds_user.id,
                    filename=file.filename,
                    filepath=file.filepath,
                    file_size=file.file_size,
                    upload_time=file.upload_time,
                    expiry_time=file.expiry_time,
                    email_sent=file.email_sent
                )
                rds_session.add(new_file)
                files_migrated += 1
                print(f"   ✅ Migrating: {file.filename}")
        
        rds_session.commit()
        print(f"\n   📊 Files: {files_migrated} migrated, {files_skipped} skipped")
        
        # Verify migration
        print("\n🔍 Verifying migration...")
        rds_user_count = rds_session.query(User).count()
        rds_file_count = rds_session.query(File).count()
        sqlite_user_count = sqlite_session.query(User).count()
        sqlite_file_count = sqlite_session.query(File).count()
        
        print(f"   SQLite: {sqlite_user_count} users, {sqlite_file_count} files")
        print(f"   RDS:    {rds_user_count} users, {rds_file_count} files")
        
        if rds_user_count >= sqlite_user_count and rds_file_count >= sqlite_file_count:
            print("\n✅ Migration completed successfully!")
            print("\n📝 Next steps:")
            print("   1. Test the application with RDS")
            print("   2. Verify all data is accessible")
            print("   3. Keep SQLite backup as safety measure")
            print("   4. Once verified, you can archive SQLite database")
            return True
        else:
            print("\n⚠️  Warning: Some data may not have migrated")
            print("   Please review the migration log above")
            return False
        
    except Exception as e:
        print(f"\n❌ Migration failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Close sessions
        try:
            sqlite_session.close()
            rds_session.close()
        except:
            pass

if __name__ == '__main__':
    with app.app_context():
        success = migrate_data()
        exit(0 if success else 1)

