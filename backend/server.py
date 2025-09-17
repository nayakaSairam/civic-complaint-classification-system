from fastapi import FastAPI, Request, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from database import SessionLocal, engine, Base, ComplaintStatus
from models import Complaint, User, create_tables
import contextlib
import uvicorn
import joblib
from sentence_transformers import SentenceTransformer
import datetime
import uuid
import os

# Create the FastAPI app instance
app = FastAPI()

# Add CORS middleware to allow cross-origin requests from your frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Use a context manager to get the database session
@contextlib.contextmanager
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create database tables when the app starts up
@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    print("Database tables created!")

# Load machine learning model and label encoder
try:
    loaded_best_model = joblib.load("complaint_agency_bert_classifier.joblib")
    loaded_le = joblib.load("label_encoder_bert.joblib")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    print("Model, label encoder, and embedder loaded successfully.")
except FileNotFoundError:
    print("Error: Model files not found. Ensure they are in the 'backend' directory.")
    sys.exit(1)

# API Routes
# =========================================================================

# Helper function to get a user by email
def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

# Helper function to get a complaint by ID
def get_complaint_by_id(db: Session, complaint_id: int):
    return db.query(Complaint).filter(Complaint.id == complaint_id).first()

# User login and authentication
@app.post("/login")
def login(request: Request, db: Session = Depends(get_db)):
    # Assuming a simple JSON body with email and password
    user_data = request.json()
    email = user_data.get("email")
    password = user_data.get("password")
    
    user = get_user_by_email(db, email)
    if not user or user.password != password: # Warning: This is not secure! Use a password hashing library.
        raise HTTPException(status_code=400, detail="Invalid email or password")
    
    return {"message": "Login successful", "user": user.email, "user_id": user.id}

# User signup
@app.post("/signup")
def signup(request: Request, db: Session = Depends(get_db)):
    user_data = request.json()
    name = user_data.get("name")
    email = user_data.get("email")
    password = user_data.get("password")
    
    if get_user_by_email(db, email):
        raise HTTPException(status_code=400, detail="Email already registered")
        
    new_user = User(name=name, email=email, password=password) # Warning: Not hashed!
    db.add(new_user)
    db.commit()
    return {"message": "User created successfully"}

# Submit a new complaint
@app.post("/complaints")
def create_complaint(request: Request, db: Session = Depends(get_db)):
    complaint_data = request.json()
    title = complaint_data.get("title")
    description = complaint_data.get("description")
    location = complaint_data.get("location")
    user_id = complaint_data.get("user_id")

    # Predict the department using the ML model
    text_input = f"{title}. {description}"
    embeddings = embedder.encode([text_input])
    prediction = loaded_best_model.predict(embeddings)
    predicted_department = loaded_le.inverse_transform(prediction)[0]

    new_complaint = Complaint(
        title=title,
        description=description,
        location=location,
        user_id=user_id,
        department=predicted_department,
        status=ComplaintStatus.registered
    )
    db.add(new_complaint)
    db.commit()
    db.refresh(new_complaint)
    
    return {"message": "Complaint submitted and classified.", "complaint": new_complaint}

# Get a user's complaints
@app.get("/complaints/user/{user_id}")
def get_user_complaints(user_id: int, db: Session = Depends(get_db)):
    complaints = db.query(Complaint).filter(Complaint.user_id == user_id).all()
    return complaints

# Get all complaints
@app.get("/complaints")
def get_all_complaints(db: Session = Depends(get_db)):
    complaints = db.query(Complaint).all()
    return complaints

# Update complaint status
@app.put("/complaints/{complaint_id}")
def update_complaint_status(complaint_id: int, request: Request, db: Session = Depends(get_db)):
    complaint = get_complaint_by_id(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    new_status = request.json().get("status")
    if new_status not in [e.value for e in ComplaintStatus]:
        raise HTTPException(status_code=400, detail="Invalid status")
        
    complaint.status = new_status
    if new_status == ComplaintStatus.resolved:
        complaint.resolved_date = datetime.datetime.utcnow()
    
    db.commit()
    db.refresh(complaint)
    return {"message": "Complaint status updated", "complaint": complaint}

# Delete a complaint
@app.delete("/complaints/{complaint_id}")
def delete_complaint(complaint_id: int, db: Session = Depends(get_db)):
    complaint = get_complaint_by_id(db, complaint_id)
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    
    db.delete(complaint)
    db.commit()
    return {"message": "Complaint deleted successfully"}