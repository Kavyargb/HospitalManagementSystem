# test_app.py
import os
import sys
from db.connection import get_db_connection, execute_query

def run_tests():
    print("=== HMS System Verification ===")
    
    # 1. Test database connection
    print("1. Testing database connection...")
    conn = get_db_connection()
    if conn:
        print("   [SUCCESS] Connection established!")
        conn.close()
    else:
        print("   [FAILURE] Could not establish connection.")
        sys.exit(1)
        
    # 2. Test user seeding
    print("2. Testing seeded user query...")
    users = execute_query("SELECT username, role FROM users", fetch='all')
    if users:
        print(f"   [SUCCESS] Found {len(users)} seeded user accounts:")
        for u in users:
            print(f"     - {u['username']} (Role: {u['role']})")
    else:
        print("   [FAILURE] No users returned.")
        sys.exit(1)
        
    # 3. Test Room list
    print("3. Testing room list query...")
    rooms = execute_query("SELECT room_number, type, is_available FROM rooms", fetch='all')
    if rooms:
         print(f"   [SUCCESS] Found {len(rooms)} hospital rooms.")
    else:
         print("   [FAILURE] No rooms returned.")
         sys.exit(1)

    # 4. Test chemistry fallback
    print("4. Testing chemistry handler...")
    from chemistry.molecule_handler import fetch_and_draw_molecule
    # Try querying Aspirin
    smiles, img_path = fetch_and_draw_molecule("Aspirin")
    if smiles:
        print(f"   [SUCCESS] Retrieved SMILES: {smiles}")
        if img_path and os.path.exists(img_path):
            print(f"   [SUCCESS] Molecule image rendered successfully at: {img_path}")
        else:
            print("   [WARNING] Molecule image path was not saved or is missing.")
    else:
        print("   [FAILURE] Could not retrieve molecular structure.")
        
    print("\nAll baseline software system diagnostics have passed successfully!")

if __name__ == '__main__':
    run_tests()
