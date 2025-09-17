import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, create_tables

# Define the database connection
DATABASE_URL = "sqlite:///./complaints.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

admin_accounts = {
    "superadmin": {"password": "super123", "role": "superadmin", "department": None},
    "buildings_admin": {"password": "build123", "role": "department_admin", "department": "Department of Buildings"},
    "consumer_admin": {"password": "consumer123", "role": "department_admin", "department": "Department of Consumer and Worker Protection"},
    "education_admin": {"password": "edu123", "role": "department_admin", "department": "Department of Education"},
    "environment_admin": {"password": "env123", "role": "department_admin", "department": "Department of Environmental Protection"},
    "health_admin": {"password": "health123", "role": "department_admin", "department": "Department of Health and Mental Hygiene"},
    "homeless_admin": {"password": "home123", "role": "department_admin", "department": "Department of Homeless Services"},
    "housing_admin": {"password": "house123", "role": "department_admin", "department": "Department of Housing Preservation and Development"},
    "parks_admin": {"password": "park123", "role": "department_admin", "department": "Department of Parks and Recreation"},
    "sanitation_admin": {"password": "clean123", "role": "department_admin", "department": "Department of Sanitation"},
    "transport_admin": {"password": "trans123", "role": "department_admin", "department": "Department of Transportation"},
    "economic_admin": {"password": "eco123", "role": "department_admin", "department": "Economic Development Corporation"},
    "police_admin": {"password": "police123", "role": "department_admin", "department": "New York City Police Department"},
    "tech_admin": {"password": "tech123", "role": "department_admin", "department": "Office of Technology and Innovation"},
    "taxi_admin": {"password": "taxi123", "role": "department_admin", "department": "Taxi and Limousine Commission"}
}

def create_admin_users():
    db = SessionLocal()
    try:
        for username, data in admin_accounts.items():
            existing_user = db.query(User).filter(User.name == username).first()
            if not existing_user:
                new_admin = User(
                    name=username,
                    email=f"{username}@civic.gov",
                    password=data["password"],
                    role=data["role"],
                    department=data["department"]
                )
                db.add(new_admin)
                print(f"Created admin user: {username}")
            else:
                print(f"Admin user '{username}' already exists. Skipping.")
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error creating admin users: {e}", file=sys.stderr)
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()  # Ensure tables exist
    create_admin_users()