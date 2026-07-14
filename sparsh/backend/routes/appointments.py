from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from database import get_db
import models, schemas, auth

router = APIRouter(prefix="/api/appointments", tags=["Appointments"])

# 1. Book Appointment (Patient)
@router.post("", response_model=schemas.AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(payload: schemas.AppointmentCreate, current_user: models.User = Depends(auth.get_current_patient), db: Session = Depends(get_db)):
    # Verify doctor exists and is approved
    doctor = db.query(models.Doctor).filter(
        models.Doctor.doctor_id == payload.doctor_id, 
        models.Doctor.is_approved == True
    ).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Doctor not found or is currently not approved to accept appointments"
        )
        
    db_appointment = models.Appointment(
        doctor_id=payload.doctor_id,
        patient_id=current_user.id,
        appointment_date=payload.appointment_date,
        appointment_time=payload.appointment_time,
        status="Pending",
        symptoms=payload.symptoms
    )
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    
    # Pre-fetch details for schema validation
    doctor_user = db.query(models.User).filter(models.User.id == db_appointment.doctor_id).first()
    patient_details = db.query(models.Patient).filter(models.Patient.patient_id == db_appointment.patient_id).first()
    
    return schemas.AppointmentResponse(
        appointment_id=db_appointment.appointment_id,
        doctor_id=db_appointment.doctor_id,
        patient_id=db_appointment.patient_id,
        appointment_date=db_appointment.appointment_date,
        appointment_time=db_appointment.appointment_time,
        status=db_appointment.status,
        symptoms=db_appointment.symptoms,
        doctor_name=doctor_user.name if doctor_user else "",
        doctor_specialization=doctor.specialization or "",
        patient_name=current_user.name,
        patient_phone=patient_details.phone if patient_details else ""
    )

# 2. Get Appointments List (Role-Based Unified Query)
@router.get("", response_model=List[schemas.AppointmentResponse])
def get_appointments(current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    if current_user.role == "patient":
        appointments = db.query(models.Appointment).filter(models.Appointment.patient_id == current_user.id).all()
    elif current_user.role == "doctor":
        # Check doctor approval
        if not current_user.doctor_profile or not current_user.doctor_profile.is_approved:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Doctor account pending approval"
            )
        appointments = db.query(models.Appointment).filter(models.Appointment.doctor_id == current_user.id).all()
    elif current_user.role == "admin":
        appointments = db.query(models.Appointment).all()
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Unknown user role"
        )
        
    results = []
    for app in appointments:
        doc_profile = db.query(models.Doctor).filter(models.Doctor.doctor_id == app.doctor_id).first()
        pat_profile = db.query(models.Patient).filter(models.Patient.patient_id == app.patient_id).first()
        
        results.append(schemas.AppointmentResponse(
            appointment_id=app.appointment_id,
            doctor_id=app.doctor_id,
            patient_id=app.patient_id,
            appointment_date=app.appointment_date,
            appointment_time=app.appointment_time,
            status=app.status,
            symptoms=app.symptoms,
            doctor_name=app.doctor.name if app.doctor else "Doctor",
            doctor_specialization=doc_profile.specialization if doc_profile else "",
            patient_name=app.patient.name if app.patient else "Patient",
            patient_phone=pat_profile.phone if pat_profile else ""
        ))
    return results

# 3. Update Appointment Status (Doctor Approve/Reject, Patient Cancel, Admin Override)
@router.put("/{appointment_id}/status", response_model=schemas.AppointmentResponse)
def update_appointment_status(appointment_id: int, payload: schemas.AppointmentUpdateStatus, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    app = db.query(models.Appointment).filter(models.Appointment.appointment_id == appointment_id).first()
    if not app:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Appointment not found"
        )
        
    # Permission verification
    if current_user.role == "patient":
        if app.patient_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Unauthorized: Not your appointment"
            )
        if payload.status != "Cancelled":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Patients are only permitted to cancel appointments"
            )
    elif current_user.role == "doctor":
        if app.doctor_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Unauthorized: Not booked with you"
            )
        if payload.status not in ["Approved", "Rejected"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Doctors are only permitted to approve or reject appointments"
            )
    elif current_user.role == "admin":
        pass # Admin can override status to anything
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Unauthorized role action"
        )
        
    app.status = payload.status
    db.add(app)
    db.commit()
    db.refresh(app)
    
    doc_profile = db.query(models.Doctor).filter(models.Doctor.doctor_id == app.doctor_id).first()
    pat_profile = db.query(models.Patient).filter(models.Patient.patient_id == app.patient_id).first()
    
    return schemas.AppointmentResponse(
        appointment_id=app.appointment_id,
        doctor_id=app.doctor_id,
        patient_id=app.patient_id,
        appointment_date=app.appointment_date,
        appointment_time=app.appointment_time,
        status=app.status,
        symptoms=app.symptoms,
        doctor_name=app.doctor.name if app.doctor else "Doctor",
        doctor_specialization=doc_profile.specialization if doc_profile else "",
        patient_name=app.patient.name if app.patient else "Patient",
        patient_phone=pat_profile.phone if pat_profile else ""
    )

# 4. Create Prescription (Doctor)
@router.post("/prescriptions", response_model=schemas.PrescriptionResponse, status_code=status.HTTP_201_CREATED)
def create_prescription(payload: schemas.PrescriptionCreate, current_user: models.User = Depends(auth.get_current_doctor), db: Session = Depends(get_db)):
    # Verify patient exists
    patient_user = db.query(models.User).filter(
        models.User.id == payload.patient_id, 
        models.User.role == "patient"
    ).first()
    if not patient_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Patient not found"
        )
        
    # Verify optional appointment connection
    if payload.appointment_id:
        app = db.query(models.Appointment).filter(models.Appointment.appointment_id == payload.appointment_id).first()
        if not app or app.doctor_id != current_user.id or app.patient_id != payload.patient_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Appointment linking details are invalid"
            )
            
    db_prescription = models.Prescription(
        doctor_id=current_user.id,
        patient_id=payload.patient_id,
        appointment_id=payload.appointment_id,
        diagnosis=payload.diagnosis,
        medicines=payload.medicines,
        notes=payload.notes,
        follow_up_date=payload.follow_up_date
    )
    db.add(db_prescription)
    db.commit()
    db.refresh(db_prescription)
    
    return schemas.PrescriptionResponse(
        prescription_id=db_prescription.prescription_id,
        doctor_id=db_prescription.doctor_id,
        doctor_name=current_user.name,
        patient_id=db_prescription.patient_id,
        patient_name=patient_user.name,
        appointment_id=db_prescription.appointment_id,
        diagnosis=db_prescription.diagnosis,
        medicines=db_prescription.medicines,
        notes=db_prescription.notes,
        follow_up_date=db_prescription.follow_up_date
    )

# 5. Get Specific Prescription Details
@router.get("/prescriptions/{prescription_id}", response_model=schemas.PrescriptionResponse)
def get_prescription_by_id(prescription_id: int, current_user: models.User = Depends(auth.get_current_user), db: Session = Depends(get_db)):
    pr = db.query(models.Prescription).filter(models.Prescription.prescription_id == prescription_id).first()
    if not pr:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Prescription not found"
        )
        
    # Check permissions (must be Admin, the prescribing Doctor, or the Patient)
    if current_user.role == "patient" and pr.patient_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Access denied"
        )
    elif current_user.role == "doctor" and pr.doctor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Access denied"
        )
    elif current_user.role not in ["admin", "patient", "doctor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Access denied"
        )
        
    return schemas.PrescriptionResponse(
        prescription_id=pr.prescription_id,
        doctor_id=pr.doctor_id,
        doctor_name=pr.doctor.name if pr.doctor else "Doctor",
        patient_id=pr.patient_id,
        patient_name=pr.patient.name if pr.patient else "Patient",
        appointment_id=pr.appointment_id,
        diagnosis=pr.diagnosis,
        medicines=pr.medicines,
        notes=pr.notes,
        follow_up_date=pr.follow_up_date
    )
