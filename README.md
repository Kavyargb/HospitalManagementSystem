# 🏥 Hospital Management System (HMS)

A comprehensive, multi-interface Hospital Management System built in **Python** with a **MySQL** backend. The system provides three independent entry points — a **Command-Line Interface (CLI)**, a **Tkinter Desktop GUI**, and a **Flask Web Application** — all sharing the same core business-logic modules and database layer.

---

## 📑 Table of Contents

1. [High-Level Architecture](#-high-level-architecture)
2. [Project Directory Structure](#-project-directory-structure)
3. [Technology Stack & Dependencies](#-technology-stack--dependencies)
4. [Database Layer (`db/`)](#-database-layer-db)
5. [Authentication Module (`auth/`)](#-authentication-module-auth)
6. [Business-Logic Modules (`modules/`)](#-business-logic-modules-modules)
   - [Patients](#1-patients--modulespatientspy)
   - [Doctors](#2-doctors--modulesdoctorspy)
   - [Rooms](#3-rooms--modulesroomspy)
   - [Appointments](#4-appointments--modulesappointmentspy)
   - [Pharmacy](#5-pharmacy--modulespharmacypy)
   - [Lab](#6-lab--moduleslabpy)
   - [Billing](#7-billing--modulesbillingpy)
   - [Staff](#8-staff--modulesstaffpy)
7. [Chemistry Module (`chemistry/`)](#-chemistry-module-chemistry)
8. [Utility Module (`utils/`)](#-utility-module-utils)
9. [Entry Points & Interfaces](#-entry-points--interfaces)
   - [CLI (`main.py`)](#1-command-line-interface--mainpy)
   - [GUI (`gui.py` + `gui_views/`)](#2-desktop-gui--guipy--gui_views)
   - [Web App (`web_app.py` + `templates/`)](#3-web-application--web_apppy--templates)
10. [Mathematical Formulas & Computational Logic](#-mathematical-formulas--computational-logic)
11. [Setup & Installation](#-setup--installation)
12. [Usage Guide](#-usage-guide)
13. [Role-Based Access Control Matrix](#-role-based-access-control-matrix)

---

## 🏗 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        PRESENTATION LAYER                          │
│  ┌─────────────┐   ┌─────────────────┐   ┌─────────────────────┐  │
│  │  CLI (main.py)│   │  GUI (gui.py)   │   │  Web (web_app.py)   │  │
│  │  text menus  │   │  Tkinter/ttk    │   │  Flask + Jinja2     │  │
│  └──────┬───────┘   └──────┬──────────┘   └──────┬──────────────┘  │
│         │                  │                      │                 │
├─────────┼──────────────────┼──────────────────────┼─────────────────┤
│         │         BUSINESS LOGIC LAYER            │                 │
│         ▼                  ▼                      ▼                 │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  modules/  (patients, doctors, appointments, pharmacy,     │    │
│  │            billing, lab, rooms, staff)                      │    │
│  ├─────────────────────────────────────────────────────────────┤    │
│  │  auth/login.py   │  chemistry/   │  utils/ (pdf, validators)│   │
│  └─────────┬────────┴───────┬───────┴──────────┬───────────────┘   │
│            │                │                  │                    │
├────────────┼────────────────┼──────────────────┼────────────────────┤
│            │         DATA ACCESS LAYER         │                    │
│            ▼                ▼                  ▼                    │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  db/connection.py  →  MySQL Server (hms_db)                │    │
│  │  db/schema.sql     →  10 tables with FK constraints        │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

The architecture follows a clean **three-tier pattern**:
- **Presentation Tier** — Three independent front-ends (CLI, GUI, Web) that never contain database queries directly.
- **Business Logic Tier** — Shared Python modules that encapsulate all domain rules, calculations, and data transformations.
- **Data Access Tier** — A single `execute_query()` gateway that manages MySQL connections, parameterised queries, and result formatting.

---

## 📂 Project Directory Structure

```
HospitalManagementSystem/
│
├── main.py                  # CLI entry point (all 5 role menus)
├── gui.py                   # Tkinter GUI entry point (login window)
├── web_app.py               # Flask web application (Admin portal)
├── config.py                # MySQL connection credentials
├── requirements.txt         # Python package dependencies
│
├── auth/
│   └── login.py             # Password hashing, verification, user CRUD
│
├── db/
│   ├── connection.py        # DB connection pool & query executor
│   └── schema.sql           # Complete DDL: 10 tables + seed data
│
├── modules/
│   ├── patients.py          # Patient registration & search
│   ├── doctors.py           # Doctor profile CRUD
│   ├── rooms.py             # Room availability management
│   ├── appointments.py      # Appointment booking & viewing
│   ├── pharmacy.py          # Medicine inventory & dispensing
│   ├── lab.py               # Lab test types, assignment, results
│   ├── billing.py           # Itemised bill generation & payment
│   └── staff.py             # Non-doctor staff account creation
│
├── chemistry/
│   └── molecule_handler.py  # PubChem API + RDKit 2D rendering
│
├── utils/
│   ├── helpers.py           # OS-aware screen clearing
│   ├── validators.py        # Input validation (phone, date, generic)
│   └── pdf_generator.py     # Revenue report PDF via FPDF
│
├── gui_views/
│   ├── main_menu.py         # Post-login role-dispatching window
│   ├── admin_views.py       # Doctor & staff management GUIs
│   └── pharmacist_views.py  # Pharmacy stock & molecule viewer GUI
│
├── templates/               # Jinja2 HTML templates (Flask)
│   ├── base.html            # Sidebar layout + CSS design system
│   ├── login.html           # Standalone login page
│   ├── dashboard.html       # Admin dashboard (stats cards)
│   ├── doctors.html         # Doctor list + add form
│   ├── staff.html           # Staff list + add form
│   └── reports.html         # Paid-bills table + PDF download
│
└── static/
    └── molecule_images/     # Auto-generated 2D molecule PNGs
```

---

## 🔧 Technology Stack & Dependencies

| Package                   | Version | Purpose                                                                 |
|---------------------------|---------|-------------------------------------------------------------------------|
| `mysql-connector-python`  | latest  | Pure-Python MySQL driver; connects via TCP to `localhost:3306`           |
| `bcrypt`                  | latest  | Adaptive password hashing (Blowfish cipher, 2¹² rounds by default)     |
| `rdkit`                   | latest  | Cheminformatics toolkit; SMILES parsing → 2D coordinate generation      |
| `pubchempy`               | latest  | REST wrapper for the PubChem PUG API; resolves drug names → SMILES      |
| `Pillow`                  | latest  | Python Imaging Library fork; used by GUI to render molecule PNG files    |
| `flask` *(implicit)*      | latest  | Micro web framework for the admin portal                                |
| `fpdf` *(implicit)*       | latest  | Lightweight PDF generation library                                      |

Install all explicit dependencies:

```bash
pip install -r requirements.txt
```

For the web application and PDF features you also need:
```bash
pip install flask fpdf
```

---

## 🗄 Database Layer (`db/`)

### `config.py` — Connection Credentials

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'tiger',
    'database': 'hms_db'
}
```

A simple dictionary unpacked with `**DB_CONFIG` into `mysql.connector.connect()`.

---

### `db/connection.py` — Connection Manager & Query Executor

This file provides the **single gateway** to the database used by every module.

#### `get_db_connection()`

Establishes a fresh TCP connection to the MySQL server.

```
Input  : (none — reads DB_CONFIG from config.py)
Output : mysql.connector.connection object | None
```

- Calls `mysql.connector.connect(**DB_CONFIG)`.
- Validates with `connection.is_connected()`.
- Returns `None` on any `mysql.connector.Error`.

#### `execute_query(query, params=None, fetch=None)`

A universal query runner that handles **SELECT**, **INSERT**, **UPDATE**, and **DELETE** statements through a single interface.

```
Input  : query  (str)  — SQL string with %s placeholders
         params (tuple) — Parameter values for safe interpolation
         fetch  (str)  — 'one' | 'all' | None

Output : dict          — if fetch='one'   (single row as dict)
         list[dict]    — if fetch='all'   (list of row-dicts)
         int           — if fetch=None    (lastrowid for INSERT)
         None          — on failure
```

**Execution logic:**

```
1. conn = get_db_connection()
2. cursor = conn.cursor(dictionary=True)     # rows returned as {col: value}
3. cursor.execute(query, params or ())       # parameterised query (SQL-injection safe)
4. if fetch == 'one'  → return cursor.fetchone()
   if fetch == 'all'  → return cursor.fetchall()
   else               → conn.commit(); return cursor.lastrowid
5. finally: cursor.close(); conn.close()
```

> **Design Note:** Each call opens and closes its own connection. This avoids stale-connection bugs and is acceptable for a low-concurrency system. In a production environment, a connection pool (e.g., `mysql.connector.pooling`) would be preferred.

---

### `db/schema.sql` — Database Schema (DDL)

Creates the `hms_db` database and 10 relational tables. The entity-relationship model is shown below:

```
┌──────────┐       ┌──────────┐       ┌──────────────┐
│  users   │──1:1──│ doctors  │──1:N──│ appointments │
│  (auth)  │       │(profile) │       │              │
└──────────┘       └────┬─────┘       └───────┬──────┘
                        │                     │
                   1:N  │                N:1  │
                        ▼                     ▼
                   ┌──────────┐         ┌──────────┐
                   │ patients │◄────────│          │
                   │          │         └──────────┘
                   └──┬──┬──┬─┘
                      │  │  │
            ┌─────────┘  │  └──────────┐
            ▼            ▼             ▼
     ┌────────────┐ ┌──────────┐ ┌───────────────┐
     │medicine_   │ │lab_      │ │   bills       │
     │issued      │ │reports   │ │               │
     └─────┬──────┘ └────┬─────┘ └───────────────┘
           │              │
           ▼              ▼
     ┌──────────┐  ┌──────────┐     ┌──────────┐
     │medicines │  │lab_tests │     │  rooms   │
     └──────────┘  └──────────┘     └──────────┘
```

#### Table Definitions

| # | Table              | Primary Key     | Key Columns & Types                                                                                                    | Foreign Keys                                      |
|---|--------------------|-----------------|------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------|
| 1 | `users`            | `id` INT AI     | `username` VARCHAR(50) UNIQUE, `password_hash` VARCHAR(255), `role` ENUM('Admin','Doctor','Receptionist','Pharmacist','Lab Tech') | —                                                 |
| 2 | `doctors`          | `id` INT AI     | `user_id` INT, `name` VARCHAR(100), `specialization` VARCHAR(100), `contact` VARCHAR(20)                               | `user_id → users(id)` CASCADE                     |
| 3 | `rooms`            | `id` INT AI     | `room_number` VARCHAR(10) UNIQUE, `type` ENUM('General','Private','ICU'), `is_available` BOOL DEFAULT TRUE             | —                                                 |
| 4 | `patients`         | `id` INT AI     | `name`, `age`, `gender` ENUM, `address`, `contact`, `admission_date` DATETIME, `discharge_date` DATETIME NULL          | `doctor_id → doctors(id)`, `room_id → rooms(id)`  |
| 5 | `appointments`     | `id` INT AI     | `appointment_time` DATETIME, `status` ENUM('Scheduled','Completed','Canceled') DEFAULT 'Scheduled'                     | `patient_id → patients(id)` CASCADE, `doctor_id → doctors(id)` CASCADE |
| 6 | `medicines`        | `id` INT AI     | `name` VARCHAR(100) UNIQUE, `smiles` TEXT, `image_path` VARCHAR(255), `quantity` INT, `expiry_date` DATE, `price` DECIMAL(10,2) | —                                                 |
| 7 | `medicine_issued`  | `id` INT AI     | `quantity` INT, `issue_date` DATETIME                                                                                  | `patient_id → patients(id)`, `medicine_id → medicines(id)` |
| 8 | `lab_tests`        | `id` INT AI     | `name` VARCHAR(100) UNIQUE, `price` DECIMAL(10,2)                                                                      | —                                                 |
| 9 | `lab_reports`      | `id` INT AI     | `result` TEXT NULL, `report_date` DATETIME                                                                             | `patient_id → patients(id)`, `test_id → lab_tests(id)` |
| 10| `bills`            | `id` INT AI     | `total_amount` DECIMAL(10,2), `payment_status` ENUM('Paid','Unpaid') DEFAULT 'Unpaid', `bill_date` DATETIME            | `patient_id → patients(id)`                       |

> `AI` = `AUTO_INCREMENT`. All `DECIMAL(10, 2)` columns store values up to **99,999,999.99** with exact cent precision — critical for financial integrity.

---

## 🔐 Authentication Module (`auth/`)

### `auth/login.py`

Handles all authentication concerns: password hashing, credential verification, and user creation.

#### `hash_password(password: str) → str`

Uses the **bcrypt** adaptive hashing algorithm.

**Mathematical basis — Blowfish key schedule (bcrypt):**

```
salt      = random(128 bits)
cost      = 12                     (default gensalt rounds, i.e., 2¹² = 4096 iterations)
hash      = bcrypt(password, salt, cost)

The cost parameter means the Blowfish key schedule is applied 2^cost times:

    iterations = 2^cost = 2^12 = 4,096

The resulting hash string has the format:
    $2b$12$<22-char-salt><31-char-hash>

Where:
    $2b$   → bcrypt version identifier
    $12$   → cost factor (log₂ of iteration count)
```

This makes brute-force attacks computationally expensive:

```
Time per hash ≈ 2^cost × T_blowfish
For cost=12:  ≈ 4,096 × T_blowfish ≈ 200–300 ms on modern hardware
```

**Code flow:**
```python
salt = bcrypt.gensalt()                               # generates random 128-bit salt
hashed = bcrypt.hashpw(password.encode('utf-8'), salt) # applies Blowfish cipher
return hashed.decode('utf-8')                          # stores as string in MySQL
```

#### `check_password(plain_password: str, hashed_password: str) → bool`

Extracts the salt from the stored hash and re-hashes the candidate password:

```
stored_hash = "$2b$12$<salt><hash>"
candidate   = bcrypt.hashpw(plain_password, stored_hash)
result      = (candidate == stored_hash)
```

**Constant-time comparison** is used internally by bcrypt to prevent timing attacks.

#### `login() → dict | None`

Interactive CLI login flow:

```
1. Prompt username (via input())
2. Prompt password (via getpass.getpass() — hides terminal echo)
3. SQL: SELECT id, username, password_hash, role FROM users WHERE username = %s
4. if user exists AND check_password(input, stored_hash):
       return {'id': ..., 'username': ..., 'password_hash': ..., 'role': ...}
   else:
       return None
```

#### `check_credentials(username, password) → dict | None`

Non-interactive version of `login()` — same logic but without `input()` calls. Used by the GUI (`gui.py`) and the Web App (`web_app.py`).

#### `create_user(username, password, role) → int | None`

```
1. Validate role ∈ {'Admin', 'Doctor', 'Receptionist', 'Pharmacist', 'Lab Tech'}
2. password_hash = hash_password(password)
3. SQL: INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)
4. Return lastrowid (the new user's ID)
```

The `UNIQUE` constraint on `users.username` ensures no duplicates — a `mysql.connector.Error` is caught and reported.

---

## 📦 Business-Logic Modules (`modules/`)

### 1. Patients — `modules/patients.py`

#### `register_patient()`

Registers a new in-patient through a 5-step interactive process:

```
Step 1: Collect personal info → (name, age, gender, address, contact)
Step 2: list_all_doctors()    → display available doctors, input doctor_id
Step 3: list_available_rooms()→ display free rooms, input room_id
Step 4: INSERT INTO patients (..., admission_date=NOW())
Step 5: UPDATE rooms SET is_available=FALSE WHERE id=room_id
```

**Room allocation is atomic in intent** — after a patient is assigned a room, that room is immediately marked unavailable to prevent double-booking.

#### `search_patient_by_id() → dict | None`

```
Input : patient_id (prompted via input())
SQL   : SELECT * FROM patients WHERE id = %s
Output: dict with all patient columns, or None
Display: Iterates over dict keys, converts snake_case → Title Case
```

---

### 2. Doctors — `modules/doctors.py`

#### `add_doctor()` (CLI-interactive)

A **two-phase transactional operation**:

```
Phase 1: Create user account
    SQL: INSERT INTO users (username, password_hash, role='Doctor') VALUES (...)
    → user_id = lastrowid

Phase 2: Create doctor profile
    SQL: INSERT INTO doctors (user_id, name, specialization, contact) VALUES (...)
```

> ⚠️ **Note:** These two INSERTs are not wrapped in a database transaction. If Phase 2 fails, an orphan user record remains. The code comments acknowledge this limitation.

#### `create_doctor_profile(name, spec, contact, username, password) → int | None`

Non-interactive backend version of `add_doctor()`, used by the GUI and Web App. Same two-phase logic, returns the new `doctor.id` on success.

#### `list_all_doctors() → list[dict] | None`

```
SQL: SELECT d.id, d.name, d.specialization, d.contact, u.username
     FROM doctors d JOIN users u ON d.user_id = u.id
```

Returns the result set and also pretty-prints it in a formatted table (for CLI use).

#### `get_doctor_id_from_user_id(user_id) → int | None`

Resolves a `users.id` to a `doctors.id`:

```
SQL: SELECT id FROM doctors WHERE user_id = %s
```

Used when a logged-in Doctor needs to view their own appointments — the session has `user.id`, but appointments reference `doctor.id`.

---

### 3. Rooms — `modules/rooms.py`

#### `list_available_rooms() → list[dict] | None`

```
SQL: SELECT id, room_number, type FROM rooms WHERE is_available = TRUE
```

Filters to only rooms where the boolean `is_available` flag is `TRUE`.

#### `update_room_status(room_id, is_available: bool)`

```
SQL: UPDATE rooms SET is_available = %s WHERE id = %s
```

Called by `register_patient()` to mark rooms as occupied (`False`) and could be called on discharge to free them (`True`).

---

### 4. Appointments — `modules/appointments.py`

#### `book_appointment()`

```
1. search_patient_by_id()  → get patient dict
2. list_all_doctors()      → display doctors
3. Input doctor_id, datetime string (format: "YYYY-MM-DD HH:MM")
4. Parse datetime: datetime.strptime(date_str, "%Y-%m-%d %H:%M")
5. SQL: INSERT INTO appointments (patient_id, doctor_id, appointment_time) VALUES (...)
   → status defaults to 'Scheduled' (schema default)
```

#### `view_doctor_appointments(user: dict)`

Shows only the currently logged-in doctor's **scheduled** appointments:

```
1. doctor_id = get_doctor_id_from_user_id(user['id'])
2. SQL: SELECT a.id, p.name AS patient_name, a.appointment_time, a.status
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        WHERE a.doctor_id = %s AND a.status = 'Scheduled'
        ORDER BY a.appointment_time
```

---

### 5. Pharmacy — `modules/pharmacy.py`

The most feature-rich module, integrating chemistry APIs for drug metadata.

#### `add_medicine()` (CLI-interactive)

```
1. Collect: name, quantity, price, expiry_date
2. Chemistry integration:
     (smiles, image_path) = fetch_and_draw_molecule(name)
     → Queries PubChem for the drug's SMILES string
     → Renders a 2D molecular structure PNG via RDKit
3. SQL: INSERT INTO medicines (name, smiles, image_path, quantity, expiry_date, price)
        VALUES (%s, %s, %s, %s, %s, %s)
```

If the PubChem lookup fails, the user is prompted whether to add the medicine without chemical data.

#### `add_medicine_to_db(name, qty, price, expiry_date_str) → bool`

Non-interactive backend version of `add_medicine()`. Used by the GUI (which runs this in a background thread to avoid freezing the UI during the PubChem API call).

#### `view_medicine_stock()`

```
SQL: SELECT id, name, quantity, price, expiry_date, image_path
     FROM medicines ORDER BY name
```

Displays a formatted table of all medicines in inventory.

#### `issue_medicine()`

Dispenses medicine to a patient with **stock validation**:

```
1. Display current stock (view_medicine_stock())
2. Input: patient_id, medicine_id, quantity_to_issue
3. Validation:
     SQL: SELECT name, quantity FROM medicines WHERE id = %s
     if medicine.quantity < quantity_to_issue:
         ERROR "Insufficient stock"
         return
4. Stock update:
     SQL: UPDATE medicines SET quantity = quantity - %s WHERE id = %s
5. Transaction record:
     SQL: INSERT INTO medicine_issued (patient_id, medicine_id, quantity, issue_date)
          VALUES (%s, %s, %s, NOW())
```

**Stock arithmetic:**

```
new_stock = current_stock − quantity_issued

Constraint: new_stock ≥ 0  (enforced by application-level check)
```

#### `view_molecule_image()`

Opens a medicine's 2D molecular structure image in the system's default viewer:

```
1. view_medicine_stock()             → show all medicines
2. Input medicine_id
3. SQL: SELECT name, image_path FROM medicines WHERE id = %s
4. Validate: image_path exists AND os.path.exists(image_path)
5. webbrowser.open(os.path.abspath(image_path))  → opens in default app
```

---

### 6. Lab — `modules/lab.py`

#### `add_lab_test()`

Defines a new lab test type:

```
SQL: INSERT INTO lab_tests (name, price) VALUES (%s, %s)
```

#### `list_all_lab_tests() → list[dict] | None`

```
SQL: SELECT id, name, price FROM lab_tests
```

#### `assign_test_to_patient()`

Doctor assigns a test to a patient:

```
1. search_patient_by_id() → patient
2. list_all_lab_tests()   → available tests
3. Validate test_id ∈ {t['id'] for t in available_tests}
4. SQL: INSERT INTO lab_reports (patient_id, test_id, report_date)
        VALUES (%s, %s, NOW())
   → result field is NULL (pending)
```

#### `input_test_result()`

Lab technician enters results for pending tests:

```
1. SQL: SELECT lr.id, p.name, lt.name
        FROM lab_reports lr
        JOIN patients p ON lr.patient_id = p.id
        JOIN lab_tests lt ON lr.test_id = lt.id
        WHERE lr.result IS NULL          ← only pending tests
2. Input: report_id, result text
3. SQL: UPDATE lab_reports SET result = %s WHERE id = %s
```

---

### 7. Billing — `modules/billing.py`

The billing module is the most mathematically intensive part of the system.

#### Constants

```python
ROOM_PRICES = {
    'General': 100.00,   # $/day
    'Private': 300.00,   # $/day
    'ICU':     500.00    # $/day
}
CONSULTATION_FEE = 150.00   # $ per appointment
```

#### `generate_patient_bill()`

Generates a **fully itemised bill** by aggregating four cost categories:

---

**Category 1: Room Charges**

```
SQL: SELECT type FROM rooms WHERE id = patient.room_id

discharge_date = patient.discharge_date  OR  NOW()  (if still admitted)

days_stayed = (discharge_date − admission_date).days + 1
```

> The `+1` ensures that a same-day admission/discharge counts as 1 day.

```
Mathematical formula:

    C_room = D × P_room

Where:
    D       = days_stayed = ⌊(t_discharge − t_admission) / 86400⌋ + 1
    P_room  = ROOM_PRICES[room_type]  ∈ {100, 300, 500}
    C_room  = total room charge ($)

Example: Patient in ICU for 3 days:
    C_room = 3 × 500 = $1,500.00
```

---

**Category 2: Consultation Fees**

```
SQL: SELECT COUNT(*) as count FROM appointments WHERE patient_id = %s

Mathematical formula:

    C_consult = N_appointments × F_consultation

Where:
    N_appointments   = number of appointments (all statuses)
    F_consultation   = $150.00 (fixed per consultation)

Example: 4 consultations:
    C_consult = 4 × 150 = $600.00
```

---

**Category 3: Lab Test Charges**

```
SQL: SELECT lt.name, lt.price
     FROM lab_reports lr JOIN lab_tests lt ON lr.test_id = lt.id
     WHERE lr.patient_id = %s

Mathematical formula:

    C_lab = Σ(i=1 to N) P_test_i

Where:
    N         = number of lab reports for this patient
    P_test_i  = price of the i-th lab test

This is a simple summation of all test prices:
    C_lab = P₁ + P₂ + ... + Pₙ

Example: CBC ($50) + X-Ray ($200) + MRI ($1500):
    C_lab = 50 + 200 + 1500 = $1,750.00
```

---

**Category 4: Pharmacy (Medicine) Charges**

```
SQL: SELECT m.name, mi.quantity, m.price
     FROM medicine_issued mi JOIN medicines m ON mi.medicine_id = m.id
     WHERE mi.patient_id = %s

Mathematical formula:

    C_pharmacy = Σ(i=1 to M) (Q_i × P_i)

Where:
    M    = number of distinct medicine issuances
    Q_i  = quantity of medicine i issued
    P_i  = unit price of medicine i

Example: 10 units of Aspirin ($2.50) + 5 units of Amoxicillin ($8.00):
    C_pharmacy = (10 × 2.50) + (5 × 8.00) = 25.00 + 40.00 = $65.00
```

---

**Grand Total Calculation**

```
Mathematical formula:

    T = C_room + C_consult + C_lab + C_pharmacy

    T = (D × P_room) + (N_appt × F_consult) + Σ P_test_i + Σ (Q_j × P_med_j)

Where T is the total bill amount stored in the bills table.
```

**Full expanded formula:**

```
T = [ (⌊(t_discharge − t_admission)/86400⌋ + 1) × P_room ]
  + [ N_appointments × 150 ]
  + [ Σ(i=1..N_tests) P_test_i ]
  + [ Σ(j=1..M_meds) Q_j × P_med_j ]
```

After display, the bill is optionally saved:

```
SQL: INSERT INTO bills (patient_id, total_amount, bill_date)
     VALUES (%s, T, NOW())
→ payment_status defaults to 'Unpaid'
```

#### `update_payment_status()`

```
1. SQL: SELECT b.id, p.name, b.total_amount, b.bill_date
        FROM bills b JOIN patients p ON b.patient_id = p.id
        WHERE b.payment_status = 'Unpaid'
2. Input bill_id
3. SQL: UPDATE bills SET payment_status = 'Paid' WHERE id = %s
```

---

### 8. Staff — `modules/staff.py`

#### `create_staff_member()`

Admin-only function to create non-doctor staff accounts:

```
Allowed roles: {'Receptionist', 'Pharmacist', 'Lab Tech'}
   (Admins and Doctors are created through separate workflows)

1. Display numbered role menu
2. Input choice_index → selected_role = creatable_roles[choice - 1]
3. Input username, password
4. Validate non-empty strings
5. Call create_user(username, password, selected_role)
```

---

## ⚗ Chemistry Module (`chemistry/`)

### `chemistry/molecule_handler.py`

Integrates **PubChem** (NIH chemical database) and **RDKit** (cheminformatics library) to fetch and visualise molecular structures of medicines.

#### `fetch_and_draw_molecule(drug_name: str) → tuple[str|None, str|None]`

**Pipeline:**

```
Step 1: PubChem API Lookup
    compounds = pcp.get_compounds(drug_name, 'name')
    → REST call to: https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{drug_name}/JSON
    → Returns list of CompoundObjects

Step 2: Extract SMILES
    smiles = compounds[0].canonical_smiles
    
    SMILES (Simplified Molecular-Input Line-Entry System) is a linear notation
    for chemical structures. Example:
        Aspirin → "CC(=O)OC1=CC=CC=C1C(=O)O"
        Caffeine → "CN1C=NC2=C1C(=O)N(C(=O)N2C)C"

Step 3: RDKit Molecule Object
    mol = Chem.MolFromSmiles(smiles)
    → Parses SMILES into a molecular graph:
       G = (V, E) where:
         V = set of atoms (vertices)
         E = set of bonds (edges with bond-order weights)

Step 4: 2D Coordinate Generation & Rendering
    Draw.MolToFile(mol, image_path, size=(300, 300))
    → Uses the RDKit 2D coordinate generator (CoordGen algorithm)
    → Produces a 300×300 pixel PNG image
    → Saved to: static/molecule_images/{drug_name}.png

Output: (smiles_string, image_file_path)
```

**SMILES mathematical representation:**

```
A SMILES string encodes a molecular graph G = (V, E):
  - Atoms → uppercase letters (C, N, O, S, etc.)
  - Single bonds → implicit (adjacent atoms)
  - Double bonds → '='
  - Triple bonds → '#'
  - Branches → parentheses '()'
  - Rings → digit pairs marking ring-closure

Example: Aspirin  C₉H₈O₄
  SMILES: CC(=O)OC1=CC=CC=C1C(=O)O
  
  Molecular formula extraction:
    |V| = 13 heavy atoms (9C + 4O)
    |E| = 13 bonds (10 single + 2 double + 1 aromatic ring)
```

---

## 🛠 Utility Module (`utils/`)

### `utils/helpers.py`

#### `clear_screen()`

OS-aware terminal clearing:

```python
if platform.system() == "Windows":
    os.system('cls')       # Windows command
else:
    os.system('clear')     # Unix/macOS command
```

---

### `utils/validators.py`

#### `is_valid_phone(phone: str) → bool`

```
Mathematical constraint:
    phone.isdigit() ∧ 7 ≤ len(phone) ≤ 15

This enforces:
    phone ∈ {s ∈ [0-9]* | 7 ≤ |s| ≤ 15}
```

Accepts international numbers (7–15 digits per ITU-T E.164 standard, which allows max 15 digits).

#### `is_valid_date(date_str, fmt="%Y-%m-%d") → bool`

Attempts `datetime.strptime(date_str, fmt)`. Returns `True` if parsing succeeds, `False` on `ValueError`. This validates:
- Correct format (e.g., `2025-12-31`)
- Valid calendar date (rejects `2025-02-30`)

#### `get_validated_input(prompt, validation_func, error_message) → str`

A **generic input loop** using higher-order function composition:

```
repeat:
    user_input = input(prompt)
    if validation_func(user_input):   # accepts any callable returning bool
        return user_input
    else:
        print(error_message)
```

This implements the mathematical concept of a **fixpoint iteration** on user input — looping until the validation predicate is satisfied.

---

### `utils/pdf_generator.py`

#### `generate_revenue_report() → str | None`

Generates a formatted PDF revenue report of all paid bills.

```
Step 1: Data Query
    SQL: SELECT b.id, p.name, b.total_amount, b.bill_date
         FROM bills b JOIN patients p ON b.patient_id = p.id
         WHERE b.payment_status = 'Paid'
         ORDER BY b.bill_date

Step 2: PDF Construction (FPDF library)
    - Page: A4 portrait (210 × 297 mm)
    - Title: "Hospital Revenue Report" (Arial Bold 16pt, centered)
    - Subtitle: "Generated on: YYYY-MM-DD HH:MM"
    - Table header: [Bill ID | Patient Name | Amount Paid | Date]
    - Table rows: one per paid bill
    
Step 3: Revenue Summation
    total_revenue = Σ(i=1 to N) bill_i.total_amount

    Mathematical formula:
        R = Σ(i=1..N) T_i
    Where:
        R   = total revenue
        N   = number of paid bills
        T_i = total_amount of the i-th paid bill

Step 4: Save
    Filename: reports/revenue_report_YYYYMMDD.pdf
    Returns: absolute file path string
```

---

## 🖥 Entry Points & Interfaces

### 1. Command-Line Interface — `main.py`

The CLI provides **five role-specific menus**, each accessible after login:

```
main()
 ├── Verify DB connection
 ├── Login loop
 │    ├── auth.login.login() → user dict
 │    └── Role dispatch:
 │         ├── 'Admin'        → admin_menu()
 │         ├── 'Doctor'       → doctor_menu()
 │         ├── 'Receptionist' → receptionist_menu()
 │         ├── 'Pharmacist'   → pharmacist_menu()
 │         └── 'Lab Tech'     → lab_tech_menu()
 └── KeyboardInterrupt handler → graceful exit
```

#### Menu Capabilities by Role

| Menu Item              | Admin | Doctor | Receptionist | Pharmacist | Lab Tech |
|------------------------|:-----:|:------:|:------------:|:----------:|:--------:|
| Manage Doctors         |  ✅   |        |              |            |          |
| Create Staff Account   |  ✅   |        |              |            |          |
| Add Lab Test Type      |  ✅   |        |              |            |    ✅    |
| Generate Revenue PDF   |  ✅   |        |              |            |          |
| View My Appointments   |       |   ✅   |              |            |          |
| Search Patient by ID   |       |   ✅   |      ✅      |            |          |
| Assign Lab Test        |       |   ✅   |              |            |          |
| Register Patient       |       |        |      ✅      |            |          |
| Book Appointment       |       |        |      ✅      |            |          |
| Generate Patient Bill  |       |        |      ✅      |            |          |
| Update Payment Status  |       |        |      ✅      |            |          |
| Add Medicine to Stock  |       |        |              |     ✅     |          |
| View Medicine Inventory|       |        |              |     ✅     |          |
| Issue Medicine         |       |        |              |     ✅     |          |
| View Molecule Structure|       |        |              |     ✅     |          |
| Input Lab Test Result  |       |        |              |            |    ✅    |

---

### 2. Desktop GUI — `gui.py` + `gui_views/`

Built with Python's standard **Tkinter** library and the themed **ttk** widget set.

#### `gui.py` — Application Root

```
class App(tk.Tk):
    __init__:
        window title = "HMS Login"
        geometry = 300×150 px
    
    create_login_widgets():
        grid layout with:
            Row 0: Label("Username") + Entry
            Row 1: Label("Password") + Entry(show="*")
            Row 2: Button("Login") → handle_login()
    
    handle_login():
        user = check_credentials(username, password)
        if user:
            self.withdraw()           # hide login window
            MainMenu(self, user)      # open role-based menu
        else:
            messagebox.showerror()    # show error dialog
```

#### `gui_views/main_menu.py` — Role Dispatcher

```
class MainMenu(tk.Toplevel):
    Dynamically renders buttons based on user.role:
    
    if role == 'Admin':
        → "Manage Doctors"  → open_doctor_management_window()
        → "Manage Staff"    → open_staff_management_window()
    
    if role == 'Pharmacist':
        → "Manage Pharmacy" → open_pharmacy_management_window()
    
    Always shows: "Logout" → self.destroy()
```

#### `gui_views/admin_views.py` — Admin Windows

**Doctor Management Window:**
- `Treeview` widget displays all doctors in a 5-column table
- "Add New Doctor" button opens a modal form with 5 fields
- `populate_doctors()` refreshes the Treeview from the database
- `save_doctor()` calls `doctors.create_doctor_profile()` (non-interactive)

**Staff Management Window:**
- `Treeview` with columns: ID, Username, Role
- Filters to non-Admin, non-Doctor users
- Add Staff form with a `Combobox` for role selection (Receptionist, Pharmacist, Lab Tech)

#### `gui_views/pharmacist_views.py` — Pharmacy Window

```
Layout: Split-pane
    Left:  Treeview (medicine list: ID, Name, Quantity, Price)
    Right: Label (molecule image display, 300×300 px)

Event binding:
    tree.bind('<<TreeviewSelect>>', show_molecule)
    → When a medicine is selected, its molecule PNG is loaded via PIL
       and displayed using ImageTk.PhotoImage

Add Medicine Form:
    → Uses threading.Thread + queue.Queue pattern
    → Reason: fetch_and_draw_molecule() makes a network API call to PubChem
      which can take several seconds. Running it on the main thread would
      freeze the Tkinter event loop.
    
    Thread architecture:
        Main Thread:         Background Thread:
        save_medicine()      worker_thread_task()
          │                    │
          ├─ disable button    ├─ pharmacy.add_medicine_to_db()
          ├─ start thread ─────┤   ├─ fetch_and_draw_molecule()
          ├─ start polling     │   └─ SQL INSERT
          │                    └─ result_queue.put(success)
          ▼
        process_queue() (called every 100ms via form.after())
          ├─ if result ready → show success/error dialog
          └─ else → schedule another check in 100ms
```

---

### 3. Web Application — `web_app.py` + `templates/`

A **Flask**-based admin portal providing CRUD operations through a browser interface.

#### `web_app.py` — Flask Server

**Configuration:**
```python
app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_super_secret_key_change_this_in_production'
```

**Authentication Decorator:**
```python
@login_required   # Custom decorator
def decorated_function(*args, **kwargs):
    if 'user' not in session or session['user']['role'] != 'Admin':
        flash("Must be Admin", "error")
        return redirect(url_for('login'))
    return f(*args, **kwargs)
```

This restricts the entire web portal to Admin users only.

**Routes:**

| Route               | Methods    | Auth     | Description                                      |
|----------------------|-----------|----------|--------------------------------------------------|
| `/login`            | GET, POST  | Public   | Login form; validates via `check_credentials()`  |
| `/logout`           | GET        | Public   | Clears session, redirects to login               |
| `/` (dashboard)     | GET        | Admin    | Shows doctor count + patient count               |
| `/doctors`          | GET, POST  | Admin    | List doctors; POST adds new doctor               |
| `/staff`            | GET, POST  | Admin    | List staff; POST creates new staff member        |
| `/reports`          | GET        | Admin    | Displays all paid bills in a table               |
| `/download/report`  | GET        | Admin    | Generates PDF and sends as file download         |

**Dashboard Statistics Queries:**
```sql
SELECT COUNT(*) as count FROM doctors   → doctors_count
SELECT COUNT(*) as count FROM patients  → patients_count
```

#### Templates — Jinja2 HTML

**`base.html`** — Layout foundation:
- CSS Grid layout: `grid-template-columns: 260px 1fr`
- Dark sidebar (`#111827`) with navigation links + Font Awesome icons
- Active link highlighting via `request.endpoint` comparison
- Flash message rendering with color-coded categories (success=green, error=red)
- Design system using CSS custom properties (`:root` variables)

**`login.html`** — Standalone page (does not extend `base.html`):
- Centered card layout with box shadow
- Google Fonts (Inter) integration
- Flash messages for login errors

**`dashboard.html`**, **`doctors.html`**, **`staff.html`**, **`reports.html`** — All extend `base.html` using Jinja2 `{% extends %}` / `{% block %}` inheritance.

---

## 📐 Mathematical Formulas & Computational Logic

### Summary of All Formulas

#### 1. Password Hashing (bcrypt)

```
H(p) = bcrypt(p, salt, 2^cost)

Where:
    p     = plaintext password (UTF-8 encoded)
    salt  = cryptographically random 128-bit value
    cost  = 12 (default)
    2^12  = 4,096 iterations of Blowfish key schedule
```

#### 2. Room Charge Calculation

```
C_room = D × P

Where:
    D = ⌊(t_discharge − t_admission) / 86400⌋ + 1     [days]
    P ∈ {100, 300, 500}                                  [$/day]
```

#### 3. Consultation Fee Calculation

```
C_consult = N × F

Where:
    N = COUNT(*) FROM appointments WHERE patient_id = pid
    F = 150.00                                            [$/visit]
```

#### 4. Lab Charges

```
C_lab = Σ(i=1..n) P_i

Where:
    P_i = lab_tests.price for the i-th test performed
```

#### 5. Pharmacy Charges

```
C_pharmacy = Σ(j=1..m) (Q_j × P_j)

Where:
    Q_j = medicine_issued.quantity
    P_j = medicines.price
```

#### 6. Grand Total Bill

```
T = C_room + C_consult + C_lab + C_pharmacy

T = [D × P_room] + [N_appt × 150] + [Σ P_test_i] + [Σ (Q_j × P_med_j)]
```

#### 7. Total Hospital Revenue

```
R = Σ(k=1..K) T_k

Where:
    K   = number of bills WHERE payment_status = 'Paid'
    T_k = bills.total_amount for the k-th paid bill
```

#### 8. Stock Deduction (Pharmacy Dispensing)

```
S_new = S_old − Q_issued

Constraint: S_new ≥ 0
            ⟺ S_old ≥ Q_issued    (validated before UPDATE)
```

#### 9. Phone Number Validation

```
Valid(phone) = isDigit(phone) ∧ (7 ≤ |phone| ≤ 15)

Where |phone| denotes the string length.
Per ITU-T E.164: max 15 digits for international numbers.
```

#### 10. SMILES Molecular Graph

```
G = (V, E)

V = {atoms}        — vertices representing chemical elements
E = {bonds}        — edges with weights:
                        1 = single bond
                        2 = double bond
                        3 = triple bond
                        1.5 = aromatic bond
```

---

## 🚀 Setup & Installation

### Prerequisites

- **Python 3.8+**
- **MySQL Server 5.7+** (running on `localhost:3306`)
- **pip** (Python package manager)

### Step-by-Step

```bash
# 1. Clone the repository
git clone https://github.com/Kavyargb/HospitalManagementSystem.git
cd HospitalManagementSystem

# 2. Install Python dependencies
pip install -r requirements.txt
pip install flask fpdf      # additional dependencies

# 3. Configure database credentials
#    Edit config.py with your MySQL username/password:
#    DB_CONFIG = {
#        'host': 'localhost',
#        'user': 'root',
#        'password': 'your_password',
#        'database': 'hms_db'
#    }

# 4. Create the database schema
#    Open MySQL client and execute:
mysql -u root -p < db/schema.sql

# 5. Create the initial Admin user
python -c "from auth.login import create_user; create_user('admin', 'admin123', 'Admin')"
```

---

## 📖 Usage Guide

### Run the CLI Application
```bash
python main.py
```
Login with your admin credentials. The system presents a role-appropriate menu.

### Run the Desktop GUI
```bash
python gui.py
```
A login window appears. After authentication, a role-specific main menu opens.

### Run the Web Application
```bash
python web_app.py
```
Navigate to `http://127.0.0.1:5000/login` in your browser. Only Admin accounts can access the web portal.

---

## 🔒 Role-Based Access Control Matrix

```
┌─────────────────────┬───────┬────────┬──────────────┬────────────┬──────────┐
│   Capability        │ Admin │ Doctor │ Receptionist │ Pharmacist │ Lab Tech │
├─────────────────────┼───────┼────────┼──────────────┼────────────┼──────────┤
│ Create staff/doctors│   ✅  │        │              │            │          │
│ Generate PDF reports│   ✅  │        │              │            │          │
│ View own appts      │       │   ✅   │              │            │          │
│ Assign lab tests    │       │   ✅   │              │            │          │
│ Search patients     │       │   ✅   │      ✅      │            │          │
│ Register patients   │       │        │      ✅      │            │          │
│ Book appointments   │       │        │      ✅      │            │          │
│ Generate/pay bills  │       │        │      ✅      │            │          │
│ Manage medicines    │       │        │              │     ✅     │          │
│ Issue medicines     │       │        │              │     ✅     │          │
│ View molecules      │       │        │              │     ✅     │          │
│ Input test results  │       │        │              │            │    ✅    │
│ Add lab test types  │   ✅  │        │              │            │    ✅    │
│ Web portal access   │   ✅  │        │              │            │          │
│ GUI access          │   ✅  │        │              │     ✅     │          │
└─────────────────────┴───────┴────────┴──────────────┴────────────┴──────────┘
```

---

## 📄 License

This project is developed for educational purposes.

---

> **Built with** 🐍 Python · 🐬 MySQL · ⚗️ RDKit · 🌐 Flask · 🖥️ Tkinter