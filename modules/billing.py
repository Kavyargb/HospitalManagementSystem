# hospital_system/modules/billing.py

from db.connection import execute_query
from modules.patients import search_patient_by_id
from datetime import datetime

# Let's define some constants for pricing. In a real system, these might be in a config table.
ROOM_PRICES = {
    'General': 100.00,
    'Private': 300.00,
    'ICU': 500.00
}
CONSULTATION_FEE = 150.00 # A fixed fee per appointment for simplicity

def generate_patient_bill():
    """Generates and displays a detailed, itemized bill for a patient."""
    print("\n--- Generate Patient Bill ---")
    patient = search_patient_by_id()
    if not patient:
        return

    patient_id = patient['id']
    total_bill = 0.0
    
    print("\n" + "="*50)
    print(f"           BILL FOR PATIENT: {patient['name']} (ID: {patient_id})")
    print("="*50)
    
    # --- 1. Calculate Room Charges ---
    print("\n--- Room Charges ---")
    room_query = "SELECT type FROM rooms WHERE id = %s"
    room = execute_query(room_query, (patient['room_id'],), fetch='one')
    if room:
        discharge_date = patient['discharge_date'] or datetime.now()
        days_stayed = (discharge_date - patient['admission_date']).days + 1
        room_type = room['type']
        price_per_day = ROOM_PRICES.get(room_type, 0)
        room_total = days_stayed * price_per_day
        total_bill += room_total
        print(f"Room Type: {room_type}")
        print(f"Days Stayed: {days_stayed} day(s) @ ${price_per_day:.2f}/day")
        print(f"Subtotal: ${room_total:.2f}")
    else:
        print("No room assigned.")

    # --- 2. Calculate Consultation Fees ---
    print("\n--- Consultation Fees ---")
    appt_query = "SELECT COUNT(*) as count FROM appointments WHERE patient_id = %s"
    appt_count = execute_query(appt_query, (patient_id,), fetch='one')['count']
    if appt_count > 0:
        consultation_total = appt_count * CONSULTATION_FEE
        total_bill += consultation_total
        print(f"{appt_count} consultation(s) @ ${CONSULTATION_FEE:.2f} each")
        print(f"Subtotal: ${consultation_total:.2f}")
    else:
        print("No consultations recorded.")

    # --- 3. Calculate Lab Test Charges ---
    print("\n--- Lab Test Charges ---")
    lab_query = """
        SELECT lt.name, lt.price FROM lab_reports lr
        JOIN lab_tests lt ON lr.test_id = lt.id
        WHERE lr.patient_id = %s
    """
    lab_tests = execute_query(lab_query, (patient_id,), fetch='all')
    if lab_tests:
        lab_total = sum(test['price'] for test in lab_tests)
        total_bill += lab_total
        for test in lab_tests:
            print(f"- {test['name']:<30} ${test['price']:.2f}")
        print(f"Subtotal: ${lab_total:.2f}")
    else:
        print("No lab tests performed.")

    # --- 4. Calculate Medicine Charges ---
    print("\n--- Pharmacy Charges ---")
    med_query = """
        SELECT m.name, mi.quantity, m.price
        FROM medicine_issued mi
        JOIN medicines m ON mi.medicine_id = m.id
        WHERE mi.patient_id = %s
    """
    medicines_issued = execute_query(med_query, (patient_id,), fetch='all')
    if medicines_issued:
        medicine_total = sum(med['quantity'] * med['price'] for med in medicines_issued)
        total_bill += medicine_total
        for med in medicines_issued:
            item_total = med['quantity'] * med['price']
            print(f"- {med['name']:<20} ({med['quantity']} units) ${item_total:.2f}")
        print(f"Subtotal: ${medicine_total:.2f}")
    else:
        print("No medicines issued.")

    # --- Final Total ---
    print("\n" + "="*50)
    print(f"GRAND TOTAL: ${total_bill:.2f}")
    print("="*50)

    # --- Save Bill to Database ---
    save_choice = input("Do you want to save this bill to the database? (y/n): ").lower()
    if save_choice == 'y':
        bill_query = "INSERT INTO bills (patient_id, total_amount, bill_date) VALUES (%s, %s, %s)"
        execute_query(bill_query, (patient_id, total_bill, datetime.now()))
        print("Bill saved successfully.")

def update_payment_status():
    """Receptionist function to mark a bill as paid."""
    print("\n--- Update Payment Status ---")
    unpaid_query = """
        SELECT b.id, p.name, b.total_amount, b.bill_date
        FROM bills b JOIN patients p ON b.patient_id = p.id
        WHERE b.payment_status = 'Unpaid'
    """
    unpaid_bills = execute_query(unpaid_query, fetch='all')
    
    if not unpaid_bills:
        print("No unpaid bills found.")
        return
        
    print("\n--- Unpaid Bills ---")
    print(f"{'Bill ID':<10}{'Patient Name':<25}{'Amount':<15}{'Date':<20}")
    print("-" * 70)
    for bill in unpaid_bills:
        print(f"{bill['id']:<10}{bill['name']:<25}${bill['total_amount']:<14.2f}{str(bill['bill_date']):<20}")
    print("-" * 70)
    
    try:
        bill_id = int(input("Enter the Bill ID to mark as paid: "))
        update_query = "UPDATE bills SET payment_status = 'Paid' WHERE id = %s"
        execute_query(update_query, (bill_id,))
        print(f"Bill ID {bill_id} has been marked as PAID.")
    except ValueError:
        print("Invalid input. Please enter a number for Bill ID.")
    except Exception as e:
        print(f"An error occurred: {e}")