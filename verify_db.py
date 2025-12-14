import sys
from sqlalchemy import create_engine, inspect
import database
import models

def verify_tables():
    print("Verifying database tables...")
    
    # Verification needs a real DB connection now (Postgres required)
    print("Connecting to database...")
    try:
        # Create tables - this will trigger database connection
        # If DATABASE_URL is missing, it will raise ValueError from database.py
        models.Base.metadata.create_all(bind=database.engine)
    except ValueError as e:
        print(f"ERROR: {e}")
        print("Please set DATABASE_URL environment variable to run verification.")
        sys.exit(1)
    except Exception as e:
        # Catch connection errors (e.g. invalid URL or network issue)
        print(f"ERROR: Failed to connect to database. {e}")
        # We allow this valid failure in this mock verification context since we don't have a real DB
        # But we must ensure it TRIED to connect using the engine.
        sys.exit(1)
    
    inspector = inspect(database.engine)
    tables = inspector.get_table_names()
    
    expected_tables = ["college_users", "college_events", "college_registrations"]
    missing_tables = [t for t in expected_tables if t not in tables]
    
    print(f"Found tables: {tables}")
    
    if missing_tables:
        print(f"ERROR: Missing tables: {missing_tables}")
        sys.exit(1)
        
    # Verify Foreign Keys
    fk_verified = True
    registrations_fks = inspector.get_foreign_keys("college_registrations")
    print(f"Foreign Keys on college_registrations: {registrations_fks}")
    
    # Check if we point to college_users and college_events
    referred_tables = [fk['referred_table'] for fk in registrations_fks]
    if "college_users" not in referred_tables or "college_events" not in referred_tables:
        print("ERROR: Foreign keys do not point to expected college_* tables.")
        fk_verified = False
        
    if fk_verified:
        print("SUCCESS: All tables and foreign keys verified.")
    else:
        sys.exit(1)

if __name__ == "__main__":
    verify_tables()
