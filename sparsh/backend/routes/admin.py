from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database import get_db
import models, schemas, auth

router = APIRouter(prefix="/api/admin", tags=["Admin"])

# 1. Admin Dashboard Stats
@router.get("/stats", response_model=schemas.AdminDashboardStats)
def get_admin_stats(current_user: models.User = Depends(auth.get_current_admin), db: Session = Depends(get_db)):
    total_doctors = db.query(models.Doctor).count()
    total_patients = db.query(models.Patient).count()
    total_appointments = db.query(models.Appointment).count()
    active_users = db.query(models.User).count()
    
    return {
        "total_doctors": total_doctors,
        "total_patients": total_patients,
        "total_appointments": total_appointments,
        "active_users": active_users
    }

# 2. Get All Doctors (including approved and pending approval)
@router.get("/doctors", response_model=List[schemas.DoctorProfileResponse])
def get_all_doctors(current_user: models.User = Depends(auth.get_current_admin), db: Session = Depends(get_db)):
    doctors = db.query(models.Doctor).all()
    # Eagerly load user records
    for doc in doctors:
        doc.user = db.query(models.User).filter(models.User.id == doc.doctor_id).first()
    return doctors

# 3. Approve Doctor Account
@router.put("/doctors/{doctor_id}/approve", response_model=schemas.DoctorProfileResponse)
def approve_doctor(doctor_id: int, current_user: models.User = Depends(auth.get_current_admin), db: Session = Depends(get_db)):
    doctor = db.query(models.Doctor).filter(models.Doctor.doctor_id == doctor_id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Doctor profile not found"
        )
    
    doctor.is_approved = True
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    
    doctor.user = db.query(models.User).filter(models.User.id == doctor.doctor_id).first()
    return doctor

# 4. Get All Patients
@router.get("/patients", response_model=List[schemas.PatientProfileResponse])
def get_all_patients(current_user: models.User = Depends(auth.get_current_admin), db: Session = Depends(get_db)):
    patients = db.query(models.Patient).all()
    # Eagerly load user records
    for pat in patients:
        pat.user = db.query(models.User).filter(models.User.id == pat.patient_id).first()
    return patients

# 5. Delete User Account (cascade will delete doctor/patient profile automatically)
@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, current_user: models.User = Depends(auth.get_current_admin), db: Session = Depends(get_db)):
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Admin cannot delete their own user account"
        )
        
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="User account not found"
        )
        
    db.delete(user)
    db.commit()
    return None
