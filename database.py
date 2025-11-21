import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

# Database URL from environment or default to SQLite for development
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/visionai"
)

# For SQLite fallback during development
# DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./visionai.db")

engine = create_engine(
    DATABASE_URL,
    # For PostgreSQL
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
    # For SQLite, use these instead:
    # connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    import models  # Import models to register them
    Base.metadata.create_all(bind=engine)
