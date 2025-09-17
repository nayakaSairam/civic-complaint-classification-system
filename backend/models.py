import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Define the database engine and base
DATABASE_URL = "sqlite:///./complaints.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
Base = declarative_base()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="citizen") # 'citizen' or 'admin'
    department = Column(String, nullable=True)
    
    complaints = relationship("Complaint", back_populates="citizen")

class Complaint(Base):
    __tablename__ = "complaints"
    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    location = Column(String)
    department = Column(String)
    status = Column(String, default="Registered")
    registered = Column(DateTime, default=datetime.datetime.now)
    resolved = Column(DateTime, nullable=True)
    citizen_id = Column(Integer, ForeignKey("users.id"))

    citizen = relationship("User", back_populates="complaints")

# Create the database tables
def create_tables():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully!")