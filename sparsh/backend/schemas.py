from pydantic import BaseModel, EmailStr, Field
from datetime import date, datetime
from typing import Optional, List

# --- AUTH SCHEMAS ---

class UserLogin(BaseModel):
    email: EmailStr
    password: str
    role: str # 'patient', 'doctor', 'admin'

class PatientRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    age: int = Field(..., gt=0, lt=150)
    gender: str = Field(..., pattern="^(Male|Female|Other)$")
    address: str = Field(..., min_length=5)
    password: str = Field(..., min_length=6)

class DoctorRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    specialization: str = Field(..., min_length=2)
    experience: int = Field(..., ge=0)
    qualification: str = Field(..., min_length=2)
    availability: str = Field(..., min_length=5)
    password: str = Field(..., min_length=6)

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    name: str
    email: str

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None


# --- USER & PROFILE SCHEMAS ---

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

class PatientProfileResponse(BaseModel):
    patient_id: int
    phone: str
    age: int
    gender: str
    address: str
    user: UserResponse

    class Config:
        from_attributes = True

class DoctorProfileResponse(BaseModel):
    doctor_id: int
    phone: str
    specialization: str
    experience: int
    qualification: str
    availability: str
    is_approved: bool
    user: UserResponse

    class Config:
        from_attributes = True

class PatientUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    address: Optional[str] = None

class DoctorUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    specialization: Optional[str] = None
    experience: Optional[int] = None
    qualification: Optional[str] = None
    availability: Optional[str] = None


# --- APPOINTMENT SCHEMAS ---

class AppointmentCreate(BaseModel):
    doctor_id: int
    appointment_date: date
    appointment_time: str # e.g. "10:00 AM"
    symptoms: Optional[str] = None

class AppointmentUpdateStatus(BaseModel):
    status: str # 'Approved', 'Rejected', 'Cancelled'

class AppointmentResponse(BaseModel):
    appointment_id: int
    doctor_id: int
    patient_id: int
    appointment_date: date
    appointment_time: str
    status: str
    symptoms: Optional[str] = None
    doctor_name: str
    doctor_specialization: str
    patient_name: str
    patient_phone: str

    class Config:
        from_attributes = True


# --- PRESCRIPTION SCHEMAS ---

class PrescriptionCreate(BaseModel):
    patient_id: int
    appointment_id: Optional[int] = None
    diagnosis: str
    medicines: str # List of medicines formatted as text
    notes: Optional[str] = None
    follow_up_date: Optional[date] = None

class PrescriptionResponse(BaseModel):
    prescription_id: int
    doctor_id: int
    doctor_name: str
    patient_id: int
    patient_name: str
    appointment_id: Optional[int] = None
    diagnosis: str
    medicines: str
    notes: Optional[str] = None
    follow_up_date: Optional[date] = None

    class Config:
        from_attributes = True


# --- ADMIN SCHEMAS ---

class AdminDashboardStats(BaseModel):
    total_doctors: int
    total_patients: int
    total_appointments: int
    active_users: int
