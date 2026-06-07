import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from functools import wraps
from datetime import datetime
from db.connection import execute_query
from auth.login import check_credentials, create_user
from modules.doctors import create_doctor_profile
from utils.pdf_generator import generate_revenue_report

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_super_secret_key_change_this_in_production'

@app.context_processor
def inject_now():
    return {'datetime_now': datetime.now()}

# --- Authentication Decorators ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash("You must be logged in to access this page.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user' not in session or session['user']['role'] not in roles:
                flash("You are not authorized to view that page.", "error")
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- Authentication Routes ---
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = check_credentials(username, password)
        
        if user:
            session['user'] = user
            flash(f"Welcome, {user['username']}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials.", "error")
            
    return render_template('login.html')

@app.route("/logout")
def logout():
    session.pop('user', None)
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# --- Landing Page Route ---
@app.route("/")
def index():
    return render_template('landing.html')

# --- User Registration Route ---
@app.route("/register", methods=['GET', 'POST'])
def register():
    if 'user' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')
        
        if not username or not password or not role:
            flash("All fields are required.", "error")
            return redirect(url_for('register'))
            
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for('register'))
            
        # Check if user already exists
        existing_user = execute_query("SELECT id FROM users WHERE username = %s", (username.lower().strip() if username else "",), fetch='one')
        if existing_user:
            flash("Username is already taken.", "error")
            return redirect(url_for('register'))
            
        if role == 'Doctor':
            name = request.form.get('doctor_name')
            specialization = request.form.get('specialization')
            contact = request.form.get('contact')
            
            if not name:
                flash("Doctor full name is required for profile creation.", "error")
                return redirect(url_for('register'))
                
            doc_id = create_doctor_profile(name, specialization, contact, username, password)
            if doc_id:
                flash("Doctor registration successful! Please log in.", "success")
                return redirect(url_for('login'))
            else:
                flash("Error creating doctor profile. Please try again.", "error")
                return redirect(url_for('register'))
        else:
            user_id = create_user(username, password, role)
            if user_id:
                flash("Registration successful! Please log in.", "success")
                return redirect(url_for('login'))
            else:
                flash("Error creating user account. Please try again.", "error")
                return redirect(url_for('register'))
                
    return render_template('register.html')

# --- Main Dashboard Switcher Route ---
@app.route("/dashboard")
@login_required
def dashboard():
    role = session['user']['role']
    
    # 1. ADMIN DASHBOARD DATA
    if role == 'Admin':
        doctors_count = execute_query("SELECT COUNT(*) as count FROM doctors", fetch='one')['count']
        patients_count = execute_query("SELECT COUNT(*) as count FROM patients WHERE discharge_date IS NULL", fetch='one')['count']
        staff_count = execute_query("SELECT COUNT(*) as count FROM users WHERE role NOT IN ('Admin', 'Doctor')", fetch='one')['count']
        
        # Calculate revenue total from paid bills
        revenue_row = execute_query("SELECT SUM(total_amount) as total FROM bills WHERE payment_status = 'Paid'", fetch='one')
        revenue = revenue_row['total'] if revenue_row and revenue_row['total'] else 0.0
        
        return render_template(
            'dashboard.html', 
            doctors_count=doctors_count, 
            patients_count=patients_count,
            staff_count=staff_count,
            revenue=revenue
        )
        
    # 2. DOCTOR DASHBOARD DATA
    elif role == 'Doctor':
        # Get doctor ID linked to user
        doc_profile = execute_query("SELECT id, name, specialization FROM doctors WHERE user_id = %s", (session['user']['id'],), fetch='one')
        
        appointments = []
        patients = []
        lab_tests = []
        
        if doc_profile:
            # Appointments
            appointments = execute_query(
                "SELECT a.id, p.name as patient_name, a.appointment_time, a.status FROM appointments a JOIN patients p ON a.patient_id = p.id WHERE a.doctor_id = %s ORDER BY a.appointment_time ASC",
                (doc_profile['id'],), fetch='all'
            )
            # Active patients assigned
            patients = execute_query(
                "SELECT p.id, p.name, p.age, p.gender, r.room_number FROM patients p JOIN rooms r ON p.room_id = r.id WHERE p.doctor_id = %s AND p.discharge_date IS NULL",
                (doc_profile['id'],), fetch='all'
            )
            
        # Get available lab tests for the assigner dropdown
        lab_tests = execute_query("SELECT id, name FROM lab_tests ORDER BY name", fetch='all')
            
        return render_template(
            'dashboard.html',
            doctor=doc_profile,
            appointments=appointments,
            patients=patients,
            lab_tests=lab_tests
        )
        
    # 3. RECEPTIONIST DASHBOARD DATA
    elif role == 'Receptionist':
        # Doctors dropdown
        doctors_list = execute_query("SELECT id, name, specialization FROM doctors ORDER BY name", fetch='all')
        # Active patients list
        active_patients = execute_query("SELECT id, name FROM patients WHERE discharge_date IS NULL ORDER BY name", fetch='all')
        # All patients list (for billing/booking)
        all_patients = execute_query("SELECT id, name FROM patients ORDER BY name", fetch='all')
        # Rooms list with occupancies (for room grid)
        rooms_list = execute_query(
            "SELECT r.id, r.room_number, r.type, r.is_available, p.name as patient_name FROM rooms r LEFT JOIN patients p ON r.id = p.room_id AND p.discharge_date IS NULL ORDER BY r.room_number",
            fetch='all'
        )
        # Available rooms dropdown
        available_rooms = execute_query("SELECT id, room_number, type FROM rooms WHERE is_available = 1 ORDER BY room_number", fetch='all')
        
        # Unpaid bills list
        unpaid_bills = execute_query(
            "SELECT b.id, p.name, b.total_amount, b.bill_date FROM bills b JOIN patients p ON b.patient_id = p.id WHERE b.payment_status = 'Unpaid' ORDER BY b.bill_date DESC",
            fetch='all'
        )
        
        # Check if calculating patient bill
        calc_patient_id = request.args.get('calculate_bill')
        bill_details = None
        if calc_patient_id:
            try:
                calc_patient_id = int(calc_patient_id)
                patient_info = execute_query("SELECT * FROM patients WHERE id = %s", (calc_patient_id,), fetch='one')
                if patient_info:
                    bill_details = _calculate_invoice(patient_info)
            except ValueError:
                pass
                
        return render_template(
            'dashboard.html',
            doctors=doctors_list,
            active_patients=active_patients,
            all_patients=all_patients,
            rooms=rooms_list,
            available_rooms=available_rooms,
            unpaid_bills=unpaid_bills,
            bill_details=bill_details
        )
        
    # 4. PHARMACIST DASHBOARD DATA
    elif role == 'Pharmacist':
        medicines = execute_query("SELECT id, name, smiles, image_path, quantity, expiry_date, price FROM medicines ORDER BY name", fetch='all')
        active_patients = execute_query("SELECT id, name FROM patients WHERE discharge_date IS NULL ORDER BY name", fetch='all')
        
        return render_template(
            'dashboard.html',
            medicines=medicines,
            patients=active_patients
        )
        
    # 5. LAB TECH DASHBOARD DATA
    elif role == 'Lab Tech':
        pending_tests = execute_query(
            "SELECT lr.id, p.name as patient_name, lt.name as test_name, lr.report_date FROM lab_reports lr JOIN patients p ON lr.patient_id = p.id JOIN lab_tests lt ON lr.test_id = lt.id WHERE lr.result IS NULL ORDER BY lr.report_date ASC",
            fetch='all'
        )
        test_types = execute_query("SELECT id, name, price FROM lab_tests ORDER BY name", fetch='all')
        
        return render_template(
            'dashboard.html',
            pending_tests=pending_tests,
            test_types=test_types
        )
        
    return render_template('dashboard.html')

# --- Helper function for invoice details calculations ---
def _calculate_invoice(patient):
    # Prices
    ROOM_PRICES = {'General': 100.00, 'Private': 300.00, 'ICU': 500.00}
    CONSULTATION_FEE = 150.00
    
    patient_id = patient['id']
    details = {
        'patient_id': patient_id,
        'name': patient['name'],
        'room_charge': 0.0,
        'room_days': 0,
        'room_type': 'None',
        'consultation_charge': 0.0,
        'consultation_count': 0,
        'lab_charge': 0.0,
        'lab_tests': [],
        'pharmacy_charge': 0.0,
        'medicines': [],
        'grand_total': 0.0
    }
    
    # 1. Room
    room = execute_query("SELECT type FROM rooms WHERE id = %s", (patient['room_id'],), fetch='one')
    if room:
        discharge_date = patient['discharge_date'] or datetime.now()
        # Parse if string (from SQLite text datetime)
        if isinstance(discharge_date, str):
            try:
                discharge_date = datetime.strptime(discharge_date.split('.')[0], "%Y-%m-%d %H:%M:%S")
            except:
                discharge_date = datetime.now()
        
        adm_date = patient['admission_date']
        if isinstance(adm_date, str):
            try:
                adm_date = datetime.strptime(adm_date.split('.')[0], "%Y-%m-%d %H:%M:%S")
            except:
                adm_date = datetime.now()
                
        days = (discharge_date - adm_date).days + 1
        price = ROOM_PRICES.get(room['type'], 0.0)
        details['room_days'] = days
        details['room_type'] = room['type']
        details['room_charge'] = float(days * price)
        
    # 2. Consultations
    appts = execute_query("SELECT COUNT(*) as count FROM appointments WHERE patient_id = %s", (patient_id,), fetch='one')
    appt_count = appts['count'] if appts else 0
    details['consultation_count'] = appt_count
    details['consultation_charge'] = float(appt_count * CONSULTATION_FEE)
    
    # 3. Lab Tests
    labs = execute_query(
        "SELECT lt.name, lt.price FROM lab_reports lr JOIN lab_tests lt ON lr.test_id = lt.id WHERE lr.patient_id = %s",
        (patient_id,), fetch='all'
    )
    if labs:
        details['lab_tests'] = labs
        details['lab_charge'] = float(sum(l['price'] for l in labs))
        
    # 4. Medicines
    meds = execute_query(
        "SELECT m.name, mi.quantity, m.price FROM medicine_issued mi JOIN medicines m ON mi.medicine_id = m.id WHERE mi.patient_id = %s",
        (patient_id,), fetch='all'
    )
    if meds:
        details['medicines'] = meds
        details['pharmacy_charge'] = float(sum(m['quantity'] * m['price'] for m in meds))
        
    # Grand Total
    details['grand_total'] = details['room_charge'] + details['consultation_charge'] + details['lab_charge'] + details['pharmacy_charge']
    
    return details


# --- Admin Doctor & Staff CRUD ---
@app.route("/doctors", methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def manage_doctors():
    if request.method == 'POST':
        name = request.form.get('name')
        spec = request.form.get('specialization')
        contact = request.form.get('contact')
        username = request.form.get('username')
        password = request.form.get('password')
        
        if create_doctor_profile(name, spec, contact, username, password):
            flash(f"Doctor '{name}' added successfully!", "success")
        else:
            flash("Error adding doctor. Username might be taken.", "error")
        return redirect(url_for('manage_doctors'))
        
    doctors_list = execute_query("SELECT d.id, d.name, d.specialization, d.contact, u.username FROM doctors d JOIN users u ON d.user_id = u.id", fetch='all')
    return render_template('doctors.html', doctors=doctors_list)

@app.route("/staff", methods=['GET', 'POST'])
@login_required
@role_required('Admin')
def manage_staff():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        role = request.form.get('role')

        if create_user(username, password, role):
            flash(f"Staff member '{username}' ({role}) created successfully!", "success")
        else:
            flash(f"Error creating staff member. Username may exist.", "error")
        return redirect(url_for('manage_staff'))
        
    staff_list = execute_query("SELECT id, username, role FROM users WHERE role NOT IN ('Admin', 'Doctor')", fetch='all')
    return render_template('staff.html', staff=staff_list)

# --- Financial Reports Route ---
@app.route("/reports")
@login_required
@role_required('Admin')
def view_reports():
    paid_bills = execute_query("SELECT b.id, p.name, b.total_amount, b.bill_date FROM bills b JOIN patients p ON b.patient_id = p.id WHERE b.payment_status = 'Paid' ORDER BY b.bill_date DESC", fetch='all')
    return render_template('reports.html', bills=paid_bills)

@app.route("/download/report")
@login_required
@role_required('Admin')
def download_report():
    report_path = generate_revenue_report()
    if report_path:
        directory = os.path.dirname(report_path)
        filename = os.path.basename(report_path)
        return send_from_directory(directory, filename, as_attachment=True)
    else:
        flash("Could not generate report. No data available.", "error")
        return redirect(url_for('view_reports'))


# --- Doctor Actions ---
@app.route("/doctor/assign_test", methods=['POST'])
@login_required
@role_required('Doctor')
def doctor_assign_test():
    patient_id = request.form.get('patient_id')
    test_id = request.form.get('test_id')
    
    if patient_id and test_id:
        query = "INSERT INTO lab_reports (patient_id, test_id, report_date) VALUES (%s, %s, %s)"
        execute_query(query, (patient_id, test_id, datetime.now()))
        flash("Lab test assigned successfully!", "success")
    else:
        flash("Invalid test assignment inputs.", "error")
        
    return redirect(url_for('dashboard'))


# --- Receptionist Actions ---
@app.route("/receptionist/register_patient", methods=['POST'])
@login_required
@role_required('Receptionist')
def register_patient():
    name = request.form.get('name')
    age = request.form.get('age')
    gender = request.form.get('gender')
    address = request.form.get('address')
    contact = request.form.get('contact')
    doctor_id = request.form.get('doctor_id')
    room_id = request.form.get('room_id')
    
    try:
        # Save patient
        query = "INSERT INTO patients (name, age, gender, address, contact, doctor_id, room_id, admission_date) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        patient_id = execute_query(query, (name, int(age), gender, address, contact, int(doctor_id), int(room_id), datetime.now()))
        
        # Mark room occupied
        execute_query("UPDATE rooms SET is_available = 0 WHERE id = %s", (room_id,))
        flash(f"Patient registered successfully! ID: {patient_id}", "success")
    except Exception as e:
        flash(f"Error registering patient: {e}", "error")
        
    return redirect(url_for('dashboard'))

@app.route("/receptionist/book_appointment", methods=['POST'])
@login_required
@role_required('Receptionist')
def book_appointment():
    patient_id = request.form.get('patient_id')
    doctor_id = request.form.get('doctor_id')
    time_str = request.form.get('appointment_time')
    
    try:
        # Parse time: HTML datetime-local format: 'YYYY-MM-DDTHH:MM'
        appt_time = datetime.strptime(time_str, "%Y-%m-%dT%H:%M")
        query = "INSERT INTO appointments (patient_id, doctor_id, appointment_time) VALUES (%s, %s, %s)"
        execute_query(query, (patient_id, doctor_id, appt_time))
        flash("Appointment booked successfully!", "success")
    except Exception as e:
        flash(f"Error booking appointment: {e}", "error")
        
    return redirect(url_for('dashboard'))

@app.route("/receptionist/save_bill", methods=['POST'])
@login_required
@role_required('Receptionist')
def save_bill():
    patient_id = request.form.get('patient_id')
    total_amount = request.form.get('total_amount')
    
    if patient_id and total_amount:
        try:
            # Check if patient exists
            patient = execute_query("SELECT name, room_id FROM patients WHERE id = %s", (patient_id,), fetch='one')
            if patient:
                # Insert bill
                query = "INSERT INTO bills (patient_id, total_amount, bill_date) VALUES (%s, %s, %s)"
                execute_query(query, (patient_id, float(total_amount), datetime.now()))
                
                # Auto discharge patient & free room!
                execute_query("UPDATE patients SET discharge_date = %s WHERE id = %s", (datetime.now(), patient_id))
                execute_query("UPDATE rooms SET is_available = 1 WHERE id = %s", (patient['room_id'],))
                
                flash("Bill saved and Patient discharged/room freed!", "success")
            else:
                flash("Patient not found.", "error")
        except Exception as e:
            flash(f"Error saving bill: {e}", "error")
    return redirect(url_for('dashboard'))

@app.route("/receptionist/pay_bill", methods=['POST'])
@login_required
@role_required('Receptionist')
def pay_bill():
    bill_id = request.form.get('bill_id')
    if bill_id:
        execute_query("UPDATE bills SET payment_status = 'Paid' WHERE id = %s", (bill_id,))
        flash(f"Bill ID {bill_id} marked as PAID!", "success")
    return redirect(url_for('dashboard'))


# --- Pharmacist Actions ---
@app.route("/pharmacist/add_medicine", methods=['POST'])
@login_required
@role_required('Pharmacist')
def add_medicine():
    name = request.form.get('name')
    qty = request.form.get('quantity')
    price = request.form.get('price')
    exp_date = request.form.get('expiry_date')
    
    # Import pharmacy function dynamically to use its database seeding
    from modules.pharmacy import add_medicine_to_db
    
    if add_medicine_to_db(name, qty, price, exp_date):
        flash(f"Medicine '{name}' added successfully!", "success")
    else:
        flash("Error adding medicine to inventory.", "error")
        
    return redirect(url_for('dashboard'))

@app.route("/pharmacist/issue_medicine", methods=['POST'])
@login_required
@role_required('Pharmacist')
def issue_medicine():
    patient_id = request.form.get('patient_id')
    medicine_id = request.form.get('medicine_id')
    qty_to_issue = request.form.get('quantity')
    
    try:
        qty_to_issue = int(qty_to_issue)
        
        # Check stock
        med = execute_query("SELECT name, quantity FROM medicines WHERE id = %s", (medicine_id,), fetch='one')
        if not med:
            flash("Medicine not found.", "error")
            return redirect(url_for('dashboard'))
            
        if med['quantity'] < qty_to_issue:
            flash(f"Insufficient stock for {med['name']}. Available: {med['quantity']}", "error")
            return redirect(url_for('dashboard'))
            
        # Deduct stock
        execute_query("UPDATE medicines SET quantity = quantity - %s WHERE id = %s", (qty_to_issue, medicine_id))
        
        # Log issuance
        query = "INSERT INTO medicine_issued (patient_id, medicine_id, quantity, issue_date) VALUES (%s, %s, %s, %s)"
        execute_query(query, (patient_id, medicine_id, qty_to_issue, datetime.now()))
        
        flash(f"Issued {qty_to_issue} units of {med['name']} successfully!", "success")
    except Exception as e:
        flash(f"Error issuing medicine: {e}", "error")
        
    return redirect(url_for('dashboard'))


# --- Lab Tech Actions ---
@app.route("/labtech/enter_result", methods=['POST'])
@login_required
@role_required('Lab Tech')
def enter_result():
    report_id = request.form.get('report_id')
    result = request.form.get('result')
    
    if report_id and result:
        execute_query("UPDATE lab_reports SET result = %s WHERE id = %s", (result, report_id))
        flash("Lab report results saved!", "success")
    else:
        flash("Invalid results inputs.", "error")
        
    return redirect(url_for('dashboard'))

@app.route("/labtech/add_test_type", methods=['POST'])
@login_required
@role_required('Lab Tech')
def add_test_type():
    name = request.form.get('name')
    price = request.form.get('price')
    
    try:
        query = "INSERT INTO lab_tests (name, price) VALUES (%s, %s)"
        execute_query(query, (name, float(price)))
        flash(f"Lab test type '{name}' created!", "success")
    except Exception as e:
        flash(f"Error adding test type: {e}", "error")
        
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    app.run(debug=True)