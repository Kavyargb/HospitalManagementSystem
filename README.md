# Hospital Management System (HMS)

A CLI-based Hospital Management System written in Python with MySQL.

## Features
- Role-based access control (Admin, Doctor, etc.)
- Patient and Doctor Management
- Appointment Scheduling
- Pharmacy module with PubChem API and RDKit for molecule visualization
- Lab Test and Billing Management
- PDF Report Generation

## Setup
1.  Ensure you have Python 3.x and MySQL Server installed.
2.  Install required Python packages:
    ```bash
    pip install -r requirements.txt
    ```
3.  Create the database schema by executing `db/schema.sql` in your MySQL client.
4.  Update database credentials in `config.py`.
5.  Create an initial admin user:
    ```bash
    python -c "from auth.login import create_user; create_user('admin', 'admin123', 'Admin')"
    ```
## Usage
- **Run the CLI application:**
  ```bash
  python main.py