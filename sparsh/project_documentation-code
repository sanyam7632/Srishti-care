# Srishti Care - Project Documentation

This document provides a comprehensive overview of the **Srishti Care** Healthcare Management System, explaining its system workflows, architecture, data schemas, and role-based modules.

---

## 1. System Architecture

Srishti Care is designed as a modular, full-stack application built using a light, high-performance tech stack:

```mermaid
graph LR
  A[Vanilla Frontend HTML/CSS/JS] <-->|JSON / HTTP REST| B[FastAPI Backend Server]
  B <-->|SQLAlchemy ORM| C[(NeonDB PostgreSQL / SQLite)]
```

* **Client Layer**: Uses plain HTML5, CSS3, and JavaScript, ensuring lightweight pages, rapid load times, and simple customization.
* **Server Layer**: FastAPI handles routing, request validation via Pydantic, password encryption via `bcrypt`, and session authentication using JWT (JSON Web Tokens).
* **Database Layer**: SQLAlchemy coordinates queries. The system defaults to local SQLite files for development, and connects to NeonDB PostgreSQL in production by reading `DATABASE_URL`.

---

## 2. Entity Relationship (ER) Diagram

The database is structured around five tables. The `doctors` and `patients` tables share a **1-to-1** relationship with the `users` table, inheriting credentials and profile records.

```mermaid
erDiagram
    USERS {
        int id PK
        string name
        string email UK
        string password
        string role
        datetime created_at
    }
    DOCTORS {
        int doctor_id PK, FK
        string phone
        string specialization
        int experience
        string qualification
        string availability
        boolean is_approved
    }
    PATIENTS {
        int patient_id PK, FK
        string phone
        int age
        string gender
        string address
    }
    APPOINTMENTS {
        int appointment_id PK
        int doctor_id FK
        int patient_id FK
        date appointment_date
        string appointment_time
        string status
        string symptoms
    }
    PRESCRIPTIONS {
        int prescription_id PK
        int doctor_id FK
        int patient_id FK
        int appointment_id FK
        string diagnosis
        string medicines
        string notes
        date follow_up_date
    }

    USERS ||--o| DOCTORS : "extends to"
    USERS ||--o| PATIENTS : "extends to"
    USERS ||--o{ APPOINTMENTS : "books / handles"
    USERS ||--o{ PRESCRIPTIONS : "receives / drafts"
    APPOINTMENTS ||--o| PRESCRIPTIONS : "associated with"
```

---

## 3. System Flowchart

The system runs on role-based authentication. Below is the workflow diagram mapping interactions between Patients, Doctors, and Admins:

```mermaid
flowchart TD
    Start([Launch Srishti Care]) --> Landing{Has Session Token?}
    
    Landing -->|No| Login[Open Login Page]
    Landing -->|Yes| Route[Dashboard Redirect]
    
    Login --> RoleSel{Select Role}
    
    RoleSel -->|Patient| PatDash[Patient Dashboard]
    RoleSel -->|Doctor| DocVerify{Doctor Approved by Admin?}
    RoleSel -->|Admin| AdmDash[Admin Dashboard]
    
    DocVerify -->|No| DocLock[Awaiting Activation Screen]
    DocVerify -->|Yes| DocDash[Doctor Dashboard]
    
    %% Patient Flow
    PatDash --> PatBook[Book Appointment]
    PatBook --> DocList[Load Approved Doctors List]
    DocList --> SubmitApt[Submit Booking - Status: Pending]
    
    PatDash --> PatRx[Download Prescriptions]
    
    %% Doctor Flow
    DocDash --> DocApprove[Approve/Reject Pending Appointments]
    DocApprove -->|Approve| CompleteApt[Slot Status: Approved]
    
    DocDash --> DocRx[Add Prescription]
    DocRx --> SaveRx[Draft Medicines & Instructions] --> PatRx
    
    %% Admin Flow
    AdmDash --> AdmDocs[Review Registered Doctors]
    AdmDocs -->|Click Activate| ActivateDoc[Update Doctor is_approved = True] --> DocVerify
    
    AdmDash --> AdmUsers[Manage Accounts & Deletions]
```

---

## 4. Role-Based Module Details

### A. Patient Module
* **Registration / Sign Up**: Provides name, contact email, phone, age, gender, address, and password. Immediately receives a JWT session on success.
* **Dashboard Overview**: Displays summary cards (Upcoming appointments, Total history, Prescription count).
* **Booking Panel**: Selects from approved doctors. Selecting a practitioner automatically pulls their clinical specialization.
* **Prescription Viewer**: Renders prescriptions inside an interactive printable prescription layout, with clean support for browser printing (`Ctrl+P` / print button).
* **Profile Settings**: Allows editing of name, phone number, age, gender, and residential location.

### B. Doctor Module
* **Registration**: Details clinical qualifications, specialization, years of experience, and availability hours.
* **Security Lock Screen**: Doctors cannot view dashboards or schedules until an administrator activates their account. Hitting any dashboard endpoint before verification yields a warning message.
* **Appointments Panel**: The doctor reviews today's active schedules, approves pending bookings, or rejects them.
* **Prescription Builder**: Connects directly to patients and appointments, compiling diagnosis details, medicine instructions, and follow-up schedules.
* **Availability Management**: Doctors can edit their clinic timings instantly, which updates in the patient's booking portal in real time.

### C. Admin Module
* **Overview panel**: Audits overall user numbers, total consultations, and system accounts.
* **Doctor Activation Desk**: Filters registered doctors pending verification. Clicking "Activate" moves their profile status from Pending to Active.
* **Database Auditor**: Provides a list of all registered patients, doctor credentials, and system bookings. Administrators can manually cancel bookings or delete accounts.

---

## 5. Security & Session Management

1. **Password Encryption**: Raw passwords submitted on registration are hashed using `bcrypt` salting (`bcrypt.hashpw`) before database insertion. The database never stores plaintext passwords.
2. **JWT Credentials Verification**: During login, the server returns an access token containing:
   - `sub`: User email
   - `role`: Designated user role
   - `exp`: Expiry time (set to 2 hours of validity)
3. **Role Checks Guards**: Backend endpoints verify the JWT signature and enforce role requirements:
   - `@router.get("/profile", current_user = Depends(get_current_patient))`
   - `@router.get("/profile", current_user = Depends(get_current_doctor))`
   - `@router.get("/stats", current_user = Depends(get_current_admin))`

---

## 6. How to Configure NeonDB PostgreSQL

By default, Srishti Care boots in SQLite mode, creating a local database file `srishti_care.db`. To swap this configuration to NeonDB in production:

1. Open your cloud console on [neon.tech](https://neon.tech) and create a PostgreSQL database.
2. Copy your connection URL: `postgresql://user:password@host/dbname?sslmode=require`
3. Edit the [`.env`](file:///c:/Users/haris/OneDrive/Desktop/mansi/.env) file in your workspace root:
   ```env
   DATABASE_URL=postgresql://user:password@host/dbname?sslmode=require
   ```
4. Restart your server. Srishti Care will automatically migrate database models and seed fresh accounts on NeonDB!
