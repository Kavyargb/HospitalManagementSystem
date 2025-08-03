from db.connection import execute_query
from modules.doctors import list_all_doctors, get_doctor_id_from_user_id
from modules.patients import search_patient_by_id
from datetime import datetime

def book_appointment():
    """Receptionist function to book a new appointment."""
    print("\n--- Book New Appointment ---")
    try:
        # 1. Select Patient
        patient = search_patient_by_id()
        if not patient:
            return
        patient_id = patient['id']

        # 2. Select Doctor
        print("\nPlease select a doctor for the appointment:")
        doctors = list_all_doctors()
        if not doctors:
            return
        doctor_id = int(input("Enter Doctor ID: "))

        # 3. Get Appointment Time
        date_str = input("Enter appointment date and time (YYYY-MM-DD HH:MM): ")
        appointment_time = datetime.strptime(date_str, "%Y-%m-%d %H:%M")

        # 4. Database Insertion
        query = "INSERT INTO appointments (patient_id, doctor_id, appointment_time) VALUES (%s, %s, %s)"
        execute_query(query, (patient_id, doctor_id, appointment_time))
        print("Appointment booked successfully!")

    except ValueError:
        print("Invalid input for ID or date format.")
    except Exception as e:
        print(f"An error occurred: {e}")

def view_doctor_appointments(user):
    """Doctor function to view their own appointments."""
    doctor_id = get_doctor_id_from_user_id(user['id'])
    if not doctor_id:
        print("Could not find a doctor profile linked to your user account.")
        return
        
    query = """
        SELECT a.id, p.name AS patient_name, a.appointment_time, a.status
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        WHERE a.doctor_id = %s AND a.status = 'Scheduled'
        ORDER BY a.appointment_time
    """
    appointments = execute_query(query, (doctor_id,), fetch='all')

    if not appointments:
        print("You have no scheduled appointments.")
        return

    print("\n--- Your Scheduled Appointments ---")
    print(f"{'ID':<5}{'Patient Name':<25}{'Time':<20}{'Status':<15}")
    print("-" * 65)
    for app in appointments:
        print(f"{app['id']:<5}{app['patient_name']:<25}{str(app['appointment_time']):<20}{app['status']:<15}")
    print("-" * 65)