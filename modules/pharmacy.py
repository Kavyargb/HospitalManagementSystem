# hospital_system/modules/pharmacy.py

from db.connection import execute_query
from chemistry.molecule_handler import fetch_and_draw_molecule
from datetime import datetime
import os
import webbrowser

def add_medicine():
    """Pharmacist function to add a new medicine to the stock."""
    print("\n--- Add New Medicine ---")
    try:
        name = input("Enter medicine name (e.g., 'Aspirin'): ").strip()
        quantity = int(input("Enter quantity: "))
        price = float(input("Enter price per unit: "))
        expiry_date_str = input("Enter expiry date (YYYY-MM-DD): ")
        expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()

        # --- Chemistry Integration ---
        smiles, image_path = fetch_and_draw_molecule(name)

        if not smiles:
            print(f"Warning: Could not fetch chemical data for '{name}'.")
            choice = input("Do you want to add it to the database anyway? (y/n): ")
            if choice.lower() != 'y':
                print("Operation cancelled.")
                return
        
        # --- Database Insertion ---
        query = """
            INSERT INTO medicines (name, smiles, image_path, quantity, expiry_date, price)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (name, smiles, image_path, quantity, price, expiry_date)
        execute_query(query, params)
        print(f"\n✅ Medicine '{name}' added to the inventory successfully.")

    except ValueError:
        print("Invalid input. Please check numbers, prices, and dates.")
    except Exception as e:
        print(f"An error occurred: {e}")

def view_medicine_stock():
    """Pharmacist function to view all medicines in stock."""
    query = "SELECT id, name, quantity, price, expiry_date, image_path FROM medicines ORDER BY name"
    medicines = execute_query(query, fetch='all')

    if not medicines:
        print("No medicines found in the inventory.")
        return

    print("\n" + "-"*90)
    print(f"{'ID':<5}{'Name':<25}{'Quantity':<10}{'Price':<10}{'Expires':<15}{'Image Path':<25}")
    print("-" * 90)
    for med in medicines:
        print(f"{med['id']:<5}{med['name']:<25}{med['quantity']:<10}{med['price']:<10}{str(med['expiry_date']):<15}{med.get('image_path', 'N/A'):<25}")
    print("-" * 90)

def issue_medicine():
    """Pharmacist function to issue medicine to a patient."""
    print("\n--- Issue Medicine ---")
    view_medicine_stock() # Show available stock first
    try:
        patient_id = int(input("Enter Patient ID: "))
        medicine_id = int(input("Enter Medicine ID to issue: "))
        quantity_to_issue = int(input("Enter quantity to issue: "))

        # Check current stock
        med = execute_query("SELECT name, quantity FROM medicines WHERE id = %s", (medicine_id,), fetch='one')
        if not med:
            print("Error: Medicine ID not found.")
            return
        if med['quantity'] < quantity_to_issue:
            print(f"Error: Insufficient stock for {med['name']}. Available: {med['quantity']}.")
            return

        # 1. Update stock
        update_query = "UPDATE medicines SET quantity = quantity - %s WHERE id = %s"
        execute_query(update_query, (quantity_to_issue, medicine_id))

        # 2. Record the transaction
        issue_query = """
            INSERT INTO medicine_issued (patient_id, medicine_id, quantity, issue_date)
            VALUES (%s, %s, %s, %s)
        """
        execute_query(issue_query, (patient_id, medicine_id, quantity_to_issue, datetime.now()))

        print(f"\n✅ Successfully issued {quantity_to_issue} units of {med['name']} to Patient ID {patient_id}.")
        print(f"Remaining stock: {med['quantity'] - quantity_to_issue}")

    except ValueError:
        print("Invalid input. Please enter numbers for IDs and quantity.")
    except Exception as e:
        print(f"An error occurred: {e}")
# ... other imports
import os
import webbrowser # Standard library to open files/urls

def view_molecule_image():
    """Lets the user select a medicine and opens its molecule image."""
    print("\n--- View Molecule Structure ---")
    view_medicine_stock()
    
    try:
        medicine_id = int(input("Enter the Medicine ID to view its structure: "))
        med = execute_query("SELECT name, image_path FROM medicines WHERE id = %s", (medicine_id,), fetch='one')

        if not med:
            print("Medicine ID not found.")
            return
            
        image_path = med.get('image_path')
        if not image_path:
            print(f"No molecule image available for {med['name']}.")
            return
            
        if not os.path.exists(image_path):
            print(f"Image file not found at path: {image_path}")
            return
            
        print(f"-> Opening image for {med['name']}...")
        # Use webbrowser to open the file with the default system application
        webbrowser.open(os.path.abspath(image_path))

    except ValueError:
        print("Invalid input. Please enter a number.")
    except Exception as e:
        print(f"An error occurred: {e}")

# ... (at the end of the file)
def add_medicine_to_db(name, quantity, price, expiry_date_str):
    """
    Non-interactive function to add medicine. Ideal for GUI/API use.
    Returns True on success, False on failure.
    """
    try:
        # Validate and convert data types
        quantity = int(quantity)
        price = float(price)
        expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()

        # --- Chemistry Integration ---
        # This is the potentially slow part
        smiles, image_path = fetch_and_draw_molecule(name)

        if not smiles:
            print(f"Warning: Could not fetch chemical data for '{name}'. Adding without it.")
        
        # --- Database Insertion ---
        query = """
            INSERT INTO medicines (name, smiles, image_path, quantity, expiry_date, price)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (name, smiles, image_path, quantity, price, expiry_date)
        execute_query(query, params)
        return True

    except Exception as e:
        print(f"Error in add_medicine_to_db: {e}")
        return False