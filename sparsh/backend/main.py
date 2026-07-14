import os
from dotenv import load_dotenv
load_dotenv()
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from database import engine, Base, get_db
import models
import schemas
import auth
from routes import patients, doctors, appointments, admin

# Lifespan async manager to handle database setup and seeding
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure all tables are created in the database
    Base.metadata.create_all(bind=engine)
    
    # Initialize a db session to seed initial data
    db = next(get_db())
    try:
        # 1. Seed default Admin user
        admin_email = "admin@srishticare.com"
        admin_exists = db.query(models.User).filter(models.User.email == admin_email).first()
        if not admin_exists:
            hashed_pw = auth.get_password_hash("admin123")
            admin_user = models.User(
                name="Srishti Care Admin",
                email=admin_email,
                password=hashed_pw,
                role="admin"
            )
            db.add(admin_user)
            db.commit()
            print("Database Seeding: Created Srishti Care admin user (admin@srishticare.com)")
            
        # 2. Seed a sample approved Doctor
        doc_email = "dr.sharma@srishticare.com"
        doc_exists = db.query(models.User).filter(models.User.email == doc_email).first()
        if not doc_exists:
            hashed_pw = auth.get_password_hash("doctor123")
            doc_user = models.User(
                name="Dr. Alok Sharma",
                email=doc_email,
                password=hashed_pw,
                role="doctor"
            )
            db.add(doc_user)
            db.commit()
            db.refresh(doc_user)
            
            doc_profile = models.Doctor(
                doctor_id=doc_user.id,
                phone="+919876543210",
                specialization="Cardiology",
                experience=12,
                qualification="MD, DM (Cardiology) - AIIMS Delhi",
                availability="Mon-Fri 09:00 AM - 02:00 PM",
                is_approved=True
            )
            db.add(doc_profile)
            db.commit()
            print("Database Seeding: Created sample approved Doctor (dr.sharma@srishticare.com)")

        # 3. Seed another sample pending Doctor
        doc_pending_email = "dr.verma@srishticare.com"
        doc_pending_exists = db.query(models.User).filter(models.User.email == doc_pending_email).first()
        if not doc_pending_exists:
            hashed_pw = auth.get_password_hash("doctor123")
            doc_user = models.User(
                name="Dr. Neha Verma",
                email=doc_pending_email,
                password=hashed_pw,
                role="doctor"
            )
            db.add(doc_user)
            db.commit()
            db.refresh(doc_user)
            
            doc_profile = models.Doctor(
                doctor_id=doc_user.id,
                phone="+919812345678",
                specialization="Pediatrics",
                experience=6,
                qualification="MBBS, DCH (Pediatrics)",
                availability="Mon-Sat 04:00 PM - 08:00 PM",
                is_approved=False # Pending approval
            )
            db.add(doc_profile)
            db.commit()
            print("Database Seeding: Created sample pending Doctor (dr.verma@srishticare.com)")
            
        # 4. Seed a sample Patient
        pat_email = "patient@gmail.com"
        pat_exists = db.query(models.User).filter(models.User.email == pat_email).first()
        if not pat_exists:
            hashed_pw = auth.get_password_hash("patient123")
            pat_user = models.User(
                name="Ramesh Kumar",
                email=pat_email,
                password=hashed_pw,
                role="patient"
            )
            db.add(pat_user)
            db.commit()
            db.refresh(pat_user)
            
            pat_profile = models.Patient(
                patient_id=pat_user.id,
                phone="+919123456780",
                age=42,
                gender="Male",
                address="Flat 402, Sunshine Apartments, Sector 12, Dwarka, New Delhi"
            )
            db.add(pat_profile)
            db.commit()
            print("Database Seeding: Created sample Patient (patient@gmail.com)")
            
    except Exception as err:
        print(f"Database Seeding warning: {err}")
    finally:
        db.close()
        
    yield

# Create FastAPI instance with Lifespan
app = FastAPI(
    title="Srishti Care",
    description="A comprehensive, beginner-friendly Healthcare Management System.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register sub-routes
app.include_router(patients.router)
app.include_router(doctors.router)
app.include_router(appointments.router)
app.include_router(admin.router)

# Unified Login Endpoint
@app.post("/api/auth/login", response_model=schemas.Token)
def login(payload: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == payload.email).first()
    if not user or not auth.verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
        
    # Check if role matches user record
    if user.role != payload.role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Access denied: You are registered as a {user.role}, not {payload.role}"
        )
        
    # Standard JWT token payload creation
    access_token = auth.create_access_token(data={"sub": user.email, "role": user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role,
        "name": user.name,
        "email": user.email
    }

# Unified Logout Endpoint (Clear session helper)
@app.post("/api/auth/logout")
def logout():
    return {"detail": "Successfully logged out"}

# Serve frontend HTML/CSS/JS files (fallback to static files)
# Ensure API endpoints take precedence by mounting static files at the end
frontend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend")
else:
    # If starting from root folder directly
    if os.path.exists("frontend"):
        app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
if __name__ == "__main__":
        import uvicorn
        uvicorn.run(app, host="127.0.0.1", port=8000)
