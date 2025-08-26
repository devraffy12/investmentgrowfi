#!/usr/bin/env python
import os
import sys
import django
import sqlite3

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'investmentdb.settings')

# Setup Django
django.setup()

# Check database file
db_path = 'db.sqlite3'
print(f"Database file exists: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    # Connect to database and check tables
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print(f"Tables in database: {[table[0] for table in tables]}")
    
    # Check if django_session table exists
    if 'django_session' in [table[0] for table in tables]:
        print("django_session table exists")
    else:
        print("django_session table MISSING")
    
    conn.close()

# Try to run migrations
print("\nRunning migrations...")
from django.core.management import execute_from_command_line
try:
    execute_from_command_line(['manage.py', 'migrate', '--verbosity=2'])
    print("Migrations completed successfully")
except Exception as e:
    print(f"Migration error: {e}")

# Check tables again after migration
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tables after migration: {[table[0] for table in tables]}")
    conn.close()
