# hospital_system/modules/doctors.py

from db.connection import execute_query
# Import the hashing function to create a new user
from auth.login import hash_password

def add_doctor():
    """Admin function to create a new doctor user and profile in one step."""
    print("\n--- Add New Doctor (User & Profile) ---")
    try:
        name = input("Enter doctor's full name: ")
        specialization = input("Enter specialization: ")
        contact = input("Enter contact number: ")

        print("\n--- Create Login Credentials for the Doctor ---")
        username = input(f"Enter a username for Dr. {name.split()[0]}: ")
        password = input(f"Enter a temporary password for Dr. {name.split()[0]}: ")

        password_hash = hash_password(password)
        role = 'Doctor'
        
        user_query = "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)"
        user_id = execute_query(user_query, (username, password_hash, role))

        if not user_id:
            print(f"\nError: Could not create a user account for '{username}'. The username might already be taken.")
            return

        doctor_query = "INSERT INTO doctors (user_id, name, specialization, contact) VALUES (%s, %s, %s, %s)"
        execute_query(doctor_query, (user_id, name, specialization, contact))

        print(f"\n✅ Success! Doctor '{name}' created with username '{username}'.")
        print("   They can now log in with the password you set.")

    except Exception as e:
        print(f"An error occurred while adding the doctor: {e}")

# The rest of the functions in this file (list_all_doctors, get_doctor_id_from_user_id) remain the same.
def list_all_doctors():
    """Lists all doctors in the system."""
    query = "SELECT d.id, d.name, d.specialization, d.contact, u.username FROM doctors d JOIN users u ON d.user_id = u.id"
    doctors = execute_query(query, fetch='all')

    if not doctors:
        print("No doctors found.")
        return None

    print("\n--- List of Doctors ---")
    print(f"{'ID':<5}{'Name':<25}{'Specialization':<20}{'Contact':<15}{'Username':<15}")
    print("-" * 85)
    for doc in doctors:
        print(f"{doc['id']:<5}{doc['name']:<25}{doc['specialization']:<20}{doc['contact']:<15}{doc['username']:<15}")
    print("-" * 85)
    return doctors

def get_doctor_id_from_user_id(user_id):
    """Helper function to find a doctor's profile ID from their user ID."""
    query = "SELECT id FROM doctors WHERE user_id = %s"
    result = execute_query(query, (user_id,), fetch='one')
    return result['id'] if result else None

# ... (at the end of the file)
def create_doctor_profile(name, specialization, contact, username, password):
    """
    Non-interactive function to create a new doctor user and profile.
    Returns the new doctor's ID on success, None on failure.
    """
    try:
        # Step 1: Create the User
        password_hash = hash_password(password)
        user_query = "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)"
        user_id = execute_query(user_query, (username, password_hash, 'Doctor'))

        if not user_id:
            raise Exception("Username may already be taken.")

        # Step 2: Create the Doctor Profile
        doctor_query = "INSERT INTO doctors (user_id, name, specialization, contact) VALUES (%s, %s, %s, %s)"
        doctor_id = execute_query(doctor_query, (user_id, name, specialization, contact))
        
        return doctor_id
    except Exception as e:
        print(f"Error in create_doctor_profile: {e}")
        # In a real app, you might want to roll back the user creation if doctor creation fails.
        return None