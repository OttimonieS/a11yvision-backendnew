"""
Database connection test script
Tests different connection methods to Supabase
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 60)
print("Testing Supabase Database Connection")
print("=" * 60)

# Test 1: Check environment variable
DATABASE_URL = os.getenv("DATABASE_URL")
print(f"\n1. DATABASE_URL loaded: {DATABASE_URL[:50]}..." if DATABASE_URL else "✗ DATABASE_URL not found!")

# Test 2: Test DNS resolution
print("\n2. Testing DNS resolution...")
import socket
try:
    host = "db.xwngeybzalnemzlaedqu.supabase.co"
    ip = socket.gethostbyname(host)
    print(f"   ✓ DNS resolved: {host} -> {ip}")
except socket.gaierror as e:
    print(f"   ✗ DNS resolution failed: {e}")
    print("\n   Possible solutions:")
    print("   - Check your internet connection")
    print("   - Try using Google DNS (8.8.8.8)")
    print("   - Check if your firewall/antivirus is blocking connections")
    print("   - Try flushing DNS: ipconfig /flushdns")
    exit(1)

# Test 3: Try direct connection with psycopg2
print("\n3. Testing psycopg2 connection...")
try:
    import psycopg2
    from urllib.parse import urlparse

    # Parse the DATABASE_URL
    result = urlparse(DATABASE_URL)
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port

    print(f"   Host: {hostname}")
    print(f"   Port: {port}")
    print(f"   Database: {database}")
    print(f"   User: {username}")

    # Try to connect
    conn = psycopg2.connect(
        host=hostname,
        port=port,
        database=database,
        user=username,
        password=password
    )
    print("   ✓ psycopg2 connection successful!")

    # Test query
    cursor = conn.cursor()
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"   ✓ PostgreSQL version: {version[:50]}...")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"   ✗ psycopg2 connection failed: {e}")
    exit(1)

# Test 4: Try SQLAlchemy connection
print("\n4. Testing SQLAlchemy connection...")
try:
    from sqlalchemy import create_engine, text

    engine = create_engine(DATABASE_URL)

    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("   ✓ SQLAlchemy connection successful!")

except Exception as e:
    print(f"   ✗ SQLAlchemy connection failed: {e}")
    exit(1)

print("\n" + "=" * 60)
print("✓ All tests passed! Database connection is working.")
print("=" * 60)
print("\nYou can now run: python init_db.py")
