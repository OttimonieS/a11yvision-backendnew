"""
Database initialization script for VisionAI

Run this script to create all database tables and optionally seed with test data.

Usage:
    python init_db.py
"""

import os
import sys

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.dirname(__file__))

from database import init_db, engine, SessionLocal
from models import Base
import models


def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")


def seed_test_data():
    """Optionally seed database with test data"""
    import uuid
    import hashlib
    from datetime import datetime, timedelta

    db = SessionLocal()

    try:
        # Check if test user already exists
        test_user = db.query(models.User).filter(models.User.email == "test@example.com").first()
        if test_user:
            print("✓ Test data already exists")
            return

        print("Seeding test data...")

        # Create test user
        user_id = str(uuid.uuid4())
        password_hash = hashlib.sha256("password123".encode()).hexdigest()

        user = models.User(
            id=user_id,
            email="test@example.com",
            name="Test User",
            password_hash=password_hash,
            created_at=datetime.utcnow()
        )
        db.add(user)

        # Create user settings
        settings = models.UserSettings(
            user_id=user_id,
            contrast_threshold="WCAG_AA",
            enable_target_size=True,
            rescan_cadence="manual"
        )
        db.add(settings)

        # Create a test scan
        scan_id = str(uuid.uuid4())
        scan = models.Scan(
            scan_id=scan_id,
            user_id=user_id,
            url="https://example.com",
            status="done",
            created_at=datetime.utcnow(),
            completed_at=datetime.utcnow(),
            screenshot_path="test_screenshot.png",
            issues_count=3,
            coverage_score=72.0,
            accessibility_score=68.0
        )
        db.add(scan)

        # Create test issues
        issues = [
            models.Issue(
                id=str(uuid.uuid4()),
                scan_id=scan_id,
                rule="color-contrast",
                wcag="WCAG 2.1 AA 1.4.3",
                severity="critical",
                confidence=0.95,
                message="Text has insufficient color contrast",
                bbox=[100, 200, 300, 50]
            ),
            models.Issue(
                id=str(uuid.uuid4()),
                scan_id=scan_id,
                rule="target-size",
                wcag="WCAG 2.1 AA 2.5.5",
                severity="serious",
                confidence=0.87,
                message="Interactive element is too small",
                bbox=[50, 100, 30, 30]
            ),
            models.Issue(
                id=str(uuid.uuid4()),
                scan_id=scan_id,
                rule="image-alt",
                wcag="WCAG 2.1 A 1.1.1",
                severity="minor",
                confidence=0.92,
                message="Image missing alternative text",
                bbox=[200, 300, 400, 250]
            )
        ]
        for issue in issues:
            db.add(issue)

        # Create activity logs
        activities = [
            models.ActivityLog(
                user_id=user_id,
                action="signup",
                details={"method": "email"},
                created_at=datetime.utcnow() - timedelta(days=7)
            ),
            models.ActivityLog(
                user_id=user_id,
                action="login",
                created_at=datetime.utcnow() - timedelta(days=7)
            ),
            models.ActivityLog(
                user_id=user_id,
                action="scan_created",
                resource_type="scan",
                resource_id=scan_id,
                details={"url": "https://example.com"},
                created_at=datetime.utcnow() - timedelta(hours=2)
            ),
            models.ActivityLog(
                user_id=user_id,
                action="scan_completed",
                resource_type="scan",
                resource_id=scan_id,
                details={"issues_count": 3, "status": "done"},
                created_at=datetime.utcnow() - timedelta(hours=1)
            )
        ]
        for activity in activities:
            db.add(activity)

        db.commit()
        print("✓ Test data seeded successfully")
        print(f"  Test user: test@example.com / password123")

    except Exception as e:
        print(f"✗ Error seeding test data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def main():
    print("=" * 60)
    print("VisionAI Database Initialization")
    print("=" * 60)

    # Create tables
    create_tables()

    # Ask if user wants to seed test data
    response = input("\nDo you want to seed test data? (y/n): ").lower()
    if response == 'y':
        seed_test_data()

    print("\n" + "=" * 60)
    print("Database initialization complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Update DATABASE_URL in .env file if needed")
    print("2. Run 'uvicorn main:app --reload' to start the server")
    print("\nIf you seeded test data:")
    print("- Email: test@example.com")
    print("- Password: password123")


if __name__ == "__main__":
    main()
