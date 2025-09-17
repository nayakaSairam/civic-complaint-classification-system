from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
import enum
import os

# Use the DATABASE_URL environment variable provided by Render
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    # Fallback to a local SQLite database for development
    DATABASE_URL = "sqlite:///./complaints.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ComplaintStatus(str, enum.Enum):
    registered = "Registered"
    in_progress = "In Progress"
    resolved = "Resolved"

# Rest of your models stay the same