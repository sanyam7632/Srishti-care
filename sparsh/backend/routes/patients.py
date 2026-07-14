from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models, schemas, auth

router = APIRouter(prefix="/api/patients", tags=["Patients"])

# Patient Registration
@router.post("/register", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
def register_patient(payload: schemas.PatientRegister, db: Session = Depends(get_db)):
    # Check if email is already in use
    existing_user = db.query(models.User).filter(models.User.email == payload.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists"
        )
    
    # Create the base user
    hashed_pw = auth.get_password_hash(payload.password)
    db_user = models.User(
        name=payload.name,
        email=payload.email,
        password=hashed_pw,
        role="patient"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Create patient profile details
    db_patient = models.Patient(
        patient_id=db_user.id,
        phone=payload.phone,
        age=payload.age,
        gender=payload.gender,
        address=payload.address
    )
    db.add(db_patient)
    db.commit()
    
    # Generate and return session access token
    access_token = auth.create_access_token(data={"sub": db_user.email, "role": db_user.role})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": db_user.role,
        "name": db_user.name,
        "email": db_user.email
    }

# Get current patient profile
@router.get("/profile", response_model=schemas.PatientProfileResponse)
def get_patient_profile(current_user: models.User = Depends(auth.get_current_patient), db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.patient_id == current_user.id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile details not found"
        )
    patient.user = current_user
    return patient

# Update patient profile
@router.put("/profile", response_model=schemas.PatientProfileResponse)
def update_patient_profile(payload: schemas.PatientUpdate, current_user: models.User = Depends(auth.get_current_patient), db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.patient_id == current_user.id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile details not found"
        )
    
    # Update base user details if provided
    if payload.name is not None:
        current_user.name = payload.name
        db.add(current_user)
        
    # Update patient profile fields
    if payload.phone is not None:
        patient.phone = payload.phone
    if payload.age is not None:
        patient.age = payload.age
    if payload.gender is not None:
        patient.gender = payload.gender
    if payload.address is not None:
        patient.address = payload.address
        
    db.add(patient)
    db.commit()
    db.refresh(patient)
    
    patient.user = current_user
    return patient

# Get patient prescriptions list
@router.get("/prescriptions", response_model=List[schemas.PrescriptionResponse])
def get_patient_prescriptions(current_user: models.User = Depends(auth.get_current_patient), db: Session = Depends(get_db)):
    prescriptions = db.query(models.Prescription).filter(models.Prescription.patient_id == current_user.id).all()
    
    # Format and return items
    results = []
    for pr in prescriptions:
        results.append(schemas.PrescriptionResponse(
            prescription_id=pr.prescription_id,
            doctor_id=pr.doctor_id,
            doctor_name=pr.doctor.name,
            patient_id=pr.patient_id,
            patient_name=pr.patient.name,
            appointment_id=pr.appointment_id,
            diagnosis=pr.diagnosis,
            medicines=pr.medicines,
            notes=pr.notes,
            follow_up_date=pr.follow_up_date
        ))
    return results
