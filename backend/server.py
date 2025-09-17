from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
import contextlib
import uvicorn
import joblib
from sentence_transformers import SentenceTransformer
import datetime
import uuid
import sys

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
    # Corrected file paths
    loaded_best_model = joblib.load("complaint_agency_bert_classifier.joblib")
    loaded_le = joblib.load("label_encoder_bert.joblib")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    print("Model, label encoder, and embedder loaded successfully.")
except FileNotFoundError:
    print("Error: Model files not found. Ensure they are in the root of the 'backend' directory.")
    sys.exit(1)

@app.route("/")
def home():
    return "Civic Complaint System Backend"

# Citizen Signup
@app.route("/api/signup", methods=["POST"])
def signup():
    db = SessionLocal()
    try:
        data = request.get_json()
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if db.query(User).filter(User.email == email).first():
            return jsonify({"error": "User with this email already exists."}), 409

        new_user = User(name=name, email=email, password=password, role="citizen")
        db.add(new_user)
        db.commit()
        return jsonify({"message": "User created successfully", "user_id": new_user.id}), 201
    finally:
        db.close()

# Citizen/Admin Login
@app.route("/api/login", methods=["POST"])
def login():
    db = SessionLocal()
    try:
        data = request.get_json()
        email = data.get("email")
        password = data.get("password")
        username = data.get("username")

        user = None
        if email:
            user = db.query(User).filter(User.email == email, User.password == password).first()
        elif username:
            user = db.query(User).filter(User.name == username, User.password == password).first()

        if user:
            return jsonify({
                "message": "Login successful",
                "user_id": user.id,
                "role": user.role,
                "name": user.name,
                "department": user.department
            }), 200
        return jsonify({"error": "Invalid credentials"}), 401
    finally:
        db.close()

# Submit new complaint with ML classification
@app.route("/api/complaints", methods=["POST"])
def create_complaint():
    db = SessionLocal()
    try:
        data = request.get_json()
        title = data.get("title")
        description = data.get("description")
        location = data.get("location")
        user_id = data.get("user_id")
        
        # ML prediction
        with contextlib.redirect_stdout(None):
            embedding = embedder.encode([description])
            pred = loaded_best_model.predict(embedding)
        department = loaded_le.inverse_transform(pred)[0]

        # Generate a unique ID for the complaint
        complaint_id = str(uuid.uuid4())

        new_complaint = Complaint(
            id=complaint_id,
            title=title,
            description=description,
            location=location,
            department=department,
            citizen_id=user_id,
            status="Registered"
        )
        db.add(new_complaint)
        db.commit()
        return jsonify({"message": "Complaint submitted successfully", "complaint": {
            "id": new_complaint.id,
            "title": new_complaint.title,
            "description": new_complaint.description,
            "location": new_complaint.location,
            "department": new_complaint.department,
            "status": new_complaint.status,
            "registered": new_complaint.registered.isoformat(),
            "user_id": new_complaint.citizen_id
        }}), 201
    except Exception as e:
        db.rollback()
        print(f"Error creating complaint: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        db.close()

# Get complaints for a specific user
@app.route("/api/complaints/user/<int:user_id>", methods=["GET"])
def get_user_complaints(user_id):
    db = SessionLocal()
    try:
        complaints = db.query(Complaint).filter(Complaint.citizen_id == user_id).all()
        complaints_list = []
        for c in complaints:
            complaints_list.append({
                "id": c.id,
                "title": c.title,
                "description": c.description,
                "location": c.location,
                "department": c.department,
                "status": c.status,
                "registered": c.registered.isoformat(),
                "resolved": c.resolved.isoformat() if c.resolved else None
            })
        return jsonify(complaints_list), 200
    finally:
        db.close()

# Get all complaints (for admin)
@app.route("/api/complaints", methods=["GET"])
def get_all_complaints():
    db = SessionLocal()
    try:
        complaints = db.query(Complaint).all()
        complaints_list = []
        for c in complaints:
            citizen_email = db.query(User.email).filter(User.id == c.citizen_id).scalar()
            complaints_list.append({
                "id": c.id,
                "title": c.title,
                "description": c.description,
                "location": c.location,
                "department": c.department,
                "status": c.status,
                "registered": c.registered.isoformat(),
                "resolved": c.resolved.isoformat() if c.resolved else None,
                "citizen_email": citizen_email
            })
        return jsonify(complaints_list), 200
    finally:
        db.close()

# Update complaint status
@app.route("/api/complaints/<string:complaint_id>", methods=["PUT"])
def update_complaint(complaint_id):
    db = SessionLocal()
    try:
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            return jsonify({"error": "Complaint not found"}), 404
            
        data = request.get_json()
        new_status = data.get("status")
        
        complaint.status = new_status
        if new_status == "Resolved":
            complaint.resolved = datetime.datetime.now()
        
        db.commit()
        return jsonify({"message": "Complaint updated successfully"}), 200
    finally:
        db.close()

# Delete complaint
@app.route("/api/complaints/<string:complaint_id>", methods=["DELETE"])
def delete_complaint(complaint_id):
    db = SessionLocal()
    try:
        complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
        if not complaint:
            return jsonify({"error": "Complaint not found"}), 404
        
        db.delete(complaint)
        db.commit()
        return jsonify({"message": "Complaint deleted successfully"}), 200
    finally:
        db.close()

if __name__ == "__main__":
    app.run(debug=True, port=5000)