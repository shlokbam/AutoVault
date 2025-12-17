"""
Script to create the 'autovault' database in RDS PostgreSQL
Usage: python3 create_rds_database.py
"""
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import RDS_HOST, RDS_PORT, RDS_USERNAME, RDS_PASSWORD, RDS_DB_NAME

def create_database():
    """Create the database if it doesn't exist"""
    print("=" * 60)
    print("AutoVault RDS Database Creation")
    print("=" * 60)
    
    # Connect to default 'postgres' database to create new database
    try:
        print(f"\n🔌 Connecting to RDS...")
        print(f"   Host: {RDS_HOST}")
        print(f"   Port: {RDS_PORT}")
        print(f"   Username: {RDS_USERNAME}")
        
        # Connect to postgres database (default database that always exists)
        conn = psycopg2.connect(
            host=RDS_HOST,
            port=RDS_PORT,
            user=RDS_USERNAME,
            password=RDS_PASSWORD,
            database='postgres'  # Connect to default database
        )
        
        # Set isolation level to allow database creation
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        print("   ✅ Connected successfully")
        
        # Check if database already exists
        print(f"\n🔍 Checking if database '{RDS_DB_NAME}' exists...")
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (RDS_DB_NAME,)
        )
        exists = cursor.fetchone()
        
        if exists:
            print(f"   ⚠️  Database '{RDS_DB_NAME}' already exists!")
            print(f"   ✅ No action needed. You can proceed to run the app.")
            cursor.close()
            conn.close()
            return True
        
        # Create the database
        print(f"\n📋 Creating database '{RDS_DB_NAME}'...")
        cursor.execute(f'CREATE DATABASE "{RDS_DB_NAME}"')
        print(f"   ✅ Database '{RDS_DB_NAME}' created successfully!")
        
        # Verify creation
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (RDS_DB_NAME,)
        )
        if cursor.fetchone():
            print(f"\n✅ Verification: Database '{RDS_DB_NAME}' exists")
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Database creation completed successfully!")
        print("=" * 60)
        print("\n📝 Next steps:")
        print("   1. Run: python3 app.py")
        print("   2. The app will automatically create tables (users, files)")
        print("   3. Start using AutoVault with RDS!")
        
        return True
        
    except psycopg2.OperationalError as e:
        print(f"\n❌ Connection failed: {str(e)}")
        print("\n🔍 Troubleshooting:")
        print("   1. Check RDS instance is 'Available' in AWS Console")
        print("   2. Verify security group allows port 5432 from your IP")
        print("   3. Verify RDS_HOST, RDS_USERNAME, RDS_PASSWORD in config.py")
        print("   4. Check if RDS instance has 'Public access' enabled")
        return False
        
    except psycopg2.Error as e:
        print(f"\n❌ Database error: {str(e)}")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = create_database()
    exit(0 if success else 1)

