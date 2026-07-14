# Srishti Care - Healthcare Management System

**Srishti Care** is a complete, role-based Healthcare Management System. Patients can search for medical doctors, book clinical slots, and view electronic prescriptions, while Practitioners and Administrators verify schedules and manage patient histories.

---

## Tech Stack & Features

* **Backend**: FastAPI (Python REST API with Swagger documentation support)
* **ORM**: SQLAlchemy 2.0+ (compatible with SQLite and PostgreSQL)
* **Authentication**: JWT token verification & `passlib` password hashing
* **Database**: NeonDB (PostgreSQL) in production, fallback to SQLite for local development
* **Frontend**: Vanilla HTML5, CSS3, and JavaScript (statically served by FastAPI)
* **Design**: Premium white & blue theme, Outfit font, glassmorphism cards, dynamic sidebars, and toast alerts

---

## Folder Structure

```text
healthcare-management-system/ (workspace root)
│
├── backend/
│   ├── routes/
│   │   ├── admin.py          # Admin endpoints (verification, deletion, stats)
│   │   ├── appointments.py   # Scheduling & prescriptions management
│   │   ├── doctors.py        # Approved doctor indexing & profiling
│   │   └── patients.py       # Patient registration & profiles
│   ├── auth.py               # Token lifecycle & security dependencies
│   ├── database.py           # SQL connections and session makers
│   ├── main.py               # Application startup, CORS & static file mounting
│   ├── models.py             # Declarative SQLAlchemy database schemas
│   └── schemas.py            # Pydantic request/response validations
│
├── frontend/
│   ├── assets/
│   │   └── srishti_care_hero.png  # High-quality website banner asset
│   ├── css/
│   │   └── style.css         # Modern styling declarations
│   ├── js/
│   │   └── app.js            # General fetch requests wrapper & alerts
│   ├── admin_dashboard.html  # System management panel
│   ├── doctor_dashboard.html # Practitioner portal
│   ├── index.html            # Landing homepage
│   ├── login.html            # Role-based credential submission screen
│   ├── patient_dashboard.html# Patient portal & booking forms
│   └── signup.html           # New patient & doctor sign-up
│
├── requirements.txt          # Python dependencies
└── README.md                 # Project instructions
```

---

## Quick Start (Local SQLite Mode)

To run the application immediately without configuring cloud databases:

### 1. Set Up Environment & Install Dependencies
Ensure you have Python 3.8+ installed. Open your terminal in the project directory and run:

```bash
pip install -r requirements.txt
```

### 2. Start the Server
Run the Uvicorn hot-reloader command:

```bash
uvicorn backend.main:app --reload
```

### 3. Open Srishti Care
Open your browser and navigate to:
* **Application URL**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
* **API Documentation**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (FastAPI Swagger UI)

---

## Seed Accounts for Immediate Testing

On initial launch, the system automatically inserts sample data. You can log in with:

| Role | Username / Email | Password | Account Status |
| :--- | :--- | :--- | :--- |
| **Admin** | `admin@srishticare.com` | `admin123` | Active |
| **Doctor (Cardiology)** | `dr.sharma@srishticare.com` | `doctor123` | Approved (Active) |
| **Doctor (Pediatrics)** | `dr.verma@srishticare.com` | `doctor123` | Pending Approval |
| **Patient** | `patient@gmail.com` | `patient123` | Active |

---

## NeonDB (PostgreSQL) Production Setup

To switch from the default SQLite database file to NeonDB, set the `DATABASE_URL` environment variable before starting the server:

### On Windows PowerShell:
```powershell
$env:DATABASE_URL="postgresql://[user]:[password]@[neondb-hostname]/[database-name]?sslmode=require"
uvicorn backend.main:app --reload
```

### On Windows Command Prompt (CMD):
```cmd
set DATABASE_URL=postgresql://[user]:[password]@[neondb-hostname]/[database-name]?sslmode=require
uvicorn backend.main:app --reload
```

### On Linux / macOS:
```bash
export DATABASE_URL="postgresql://[user]:[password]@[neondb-hostname]/[database-name]?sslmode=require"
uvicorn backend.main:app --reload
```

FastAPI automatically parses this string, updates the engine driver to use `psycopg2`, and initializes all required tables and default seed data on NeonDB!

---

## Walkthrough Testing Scenarios

1. **Verify Patient Booking**:
   - Log in as the patient `patient@gmail.com` / `patient123`.
   - Go to "Book Appointment", select **Dr. Alok Sharma**, pick a date/time, add symptoms, and click "Book Now".
   - View your pending request in the "My Appointments" history.

2. **Verify Doctor Response**:
   - Log in as the doctor `dr.sharma@srishticare.com` / `doctor123`.
   - On the Overview screen, check the "Pending Approval Requests". Click the green checkmark to Approve the patient's slot.
   - Go to "Add Prescription", select the patient's name, choose the linked booking ID, write a diagnosis and medicine instructions, and submit.

3. **Verify Prescription Printing**:
   - Log back in as `patient@gmail.com`. Go to "Prescriptions".
   - Locate the newly issued prescription, click "View/Print", and click "Print Prescription" inside the mock PDF layout.

4. **Verify Admin Auditor Controls**:
   - Log in as the administrator `admin@srishticare.com` / `admin123`.
   - View system counters (Total users, doctors, appointments).
   - In "Manage Doctors", locate **Dr. Neha Verma** (Pediatrics) who is currently "Pending Verification", and click the green checkmark to Approve/Activate her account.
   - Audits or deletes doctors, patients, or cancellations.
