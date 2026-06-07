# 🏥 Hospital Management System (HMS)

A comprehensive, multi-interface Hospital Management System built in **Python** with support for both a **MySQL** server and a transparent local **SQLite** fallback. The system provides three independent presentation interfaces — a **Command-Line Interface (CLI)**, a **Tkinter Desktop GUI**, and a premium **Flask Web Application** — all sharing the same core business-logic modules and database translation layer.

---

## 📑 Table of Contents

1. [High-Level Architecture](#-high-level-architecture)
2. [Project Directory Structure](#-project-directory-structure)
3. [Technology Stack & Dependencies](#-technology-stack--dependencies)
4. [Database Layer & Fallback Mechanics (`db/`)](#-database-layer--fallback-mechanics-db)
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
12. [Diagnostics & Verification](#-diagnostics--verification)
13. [Usage Guide](#-usage-guide)
14. [Role-Based Access Control Matrix](#-role-based-access-control-matrix)

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
│         ▼                  ▼                      ▼                 │
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
│  │                     db/connection.py                        │    │
│  │          ┌───────────────────┴───────────────────┐          │    │
│  │          ▼ (Primary)                             ▼ (Fallback)│    │
│  │  MySQL Server (hms_db)                SQLite File (db/hms.db)│    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

The architecture follows a clean **three-tier pattern**:
- **Presentation Tier** — Three independent front-ends (CLI, GUI, Web Portal) that route operations to shared core business logic modules.
- **Business Logic Tier** — Shared Python modules that encapsulate domain rules, invoice aggregation formulas, validations, and chemistry API pipelines.
- **Data Access Tier** — An abstract `execute_query()` wrapper in `db/connection.py` that handles MySQL connections and automatically falls back to SQLite, parsing SQL commands dynamically to support SQLite specifications.

---

## 📂 Project Directory Structure

```
HospitalManagementSystem/
│
├── main.py                  # CLI entry point (all 5 role menus)
├── gui.py                   # Tkinter GUI entry point (login window)
├── web_app.py               # Flask web application (SaaS landing + Multi-role portal)
├── config.py                # MySQL connection credentials configuration
├── requirements.txt         # Python package dependencies
├── test_app.py              # Diagnostic test suite (verifies DB, seeding & APIs)
│
├── auth/
│   └── login.py             # Password hashing, verification, user CRUD
│
├── db/
│   ├── connection.py        # Dual-engine connection pool & dynamic SQL translator
│   ├── schema.sql           # Complete MySQL DDL: 10 tables + initial schema seeds
│   └── hms.db               # Local SQLite database (auto-generated on MySQL fallback)
│
├── modules/
│   ├── patients.py          # Patient registration & details lookup
│   ├── doctors.py           # Doctor profile CRUD and registration maps
│   ├── rooms.py             # Room availability and occupancy management
│   ├── appointments.py      # Appointment booking, calendar, & viewing
│   ├── pharmacy.py          # Medicine inventory, pricing & dispensing records
│   ├── lab.py               # Lab test types, order assignment, & result logging
│   ├── billing.py           # Multi-category invoice math & payment logs
│   └── staff.py             # Staff account creation utilities
│
├── chemistry/
│   └── molecule_handler.py  # PubChem API + RDKit 2D rendering pipeline
│
├── utils/
│   ├── helpers.py           # OS-aware terminal screens clear commands
│   ├── validators.py        # Input verification (phone numbers, dates, inputs)
│   └── pdf_generator.py     # Revenue invoice PDF generation via FPDF
│
├── gui_views/
│   ├── main_menu.py         # Post-login dispatching Tkinter frames
│   ├── admin_views.py       # Doctor & staff account administration UIs
│   └── pharmacist_views.py  # Pharmacy stock treeviews & chemistry renderer GUIs
│
├── templates/               # Jinja2 HTML templates (Flask Portal)
│   ├── base.html            # Main viewport framework (sidebar nav + styling tokens)
│   ├── landing.html         # SaaS product introduction & pricing marketing page
│   ├── register.html        # Public registration form (with dynamic doctor inputs)
│   ├── login.html           # Unified credentials authorization window
│   ├── dashboard.html       # Role-adaptive workspace dashboard panels
│   ├── doctors.html         # Administrator's clinical staff directory
│   ├── staff.html           # Administrator's general staff account list
│   └── reports.html         # Financial statements list with PDF exporter
│
└── static/
    ├── css/
    │   └── style.css        # Core custom stylesheet (Outfit typography, dark UI themes)
    └── molecule_images/     # Generated 2D molecular structures (.png)
```

---

## 🔧 Technology Stack & Dependencies

| Package                   | Version | Purpose                                                                 |
|---------------------------|---------|-------------------------------------------------------------------------|
| `mysql-connector-python`  | latest  | Pure-Python MySQL driver; connects via TCP to target servers.             |
| `sqlite3`                 | built-in| Standard library fallback module; provides zero-configuration local database support. |
| `bcrypt`                  | latest  | Adaptive password hashing (Blowfish cipher, 2¹² rounds by default).     |
| `rdkit`                   | latest  | Cheminformatics toolkit; SMILES parsing → 2D coordinate generation.     |
| `pubchempy`               | latest  | REST wrapper for PubChem PUG API; resolves drug names → SMILES.        |
| `Pillow`                  | latest  | Image loading and rendering library; displays chemical graphics.        |
| `flask`                   | latest  | Micro web framework for the public landing page & portals.              |
| `fpdf`                    | latest  | Lightweight PDF generation library for business records.                 |

Install dependencies:
```bash
pip install -r requirements.txt
pip install flask fpdf
```

---

## 🗄 Database Layer & Fallback Mechanics (`db/`)

### `config.py` — MySQL Credentials
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_password',
    'database': 'hms_db'
}
```

### `db/connection.py` — Dual-Engine Wrapper
This module provides a **single transaction gateway** `execute_query(query, params, fetch)` that abstracts the database implementation details from the rest of the application:

1. **MySQL Direct Connection**: Tries connecting to the MySQL server using `DB_CONFIG`.
2. **Transparent SQLite Fallback**: If `mysql-connector-python` is missing, or the connection to the MySQL server fails (e.g., server offline, bad credentials), it creates a local SQLite database at `db/hms.db`.
3. **Dynamic Dialect Translation**: To ensure cross-compatibility between the MySQL DDL script and SQLite syntax:
   - Removes MySQL-specific database statements (`CREATE DATABASE`, `USE`).
   - Translates `AUTO_INCREMENT` definitions to SQLite `AUTOINCREMENT`.
   - Replaces custom `ENUM(...)` types with SQLite-compliant `TEXT` variables.
4. **Auto-Seeding**: Seeds the SQLite database automatically on its initial creation with standard staff accounts for all 5 system roles, clinic rooms, common medications, and lab test formats.
5. **Universal Query Parsing**: Evaluates placeholders dynamically, converting `%s` markers to SQLite `?` queries before sending them to the database engine.

---

## 🔐 Authentication Module (`auth/`)

### `auth/login.py`

#### `hash_password(password: str) → str`
Uses the **bcrypt** adaptive hashing algorithm. The Blowfish key schedule is applied $2^{\text{cost}}$ times ($2^{12} = 4096$ rounds) using a cryptographically random 128-bit salt:

$$\text{Iterations} = 2^{\text{cost}} = 4,096$$

The resulting hash string is formatted as:
`$2b$12$<22-char-salt><31-char-hash>`
where `$2b$` indicates the bcrypt version, and `$12$` is the work factor. Recomputing the Blowfish cipher key takes 200–300 ms on modern hardware, preventing brute-force attacks.

#### `check_credentials(username, password) → dict | None`
Verifies credentials in a constant-time comparison window to mitigate timing attacks. Used by CLI, GUI, and Web Application portals.

#### `create_user(username, password, role) → int | None`
Inserts a new user record. Allowed roles are validated against the set: `{'Admin', 'Doctor', 'Receptionist', 'Pharmacist', 'Lab Tech'}`. Passwords are automatically hashed prior to insertion.

---

## 📦 Business-Logic Modules (`modules/`)

### 1. Patients — `modules/patients.py`
Manages registration records. During ward allocation, it checks for available rooms, registers the entry timestamp, and marks the assigned room `is_available = FALSE` to prevent overlapping assignments.

### 2. Doctors — `modules/doctors.py`
Creates clinical profiles. Establishes a double insertion mapping:
1. Creates a standard authentication user record with `role = 'Doctor'`.
2. Uses the resulting `user_id` to insert a doctor profile record containing contact numbers and medical specialty fields.

### 3. Rooms — `modules/rooms.py`
Tracks hospital wards and emergency units. Rooms are categorized as `General`, `Private`, or `ICU` with active flags to signal availability.

### 4. Appointments — `modules/appointments.py`
Processes clinic scheduling. Parses user-submitted date-time strings into Python standard `datetime` objects and registers calendar events as `Scheduled`, `Completed`, or `Canceled`.

### 5. Pharmacy — `modules/pharmacy.py`
Manages the drug database. When adding inventory, the module routes the drug name to the `chemistry/` module to query PubChem and draw structural maps. Dispensing includes inventory check bounds:

$$S_{\text{new}} = S_{\text{old}} - Q_{\text{issued}} \quad \text{where} \quad S_{\text{old}} \ge Q_{\text{issued}}$$

### 6. Lab — `modules/lab.py`
Logs diagnostic requests. Doctors assign tests from the catalog (e.g., CBC, MRI). Lab Technicians receive assignments, complete the analysis, and record result descriptions into the report.

### 7. Billing — `modules/billing.py`
Calculates financial summaries. Items are aggregated across four categories (Room charges, Consultations, Lab diagnostics, and Pharmacy supplies) using exact cent arithmetic (`DECIMAL(10,2)`).

### 8. Staff — `modules/staff.py`
Creates general accounts for administrative, pharmacy, and diagnostic departments.

---

## ⚗ Chemistry Module (`chemistry/`)

### `chemistry/molecule_handler.py`
Connects to external chemical registries to extract drug formulas:

1. **PubChem API Query**: Sends an HTTP request to the PUG REST API:
   `https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/{drug_name}/JSON`
2. **SMILES Parsing**: Extracts the canonical SMILES string from the chemical registry payload (e.g., Aspirin $\to$ `"CC(=O)OC1=CC=CC=C1C(=O)O"`).
3. **Graph Construction**: RDKit translates the SMILES string into a mathematical graph representation $G = (V, E)$ where atoms are nodes and chemical bonds are weighted edges:

$$G = (V, E) \quad \text{where} \quad V = \{\text{Atoms}\}, \ E = \{\text{Bonds}\}$$

4. **Coordinate Drawing**: RDKit's CoordGen algorithm calculates 2D rendering layout coordinates and exports a $300 \times 300$ pixel PNG file to `static/molecule_images/`.

---

## 🛠 Utility Module (`utils/`)

- **`utils/helpers.py`** — OS-aware clear screen script mapping commands for Windows (`cls`) and Unix (`clear`).
- **`utils/validators.py`** — Evaluates user inputs. Validates telephone structures against international standard lengths:

$$\text{Valid}(\text{phone}) \iff \text{phone.isdigit()} \land (7 \le |\text{phone}| \le 15)$$

- **`utils/pdf_generator.py`** — Extracts paid bills records from the database, sums aggregate values, compiles tables, and saves clean invoice reports to `reports/revenue_report_YYYYMMDD.pdf`.

---

## 🖥 Entry Points & Interfaces

### 1. Command-Line Interface — `main.py`
Provides role-specific console dashboards containing secure hidden inputs (`getpass`). Displays actions appropriate to the user's role:

```bash
python main.py
```

---

### 2. Desktop GUI — `gui.py` + `gui_views/`
A Tkinter-based desktop interface.
- **Dynamic Views**: Instantiates specific views matching the authorized role after checking credentials.
- **Asynchronous Workers**: To prevent PubChem network API lookups and RDKit molecule rendering from locking up the Tkinter GUI thread, the medicine registration window uses a multi-threaded design:
  - **Worker Thread**: Contacts PubChem, parses SMILES, writes PNG images, and records database inserts.
  - **Main Thread**: Periodically checks a message queue (`queue.Queue`) every 100ms using Tkinter's `.after()` loop to refresh treeviews and show result dialogs when the background thread completes.

---

### 3. Web Application — `web_app.py` + `templates/`
A modern web portal built using Flask, Jinja2, and custom styled CSS.

#### Page Views
- **SaaS Marketing Page (`/`)**: A premium dark landing page highlighting features, uptime statistics, and subscription structures (Starter Clinic, Pro Hospital, Enterprise Network). Includes a glassmorphic dashboard mockup.
- **Public Register (`/register`)**: Public enrollment form allowing users to select their system role. Selecting `'Doctor'` runs client-side JavaScript to slide open clinical registration fields (specialization, full name, contact details).
- **Secure Portal Dashboard (`/dashboard`)**: Implements strict route authorization checking. Shows five customized dashboard layouts depending on the user's role:
  1. **Admin Panel**: Displays hospital statistics cards (active medical staff, current patients, total revenue sums), and directories for managing clinical personnel.
  2. **Doctor Workspace**: Shows appointment calendars, lists assigned ward patients, and provides lab order assignment menus.
  3. **Reception Desk**: Contains forms to register patients, book appointments, view unpaid bills, and display interactive room occupancy grids. Includes an **Invoice Calculator** that displays room fees, diagnostic costs, consultation fees, and pharmacy charges before finalizing the bill.
  4. **Pharmacist Station**: Displays medication stock, allows adding new medicines, and logs prescription drug dispensing.
  5. **Lab Workspace**: Monitors pending tests, registers test results, and adds new diagnostic categories.

#### Flask Route Reference

| Route | Methods | Authorization | Page Template | Description |
|---|---|---|---|---|
| `/` | `GET` | Public | `landing.html` | Premium SaaS landing page. |
| `/register` | `GET`, `POST` | Public | `register.html` | Registers new accounts (with dynamic Doctor profile fields). |
| `/login` | `GET`, `POST` | Public | `login.html` | Secure user credentials authorization. |
| `/logout` | `GET` | Public | — | Clears user sessions and redirects to login. |
| `/dashboard` | `GET` | Authenticated | `dashboard.html` | Multi-role responsive dashboard viewport. |
| `/doctors` | `GET`, `POST` | Admin | `doctors.html` | View clinic doctors directory or add new ones. |
| `/staff` | `GET`, `POST` | Admin | `staff.html` | View general staff list or add new members. |
| `/reports` | `GET` | Admin | `reports.html` | Displays paid bills audit listings. |
| `/download/report`| `GET` | Admin | — | Generates revenue audit PDF and triggers download. |
| `/doctor/assign_test` | `POST` | Doctor | — | Orders diagnostic lab tests for a patient. |
| `/receptionist/register_patient` | `POST` | Receptionist | — | Registers a new patient and assigns a room. |
| `/receptionist/book_appointment` | `POST` | Receptionist | — | Books a doctor appointment slot. |
| `/receptionist/save_bill` | `POST` | Receptionist | — | Computes final bill, discharges patient, and frees the room. |
| `/receptionist/pay_bill` | `POST` | Receptionist | — | Marks unpaid invoices as paid. |
| `/pharmacist/add_medicine` | `POST` | Pharmacist | — | Creates drug inventory (triggers PubChem thread API). |
| `/pharmacist/issue_medicine` | `POST` | Pharmacist | — | Deducts drug stock levels and logs issuance. |
| `/labtech/enter_result` | `POST` | Lab Tech | — | Enters laboratory diagnostic outcomes. |
| `/labtech/add_test_type` | `POST` | Lab Tech | — | Creates new diagnostic test catalog items. |

---

## 📐 Mathematical Formulas & Computational Logic

### 1. Room Charge Aggregation
Calculates charges based on room type rates (General = \$100/day, Private = \$300/day, ICU = \$500/day). The total stay duration is calculated from the admission and discharge timestamps, rounding fractional days up ($+1$) to count same-day discharges:

$$C_{\text{room}} = D \times P_{\text{room}}$$

$$D = \lfloor(t_{\text{discharge}} - t_{\text{admission}}) / 86,400\rfloor + 1$$

### 2. Consultation Fees
Aggregates fees for all booked appointments linked to a patient, charged at a flat rate of \$150.00 per consultation:

$$C_{\text{consult}} = N_{\text{appts}} \times 150.00$$

### 3. Lab Diagnostic Charges
Calculates the sum of all clinical tests assigned to the patient during their admission:

$$C_{\text{lab}} = \sum_{i=1}^{n} P_{\text{test}_i}$$

### 4. Pharmacy Charges
Aggregates quantities ($Q_j$) of medications issued to a patient multiplied by their unit price ($P_j$):

$$C_{\text{pharmacy}} = \sum_{j=1}^{m} (Q_j \times P_j)$$

### 5. Final Invoice Calculation
Calculates the patient's grand total bill:

$$T = C_{\text{room}} + C_{\text{consult}} + C_{\text{lab}} + C_{\text{pharmacy}}$$

$$T = \left[ D \times P_{\text{room}} \right] + \left[ N_{\text{appts}} \times 150.00 \right] + \sum_{i=1}^{n} P_{\text{test}_i} + \sum_{j=1}^{m} (Q_j \times P_j)$$

---

## 🚀 Setup & Installation

### 1. Install System Requirements
Make sure you have **Python 3.8+** installed. Install the Python dependencies:
```bash
pip install -r requirements.txt
pip install flask fpdf
```

### 2. Setup Database

#### Option A: Quick Zero-Configuration Run (SQLite)
No database setup is required. When starting the application, if MySQL connection details are not found or fail, the application **automatically falls back to SQLite**, creating `db/hms.db` and seeding it with standard testing data.

#### Option B: Production Database Server (MySQL)
1. Edit `config.py` with your MySQL server credentials:
   ```python
   DB_CONFIG = {
       'host': 'localhost',
       'user': 'root',
       'password': 'your_password',
       'database': 'hms_db'
   }
   ```
2. Run the MySQL schema initialization command:
   ```bash
   mysql -u root -p < db/schema.sql
   ```
3. Initialize the default Administrator account:
   ```bash
   python -c "from auth.login import create_user; create_user('admin', 'admin123', 'Admin')"
   ```

---

## 🔍 Diagnostics & Verification

The project includes a verification script `test_app.py` to run baseline tests on the system:
```bash
python test_app.py
```
This script runs a diagnostic check on:
- Database connectivity (MySQL connection test or SQLite fallback creation).
- Seeded user database validation (confirms Admin, Doctor, Receptionist, Pharmacist, and Lab Tech roles).
- Hospital room list retrieval.
- Cheminformatics pipeline (contacts PubChem API for Aspirin and draws its 2D molecular structure using RDKit).

---

## 📖 Usage Guide

### Launching the Web Portal
```bash
python web_app.py
```
Open your browser and navigate to `http://127.0.0.1:5000/`. You can log in using one of the pre-seeded role accounts:
- **Admin**: `admin` / `admin123`
- **Doctor**: `doctor` / `doctor123`
- **Receptionist**: `receptionist` / `receptionist123`
- **Pharmacist**: `pharmacist` / `pharmacist123`
- **Lab Tech**: `labtech` / `labtech123`

### Launching the Desktop App
```bash
python gui.py
```
Displays a graphical Tkinter login window. Authenticated roles will view their respective menus (e.g. treeviews and medicine molecule viewers for Pharmacist accounts).

### Launching the CLI App
```bash
python main.py
```
Provides simple, text-based navigation menus.

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
│ Web portal access   │   ✅  │   ✅   │      ✅      │     ✅     │    ✅    │
│ GUI access          │   ✅  │        │              │     ✅     │          │
└─────────────────────┴───────┴────────┴──────────────┴────────────┴──────────┘
```

---

> **Built with** 🐍 Python · 🐬 MySQL / 🗄️ SQLite · ⚗️ RDKit & PubChem · 🌐 Flask · 🖥️ Tkinter & ttk