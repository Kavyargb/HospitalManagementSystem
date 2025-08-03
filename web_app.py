import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from functools import wraps
from db.connection import execute_query
from auth.login import check_credentials, create_user
from modules.doctors import create_doctor_profile
from utils.pdf_generator import generate_revenue_report

# Initialize the Flask application
app = Flask(__name__)
# A secret key is required for session management and flashing messages
app.config['SECRET_KEY'] = 'a_super_secret_key_change_this_in_production'

# --- Authentication Decorator ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session or session['user']['role'] != 'Admin':
            flash("You must be logged in as an Admin to view this page.", "error")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Authentication Routes ---
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = check_credentials(username, password)
        
        if user and user['role'] == 'Admin':
            session['user'] = user # Store user info in the session
            flash(f"Welcome, {user['username']}!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid credentials or not an Admin account.", "error")
            
    return render_template('login.html')

@app.route("/logout")
def logout():
    session.pop('user', None) # Clear the session
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))

# --- Main Admin Dashboard Route ---
@app.route("/")
@login_required
def dashboard():
    doctors_count = execute_query("SELECT COUNT(*) as count FROM doctors", fetch='one')['count']
    patients_count = execute_query("SELECT COUNT(*) as count FROM patients", fetch='one')['count']
    return render_template('dashboard.html', doctors_count=doctors_count, patients_count=patients_count)

# --- Doctor Management Routes ---
@app.route("/doctors", methods=['GET', 'POST'])
@login_required
def manage_doctors():
    if request.method == 'POST':
        # Logic to add a new doctor
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
        
    # GET request: Display all doctors
    doctors_list = execute_query("SELECT d.id, d.name, d.specialization, d.contact, u.username FROM doctors d JOIN users u ON d.user_id = u.id", fetch='all')
    return render_template('doctors.html', doctors=doctors_list)

# --- Staff Management Routes ---
@app.route("/staff", methods=['GET', 'POST'])
@login_required
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
        
    # GET request: Display staff members
    staff_list = execute_query("SELECT id, username, role FROM users WHERE role NOT IN ('Admin', 'Doctor')", fetch='all')
    return render_template('staff.html', staff=staff_list)

# --- Reports and PDF Download ---
@app.route("/reports")
@login_required
def view_reports():
    paid_bills = execute_query("SELECT b.id, p.name, b.total_amount, b.bill_date FROM bills b JOIN patients p ON b.patient_id = p.id WHERE b.payment_status = 'Paid' ORDER BY b.bill_date DESC", fetch='all')
    return render_template('reports.html', bills=paid_bills)

@app.route("/download/report")
@login_required
def download_report():
    # This generates the PDF and returns its full path
    report_path = generate_revenue_report()
    if report_path:
        # Get directory and filename from the path
        directory = os.path.dirname(report_path)
        filename = os.path.basename(report_path)
        # Send the file for download
        return send_from_directory(directory, filename, as_attachment=True)
    else:
        flash("Could not generate report. No data available.", "error")
        return redirect(url_for('view_reports'))


if __name__ == '__main__':
    app.run(debug=True)