# Srishti Care - File-by-File Codebase Documentation

This document explains the purpose, major code structures, functions, and workflows of every file inside the **Srishti Care** Healthcare Management System.

---

## 1. Backend Codebase (`backend/`)

### 📂 [database.py](file:///c:/Users/haris/OneDrive/Desktop/mansi/backend/database.py)
* **Purpose**: Orchestrates database connection and configuration parameters.
* **Key Components**:
  - `load_dotenv()`: Reads `.env` parameters first.
  - `create_engine`: Boots the SQL connection. If using SQLite, it injects `connect_args={"check_same_thread": False}` to bypass multi-threading blocks. If PostgreSQL is detected, it automatically reformats `postgres://` prefix headers to `postgresql://` as required by SQLAlchemy.
  - `SessionLocal`: Prepares database query transactions.
  - `get_db()`: A generator function injected into FastAPI routes to yield database sessions and automatically close them on query completion.

### 📂 [models.py](file:///c:/Users/haris/OneDrive/Desktop/mansi/backend/models.py)
* **Purpose**: Establishes database tables using SQLAlchemy's Declarative Mapping.
* **Key Components**:
  - `User`: Basic credentials model mapping accounts. Includes a `role` column (`admin`, `doctor`, `patient`) and sets cascade triggers on child tables.
  - `Doctor`: Links to `User.id` via `doctor_id` foreign key. Declares specialization, phone, qualification, availability slots, and an `is_approved` verification flag.
  - `Patient`: Links to `User.id` via `patient_id` foreign key. Declares age, gender, address, and phone.
  - `Appointment`: Associates doctor IDs, patient IDs, booking dates/slots, reason symptoms, and scheduling status (`Pending`, `Approved`, `Rejected`, `Cancelled`).
  - `Prescription`: Associates appointments, compile clinical diagnosis descriptions, lists medicines text, follow-up dates, and physician notes.

### 📂 [schemas.py](file:///c:/Users/haris/OneDrive/Desktop/mansi/backend/schemas.py)
* **Purpose**: Houses Pydantic schemas that enforce input parameters validation and reformat output JSON objects.
* **Key Components**:
  - `PatientRegister` & `DoctorRegister`: Form field validators that enforce formats (such as min_length for passwords, name boundaries, age limits, and regex phone configurations).
  - `UserResponse`, `PatientProfileResponse`, `DoctorProfileResponse`: Filters output records, stripping hashed passwords before responding to queries.
  - `AppointmentCreate` & `AppointmentResponse`: Parses dates, booking hours, and outputs matching details.
  - `PrescriptionCreate` & `PrescriptionResponse`: Compiles prescription payloads.

### 📂 [auth.py](file:///c:/Users/haris/OneDrive/Desktop/mansi/backend/auth.py)
* **Purpose**: Manages JWT creation, security guards, and password hashing.
* **Key Components**:
  - `get_password_hash(password)`: Salting and hashing using raw `bcrypt.hashpw` calls.
  - `verify_password(plain, hashed)`: Standard password validation via `bcrypt.checkpw`.
  - `create_access_token(data, expire)`: Compiles JWT scopes (`sub` and `role`) and appends an expiry window (defaults to 120 minutes).
  - `get_current_user`: Extracts the Bearer token from the header, validates the signature using `SECRET_KEY`, queries the matching user, and returns it.
  - `get_current_patient`, `get_current_doctor`, `get_current_admin`: Secondary dependency guards. They intercept queries, verify roles, and ensure doctors are approved before yielding access.

### 📂 [main.py](file:///c:/Users/haris/OneDrive/Desktop/mansi/backend/main.py)
* **Purpose**: Backend server entry point, lifecycle events, and global configurations.
* **Key Components**:
  - `lifespan(app)`: Triggers database migration tables creation, then runs seeding blocks to insert default Admin, Cardiologist, Pediatrician, and Patient records.
  - `CORSMiddleware`: Permits requests across multiple origin ports.
  - `login(payload)`: Evaluates email and password, verifies roles match, generates a JWT token, and returns user details.
  - `app.mount()`: Serves all static HTML frontend directories from root `/`.

---

## 2. Backend Routes (`backend/routes/`)

### 📂 [routes/patients.py](file:///c:/Users/haris/OneDrive/Desktop/mansi/backend/routes/patients.py)
* **Endpoints**:
  - `POST /register`: Registers a new patient user and profile details.
  - `GET /profile`: Loads details of the logged-in patient.
  - `PUT /profile`: Updates editable fields (name, phone, age, gender, address).
  - `GET /prescriptions`: Loads all clinical prescriptions issued to this patient.

### 📂 [routes/doctors.py](file:///c:/Users/haris/OneDrive/Desktop/mansi/backend/routes/doctors.py)
* **Endpoints**:
  - `POST /register`: Registers a new doctor (defaults `is_approved = False`).
  - `GET /`: Returns list of all approved doctors. (Publicly accessible by patients for bookings).
  - `GET /profile`: Loads profile details of the logged-in doctor.
  - `PUT /profile`: Updates specialization, qualifications, and availability timings.

### 📂 [routes/appointments.py](file:///c:/Users/haris/OneDrive/Desktop/mansi/backend/routes/appointments.py)
* **Endpoints**:
  - `POST /`: Patient books an appointment slot (defaults status to `Pending`).
  - `GET /`: Returns list of appointments. The route automatically filters results:
    - Patients see only their own bookings.
    - Doctors see only appointments scheduled with them.
    - Admins see all bookings in the system.
  - `PUT /{id}/status`: Updates appointment status. Enforces permissions:
    - Patients can only change status to `Cancelled`.
    - Doctors can change status to `Approved` or `Rejected`.
    - Admins can change status to anything.
  - `POST /prescriptions`: Doctor issues a prescription linked to a patient and appointment.
  - `GET /prescriptions/{id}`: Displays prescription details (verifies user is the patient, doctor, or admin).

### 📂 [routes/admin.py](file:///c:/Users/haris/OneDrive/Desktop/mansi/backend/routes/admin.py)
* **Endpoints**:
  - `GET /stats`: Returns overall platform stats (total doctors, patients, appointments, users).
  - `GET /doctors`: Lists all doctors (approved and pending).
  - `PUT /doctors/{doctor_id}/approve`: Admin activates a pending doctor account.
  - `GET /patients`: Lists all registered patients.
  - `DELETE /users/{user_id}`: Admin deletes a user account (cascades to wipe profiles).

---

## 3. Frontend Utilities (`frontend/`)

### 📂 [frontend/js/app.js](file:///c:/Users/haris/OneDrive/Desktop/mansi/frontend/js/app.js)
* **Purpose**: Unified client-side storage, api configuration, redirection, and alerting.
* **Key Components**:
  - `saveSession()`: Saves the JWT token, name, email, and role inside `localStorage`.
  - `checkAuthGuard(role)`: Validates that a user is logged in with the correct role. If validation fails, it redirects them to their correct panel or login.
  - `showToast(title, msg, type)`: Spawns toast alert banners dynamically in the top-right corner.
  - `apiRequest(endpoint, options)`: Wrapper that automatically appends `Authorization: Bearer <token>`, parses response JSON, handles standard 401 token expirations, and redirects users to login if needed.
  - `apiLogout()`: Hits backend logout, clears `localStorage`, and returns to home.

### 📂 [frontend/css/style.css](file:///c:/Users/haris/OneDrive/Desktop/mansi/frontend/css/style.css)
* **Purpose**: Styles the Srishti Care interface.
* **Key Components**:
  - Custom Root Variables: Colors, fonts, shadows, borders, transitions.
  - Navigation styles: Sticky blurred background panel, logo, and active links.
  - Grid structures: Two-column hero sections, 4-column statistics grids, dashboard layout panels.
  - Responsive Sidebars: Absolute fixed layouts with highlights. Switches to hamburger toggle layout on screens under 768px.
  - Badges and Tables: Colors for pending, approved, and cancelled states. Custom list items, print styling overlays, and slide-in toast notifications.

---

## 4. Frontend Interactive Pages

### 📂 [frontend/index.html](file:///c:/Users/haris/OneDrive/Desktop/mansi/frontend/index.html)
* **Purpose**: Landing home page.
* **Logic**: On page load, it checks if a session exists. If logged in, it dynamically replaces "Login/Signup" buttons with a link to the user's dashboard. It also updates the doctors counter dynamically by hitting the public doctors listing API.

### 📂 [frontend/login.html](file:///c:/Users/haris/OneDrive/Desktop/mansi/frontend/login.html)
* **Purpose**: Credentials submission portal.
* **Logic**: Gathers user input, evaluates the selected role (Patient, Doctor, Admin) via custom icon options, sends a `POST /api/auth/login` request, saves session tokens on success, and redirects to the appropriate dashboard.

### 📂 [frontend/signup.html](file:///c:/Users/haris/OneDrive/Desktop/mansi/frontend/signup.html)
* **Purpose**: Registration portal.
* **Logic**: Implements a clean tabbed panel to switch between Patient and Doctor sign-up forms. On submission, it matches passwords, sends a register request, saves session tokens, and redirects immediately.

### 📂 [frontend/patient_dashboard.html](file:///c:/Users/haris/OneDrive/Desktop/mansi/frontend/patient_dashboard.html)
* **Purpose**: Patient dashboard.
* **Logic**: Enforces patient authentication. Standard javascript triggers load details, load approved doctors list, query appointment status history, and retrieve prescriptions. Features a printable PDF prescription preview modal.

### 📂 [frontend/doctor_dashboard.html](file:///c:/Users/haris/OneDrive/Desktop/mansi/frontend/doctor_dashboard.html)
* **Purpose**: Doctor dashboard.
* **Logic**: Enforces doctor authentication. Checks for active profile verification. If pending, it disables standard sidebar navigation and renders an "Awaiting Verification" screen. If active, it provides lists to accept/reject appointments, write prescriptions, and adjust availability slots.

### 📂 [frontend/admin_dashboard.html](file:///c:/Users/haris/OneDrive/Desktop/mansi/frontend/admin_dashboard.html)
* **Purpose**: Admin control center.
* **Logic**: Enforces admin authentication. Populates counters (total doctors, patients, active users, and appointments). Includes control tables to approve doctor registrations, view list directories, cancel bookings, and delete user profiles.
