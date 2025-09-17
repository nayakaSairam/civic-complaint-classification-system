from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import enum
import os

DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./complaints.db"

# Create a connection engine, using different arguments based on the database type
if DATABASE_URL.startswith("sqlite:///"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ComplaintStatus(str, enum.Enum):
    registered = "Registered"
    in_progress = "In Progress"
    resolved = "Resolved"

# Note: Your Complaint and User models will be defined in a separate models.py file.
# The `Base` object above is what links them to the database engine.