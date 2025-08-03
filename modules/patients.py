from db.connection import execute_query
from modules.doctors import list_all_doctors
from modules.rooms import list_available_rooms, update_room_status
from datetime import datetime

def register_patient():
    """Receptionist function to register a new patient."""
    print("\n--- Register New Patient ---")
    try:
        # 1. Collect Patient Info
        name = input("Enter patient's full name: ")
        age = int(input("Enter age: "))
        gender = input("Enter gender (Male/Female/Other): ")
        address = input("Enter address: ")
        contact = input("Enter contact number: ")

        # 2. Assign Doctor
        print("\nPlease assign a doctor:")
        doctors = list_all_doctors()
        if not doctors:
            print("Cannot register patient. No doctors available.")
            return
        doctor_id = int(input("Enter the Doctor ID to assign: "))

        # 3. Assign Room
        print("\nPlease assign a room:")
        rooms = list_available_rooms()
        if not rooms:
            print("Cannot register patient. No rooms available.")
            return
        room_id = int(input("Enter the Room ID to assign: "))

        # 4. Database Insertion
        admission_date = datetime.now()
        query = """
            INSERT INTO patients (name, age, gender, address, contact, doctor_id, room_id, admission_date)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (name, age, gender, address, contact, doctor_id, room_id, admission_date)
        patient_id = execute_query(query, params)
        
        # 5. Update Room Availability
        update_room_status(room_id, is_available=False)

        print(f"Patient '{name}' registered successfully with ID: {patient_id}.")

    except ValueError:
        print("Invalid input. Please enter numbers for age, doctor ID, and room ID.")
    except Exception as e:
        print(f"An error occurred: {e}")

def search_patient_by_id():
    """Searches for a patient by their ID."""
    try:
        patient_id = int(input("Enter Patient ID to search: "))
        query = "SELECT * FROM patients WHERE id = %s"
        patient = execute_query(query, (patient_id,), fetch='one')

        if patient:
            print("\n--- Patient Details ---")
            for key, value in patient.items():
                print(f"{key.replace('_', ' ').title()}: {value}")
            return patient
        else:
            print(f"No patient found with ID {patient_id}.")
            return None
    except ValueError:
        print("Invalid ID. Please enter a number.")
        return None