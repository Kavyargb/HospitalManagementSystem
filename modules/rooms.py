from db.connection import execute_query

def list_available_rooms():
    """Lists all available rooms."""
    query = "SELECT id, room_number, type FROM rooms WHERE is_available = TRUE"
    rooms = execute_query(query, fetch='all')

    if not rooms:
        print("No available rooms found.")
        return None

    print("\n--- Available Rooms ---")
    print(f"{'ID':<5}{'Room Number':<15}{'Type':<10}")
    print("-" * 35)
    for room in rooms:
        print(f"{room['id']:<5}{room['room_number']:<15}{room['type']:<10}")
    print("-" * 35)
    return rooms

def update_room_status(room_id, is_available):
    """Internal helper to update a room's availability."""
    query = "UPDATE rooms SET is_available = %s WHERE id = %s"
    execute_query(query, (is_available, room_id))