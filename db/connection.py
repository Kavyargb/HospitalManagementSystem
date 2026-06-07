import os
import sqlite3
from config import DB_CONFIG

try:
    import mysql.connector
    from mysql.connector import Error
    _mysql_available = True
except ImportError:
    _mysql_available = False

# Global flag to track if we are running in SQLite mode
_use_sqlite = not _mysql_available

def get_db_connection():
    """
    Establishes a connection to the database.
    Tries MySQL first (using DB_CONFIG).
    If MySQL connection fails, falls back transparently to a local SQLite database (db/hms.db).
    """
    global _use_sqlite
    
    # Try MySQL first if not already locked to SQLite
    if not _use_sqlite and _mysql_available:
        try:
            connection = mysql.connector.connect(**DB_CONFIG)
            if connection.is_connected():
                return connection
        except Exception as e:
            print(f"MySQL connection failed: {e}. Falling back to SQLite database...")
            _use_sqlite = True
    else:
        _use_sqlite = True

    # SQLite Fallback
    try:
        db_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(db_dir, 'hms.db')
        
        # Ensure db directory exists
        os.makedirs(db_dir, exist_ok=True)
        
        # Connect to SQLite
        connection = sqlite3.connect(db_path)
        connection.row_factory = sqlite3.Row
        
        # Check if tables need initialization
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            print("Initializing SQLite database schema...")
            _init_sqlite(connection)
            print("Seeding SQLite database initial data...")
            _seed_sqlite(connection)
            
        return connection
    except Exception as sqle:
        print(f"Failed to connect to SQLite fallback database: {sqle}")
        return None

def _init_sqlite(conn):
    """Parses and converts MySQL DDL schema from db/schema.sql to SQLite syntax and runs it."""
    try:
        schema_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'schema.sql')
        if not os.path.exists(schema_path):
            schema_path = 'db/schema.sql'
            
        with open(schema_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
            
        # Parse and translate to SQLite dialect
        import re
        statements = sql_script.split(';')
        cursor = conn.cursor()
        for statement in statements:
            stmt = statement.strip()
            if not stmt:
                continue
                
            # Skip MySQL specific database statements
            if stmt.upper().startswith("CREATE DATABASE") or stmt.upper().startswith("USE "):
                continue
                
            # Replace MySQL AUTO_INCREMENT with SQLite AUTOINCREMENT style
            # (In SQLite, INTEGER PRIMARY KEY AUTOINCREMENT is the correct form)
            stmt = re.sub(r'`id`\s+INT\s+AUTO_INCREMENT\s+PRIMARY KEY', '`id` INTEGER PRIMARY KEY AUTOINCREMENT', stmt, flags=re.IGNORECASE)
            stmt = re.sub(r'`id`\s+INT\s+AUTO_INCREMENT', '`id` INTEGER PRIMARY KEY AUTOINCREMENT', stmt, flags=re.IGNORECASE)
            
            # Replace ENUMs with TEXT
            stmt = re.sub(r'ENUM\([^)]+\)', 'TEXT', stmt, flags=re.IGNORECASE)
            
            try:
                cursor.execute(stmt)
            except sqlite3.Error as err:
                print(f"SQLite Schema Init Warning on statement: {stmt[:50]}... Error: {err}")
                
        conn.commit()
    except Exception as e:
        print(f"Error during SQLite schema initialization: {e}")

def _seed_sqlite(conn):
    """Seeds the SQLite database with starting data for all 5 roles and baseline records."""
    try:
        import bcrypt
        def hash_pw(password):
            salt = bcrypt.gensalt()
            return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            
        cursor = conn.cursor()
        
        # 1. Seed user accounts for all 5 roles
        roles_to_seed = [
            ('admin', 'admin123', 'Admin'),
            ('doctor', 'doctor123', 'Doctor'),
            ('receptionist', 'receptionist123', 'Receptionist'),
            ('pharmacist', 'pharmacist123', 'Pharmacist'),
            ('labtech', 'labtech123', 'Lab Tech')
        ]
        
        user_ids = {}
        for username, pwd, role in roles_to_seed:
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            exists = cursor.fetchone()
            if not exists:
                hashed = hash_pw(pwd)
                cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)", (username, hashed, role))
                user_ids[role] = cursor.lastrowid
            else:
                user_ids[role] = exists['id']
                
        # 2. Seed Doctor profile
        cursor.execute("SELECT id FROM doctors WHERE user_id = ?", (user_ids['Doctor'],))
        if not cursor.fetchone():
            cursor.execute("INSERT INTO doctors (user_id, name, specialization, contact) VALUES (?, ?, ?, ?)",
                           (user_ids['Doctor'], 'Dr. Gregory House', 'Diagnostic Medicine', '555-0199'))
                           
        # 3. Seed Rooms
        rooms = [
            ('101', 'General', 1),
            ('102', 'General', 1),
            ('201', 'Private', 1),
            ('202', 'Private', 1),
            ('301', 'ICU', 1)
        ]
        for r_num, r_type, r_avail in rooms:
            cursor.execute("SELECT id FROM rooms WHERE room_number = ?", (r_num,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO rooms (room_number, type, is_available) VALUES (?, ?, ?)", (r_num, r_type, r_avail))
                
        # 4. Seed Medicines
        medicines = [
            ('Aspirin', 'CC(=O)OC1=CC=CC=C1C(=O)O', 'static/molecule_images/aspirin.png', 100, '2027-12-31', 2.50),
            ('Amoxicillin', 'CC1(C(N2C(S1)C(C2=O)NC(=O)C(C3=CC=C(C=C3)O)N)C(=O)O)C', 'static/molecule_images/amoxicillin.png', 50, '2026-10-15', 8.00),
            ('Ibuprofen', 'CC(C)CC1=CC=C(C=C1)C(C)C(=O)O', 'static/molecule_images/ibuprofen.png', 150, '2028-05-20', 3.75),
            ('Paracetamol', 'CC(=O)NC1=CC=C(C=C1)O', 'static/molecule_images/paracetamol.png', 200, '2027-08-11', 1.20)
        ]
        for name, smiles, img, qty, exp, price in medicines:
            cursor.execute("SELECT id FROM medicines WHERE name = ?", (name,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO medicines (name, smiles, image_path, quantity, expiry_date, price) VALUES (?, ?, ?, ?, ?, ?)",
                               (name, smiles, img, qty, exp, price))
                               
        # 5. Seed Lab Tests
        tests = [
            ('Complete Blood Count (CBC)', 45.00),
            ('Lipid Panel', 60.00),
            ('Basic Metabolic Panel', 75.00),
            ('X-Ray Chest', 120.00),
            ('MRI Scan Brain', 850.00)
        ]
        for name, price in tests:
            cursor.execute("SELECT id FROM lab_tests WHERE name = ?", (name,))
            if not cursor.fetchone():
                cursor.execute("INSERT INTO lab_tests (name, price) VALUES (?, ?)", (name, price))
                
        conn.commit()
    except Exception as e:
        print(f"Error during SQLite seeding: {e}")

def execute_query(query, params=None, fetch=None):
    """
    A helper function to execute queries and manage connections.
    Translates query placeholders and maps output to dictionaries for SQLite.
    """
    connection = get_db_connection()
    if not connection:
        return None
        
    is_sqlite_conn = isinstance(connection, sqlite3.Connection)
    
    # Translate query parameters if using SQLite
    if is_sqlite_conn:
        # Replace %s syntax with ? for SQLite parameters
        query_to_run = query.replace('%s', '?')
        cursor = connection.cursor()
    else:
        query_to_run = query
        cursor = connection.cursor(dictionary=True)
        
    result = None
    try:
        cursor.execute(query_to_run, params or ())
        if fetch == 'one':
            row = cursor.fetchone()
            if row:
                result = dict(row) if is_sqlite_conn else row
        elif fetch == 'all':
            rows = cursor.fetchall()
            if rows:
                result = [dict(r) for r in rows] if is_sqlite_conn else rows
            else:
                result = []
        else:
            if not is_sqlite_conn:
                connection.commit()
                result = cursor.lastrowid
            else:
                connection.commit()
                result = cursor.lastrowid
    except Exception as e:
        print(f"Query failed: {e}\nQuery was: {query_to_run}\nParams: {params}")
    finally:
        cursor.close()
        connection.close()
    return result