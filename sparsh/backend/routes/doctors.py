from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models, schemas, auth

router = APIRouter(prefix="/api/doctors", tags=["Doctors"])

# Doctor Registration
@router.post("/register", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
def register_doctor(payload: schemas.DoctorRegister, db: Session = Depends(get_db)):
    # Check if email is already in use
    existing_user = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists"
        )
    
    # Create base user
    hashed_pw = auth.get_password_hash(payload.password)
    db_user = models.User(
        name=payload.name,
        email=payload.email,
        password=hashed_pw,
        role="doctor"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create doctor profile details (default is_approved to False)
    db_doctor = models.Doctor(
        doctor_id=db_user.id,
        phone=payload.phone,
        specialization=payload.specialization,
        experience=payload.experience,
        qualification=payload.qualification,
        availability=payload.availability,
        is_approved=False
    )
    db.add(db_doctor)
    db.commit()
    
    # Generate token (they can log in, but guard check will complain if not approved)
    access_token = auth.create_access_token(data={"sub": db_user.email, "role": db_user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": db_user.role,
        "name": db_user.name,
        "email": db_user.email
    }

# Get list of approved doctors for patients to book appointments
@router.get("", response_model=List[schemas.DoctorProfileResponse])
def get_approved_doctors(db: Session = Depends(get_db)):
    doctors = db.query(models.Doctor).filter(models.Doctor.is_approved == True).all()
    # Eagerly load user relationship details
    for doc in doctors:
        doc.user = db.query(models.User).filter(models.User.id == doc.doctor_id).first()
    return doctors

# Get doctor's own profile (requires approved doctor token)
@router.get("/profile", response_model=schemas.DoctorProfileResponse)
def get_doctor_profile(current_user: models.User = Depends(auth.get_current_doctor), db: Session = Depends(get_db)):
    doctor = db.query(models.Doctor).filter(models.Doctor.doctor_id == current_user.id).first()
    doctor.user = current_user
    return doctor

# Update doctor profile details
@router.put("/profile", response_model=schemas.DoctorProfileResponse)
def update_doctor_profile(payload: schemas.DoctorUpdate, current_user: models.User = Depends(auth.get_current_doctor), db: Session = Depends(get_db)):
    doctor = db.query(models.Doctor).filter(models.Doctor.doctor_id == current_user.id).first()
    
    # Update base user details if provided
    if payload.name is not None:
        current_user.name = payload.name
        db.add(current_user)
        
    # Update doctor details
    if payload.phone is not None:
        doctor.phone = payload.phone
    if payload.specialization is not None:
        doctor.specialization = payload.specialization
    if payload.experience is not None:
        doctor.experience = payload.experience
    if payload.qualification is not None:
        doctor.qualification = payload.qualification
    if payload.availability is not None:
        doctor.availability = payload.availability
        
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    doctor.user = current_user
    return doctor
