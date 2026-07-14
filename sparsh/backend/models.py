from sqlalchemy import Column, Integer, String, Boolean, Date, ForeignKey, Text, DateTime, func
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(200), nullable=False)
    role = Column(String(20), nullable=False) # admin, doctor, patient
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    doctor_profile = relationship("Doctor", back_populates="user", uselist=False, cascade="all, delete-orphan")
    patient_profile = relationship("Patient", back_populates="user", uselist=False, cascade="all, delete-orphan")

class Doctor(Base):
    __tablename__ = "doctors"
    
    doctor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    phone = Column(String(20), nullable=True)
    specialization = Column(String(100), nullable=True)
    experience = Column(Integer, nullable=True) # Years
    qualification = Column(String(150), nullable=True)
    availability = Column(String(200), nullable=True)
    is_approved = Column(Boolean, default=False) # Admin needs to approve registered doctors
    
    user = relationship("User", back_populates="doctor_profile")

class Patient(Base):
    __tablename__ = "patients"
    
    patient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    phone = Column(String(20), nullable=True)
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    address = Column(Text, nullable=True)
    
    user = relationship("User", back_populates="patient_profile")

class Appointment(Base):
    __tablename__ = "appointments"
    
    appointment_id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    patient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    appointment_date = Column(Date, nullable=False)
    appointment_time = Column(String(50), nullable=False)
    status = Column(String(50), default="Pending") # Pending, Approved, Rejected, Cancelled
    symptoms = Column(Text, nullable=True)
    
    # Direct access to patient/doctor details
    doctor = relationship("User", foreign_keys=[doctor_id])
    patient = relationship("User", foreign_keys=[patient_id])

class Prescription(Base):
    __tablename__ = "prescriptions"
    
    prescription_id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    patient_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    appointment_id = Column(Integer, ForeignKey("appointments.appointment_id", ondelete="SET NULL"), nullable=True)
    
    diagnosis = Column(String(200), nullable=False)
    medicines = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    follow_up_date = Column(Date, nullable=True)
    
    doctor = relationship("User", foreign_keys=[doctor_id])
    patient = relationship("User", foreign_keys=[patient_id])
    appointment = relationship("Appointment")
