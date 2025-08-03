from db.connection import execute_query
from modules.patients import search_patient_by_id
from datetime import datetime

def add_lab_test():
    """Admin/Lab Tech function to add a new type of lab test."""
    print("\n--- Add New Lab Test Type ---")
    try:
        name = input("Enter test name (e.g., 'Complete Blood Count'): ")
        price = float(input("Enter price for this test: "))
        
        query = "INSERT INTO lab_tests (name, price) VALUES (%s, %s)"
        execute_query(query, (name, price))
        print(f"Lab test '{name}' added successfully.")
        
    except ValueError:
        print("Invalid price. Please enter a number.")
    except Exception as e:
        print(f"An error occurred: {e}")

def list_all_lab_tests():
    """Helper function to list all available lab tests."""
    tests = execute_query("SELECT id, name, price FROM lab_tests", fetch='all')
    if not tests:
        print("No lab tests found in the system.")
        return None
        
    print("\n--- Available Lab Tests ---")
    print(f"{'ID':<5}{'Test Name':<30}{'Price':<10}")
    print("-" * 50)
    for test in tests:
        print(f"{test['id']:<5}{test['name']:<30}{test['price']:<10.2f}")
    print("-" * 50)
    return tests

def assign_test_to_patient():
    """Doctor function to assign a lab test to a patient."""
    print("\n--- Assign Lab Test to Patient ---")
    patient = search_patient_by_id()
    if not patient:
        return
        
    available_tests = list_all_lab_tests()
    if not available_tests:
        return
        
    try:
        test_id = int(input("Enter the Test ID to assign: "))
        # Check if test_id is valid
        if not any(t['id'] == test_id for t in available_tests):
            print("Invalid Test ID.")
            return

        query = "INSERT INTO lab_reports (patient_id, test_id, report_date) VALUES (%s, %s, %s)"
        execute_query(query, (patient['id'], test_id, datetime.now()))
        print(f"Test assigned successfully to patient {patient['name']}.")
        
    except ValueError:
        print("Invalid input. Please enter a number for Test ID.")
    except Exception as e:
        print(f"An error occurred: {e}")

def input_test_result():
    """Lab Tech function to input the result of a pending test."""
    print("\n--- Input Lab Test Result ---")
    # First, show pending tests (those without a result)
    pending_query = """
        SELECT lr.id, p.name AS patient_name, lt.name AS test_name
        FROM lab_reports lr
        JOIN patients p ON lr.patient_id = p.id
        JOIN lab_tests lt ON lr.test_id = lt.id
        WHERE lr.result IS NULL
    """
    pending_tests = execute_query(pending_query, fetch='all')
    
    if not pending_tests:
        print("No pending lab tests found.")
        return
        
    print("\n--- Pending Lab Tests ---")
    print(f"{'Report ID':<10}{'Patient Name':<25}{'Test Name':<30}")
    print("-" * 65)
    for test in pending_tests:
        print(f"{test['id']:<10}{test['patient_name']:<25}{test['test_name']:<30}")
    print("-" * 65)
    
    try:
        report_id = int(input("Enter the Report ID to update: "))
        result = input("Enter the test result: ")
        
        update_query = "UPDATE lab_reports SET result = %s WHERE id = %s"
        execute_query(update_query, (result, report_id))
        print(f"Result for Report ID {report_id} updated successfully.")
        
    except ValueError:
        print("Invalid input. Please enter a number for Report ID.")
    except Exception as e:
        print(f"An error occurred: {e}")