# hospital_system/main.py

import auth.login
from db.connection import get_db_connection
import modules.patients as patients
import modules.doctors as doctors
import modules.appointments as appointments
import modules.pharmacy as pharmacy
import modules.lab as lab
import modules.billing as billing
from utils.pdf_generator import generate_revenue_report
import modules.staff as staff # Import the new module

def admin_menu(user):
    print(f"\n--- Admin Menu (Logged in as {user['username']}) ---")
    while True:
        print("1. Manage Doctors (Add/List)")
        print("2. Create Staff Account (Receptionist, Pharmacist, etc.)") # New granular option
        print("3. Add New Lab Test Type")
        print("4. Generate Revenue Report (PDF)")
        print("5. Logout")
        choice = input("Enter choice: ")
        if choice == '1':
            # You could create a sub-menu for doctors here
            print("1. Add New Doctor\n2. List All Doctors")
            doc_choice = input("Doctor management choice: ")
            if doc_choice == '1':
                doctors.add_doctor()
            elif doc_choice == '2':
                doctors.list_all_doctors()
        elif choice == '2':
            staff.create_staff_member() # Call the new function
        elif choice == '3':
            lab.add_lab_test()
        elif choice == '4':
            generate_revenue_report()
        elif choice == '5':
            break
        else:
            print("Invalid choice.")

def doctor_menu(user):
    print(f"\n--- Doctor Menu (Logged in as {user['username']}) ---")
    while True:
        print("1. View My Appointments")
        print("2. Search Patient by ID")
        print("3. Assign Lab Test to Patient")
        print("4. Logout")
        choice = input("Enter choice: ")
        if choice == '1':
            appointments.view_doctor_appointments(user)
        elif choice == '2':
            patients.search_patient_by_id()
        elif choice == '3':
            lab.assign_test_to_patient()
        elif choice == '4':
            break
        else:
            print("Invalid choice.")

def receptionist_menu(user):
    print(f"\n--- Receptionist Menu (Logged in as {user['username']}) ---")
    while True:
        print("1. Register Patient")
        print("2. Book Appointment")
        print("3. Search Patient by ID")
        print("4. Generate Patient Bill")
        print("5. Update Payment Status")
        print("6. Logout")
        choice = input("Enter choice: ")
        if choice == '1':
            patients.register_patient()
        elif choice == '2':
            appointments.book_appointment()
        elif choice == '3':
            patients.search_patient_by_id()
        if choice == '4':
            billing.generate_patient_bill()
        elif choice == '5':
            billing.update_payment_status()
        elif choice == '6':
            break
        else:
            print("Invalid choice.")
            
def pharmacist_menu(user):
    print(f"\n--- Pharmacist Menu (Logged in as {user['username']}) ---")
    while True:
        print("1. Add New Medicine to Stock")
        print("2. View Medicine Inventory")
        print("3. Issue Medicine to Patient")
        print("4. View Molecule Structure") # New Option
        print("5. Logout")
        choice = input("Enter choice: ")

        if choice == '1':
            pharmacy.add_medicine()
        elif choice == '2':
            pharmacy.view_medicine_stock()
        elif choice == '3':
            pharmacy.issue_medicine()
        elif choice == '4':
            pharmacy.view_molecule_image() # Call the new function
        elif choice == '5':
            break
        else:
            print("Invalid choice. Please try again.")



def lab_tech_menu(user):
    print(f"\n--- Lab Tech Menu (Logged in as {user['username']}) ---")
    while True:
        print("1. Input Lab Test Result")
        print("2. Add New Lab Test Type")
        print("3. Logout")
        choice = input("Enter choice: ")
        if choice == '1':
            lab.input_test_result()
        elif choice == '2':
            lab.add_lab_test()
        elif choice == '3':
            break
        else:
            print("Invalid choice.")
def main():
    if not get_db_connection():
        print("Could not connect to the database. Exiting.")
        return

    print("==========================================")
    print(" Welcome to the Hospital Management System ")
    print("==========================================")

    while True:
        current_user = auth.login.login()

        if current_user:
            role = current_user['role']
            if role == 'Admin':
                admin_menu(current_user)
            elif role == 'Doctor':
                doctor_menu(current_user)
            elif role == 'Receptionist':
                receptionist_menu(current_user)
            elif role == 'Pharmacist':
                pharmacist_menu(current_user)
            elif role =="Lab Tech":
                lab_tech_menu(current_user)            
            print("You have been logged out.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nApplication terminated by user. Goodbye!")