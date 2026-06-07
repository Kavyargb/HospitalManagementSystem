# hospital_system/auth/login.py

import bcrypt
import getpass
from db.connection import execute_query

def hash_password(password):
    """Hashes the password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def check_password(plain_password, hashed_password):
    """Checks if the plain password matches the hashed one."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def login():
    """
    Handles the user login process.
    Prompts for username and password, verifies them against the database.
    Returns user's data upon successful login, otherwise None.
    """
    print("\n--- HMS Login ---")
    username = input("Username: ")
    password = getpass.getpass("Password: ") # Hides password input

    # Fetch user from the database
    query = "SELECT id, username, password_hash, role FROM users WHERE username = %s"
    user = execute_query(query, (username.lower().strip() if username else "",), fetch='one')

    if user and check_password(password, user['password_hash']):
        print(f"\nWelcome, {user['username']}! (Role: {user['role']})")
        return user  # Return user data dictionary
    else:
        print("Invalid username or password. Please try again.")
        return None

# --- Helper function for creating users (for testing) ---
def create_user(username, password, role):
    """A utility function to add new users to the database."""
    # Validate role
    valid_roles = ['Admin', 'Doctor', 'Receptionist', 'Pharmacist', 'Lab Tech']
    if role not in valid_roles:
        print(f"Error: Invalid role '{role}'. Must be one of {valid_roles}")
        return None

    password_hash = hash_password(password)
    query = "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)"
    try:
        user_id = execute_query(query, (username.lower().strip() if username else "", password_hash, role))
        print(f"User '{username}' created successfully with ID: {user_id}")
        return user_id
    except Exception as e:
        # This will catch unique constraint violations for username
        print(f"Error creating user '{username}': {e}")
        return None


def check_credentials(username, password):
    """
    Non-interactive function to check credentials.
    Ideal for use with a GUI.
    Returns user dictionary on success, None on failure.
    """
    query = "SELECT id, username, password_hash, role FROM users WHERE username = %s"
    user = execute_query(query, (username.lower().strip() if username else "",), fetch='one')

    if user and check_password(password, user['password_hash']):
        return user
    else:
        return None