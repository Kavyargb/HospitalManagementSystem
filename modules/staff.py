# hospital_system/modules/staff.py

from db.connection import execute_query
# We use the existing create_user function as our backend logic
from auth.login import create_user 

def create_staff_member():
    """Admin's interactive CLI function to create a new staff member."""
    print("\n--- Create New Staff Account ---")
    
    # Define the roles an admin can create
    creatable_roles = ['Receptionist', 'Pharmacist', 'Lab Tech']
    
    print("Select a role for the new staff member:")
    for i, role in enumerate(creatable_roles, 1):
        print(f"{i}. {role}")

    try:
        choice_index = int(input("Enter choice number: ")) - 1
        if not 0 <= choice_index < len(creatable_roles):
            print("Invalid choice.")
            return
        
        selected_role = creatable_roles[choice_index]
        
        username = input(f"Enter username for the new {selected_role}: ")
        password = input("Enter a temporary password: ")

        if not username or not password:
            print("Username and password cannot be empty.")
            return

        # Call the non-interactive backend function to create the user
        create_user(username, password, selected_role)
        # The create_user function already prints success/error messages.

    except ValueError:
        print("Invalid input. Please enter a number.")
    except Exception as e:
        print(f"An error occurred: {e}")