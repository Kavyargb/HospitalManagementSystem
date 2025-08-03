import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

def get_db_connection():
    """
    Establishes a connection to the MySQL database.
    Returns the connection object or None if connection fails.
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None

def execute_query(query, params=None, fetch=None):
    """
    A helper function to execute queries and manage connections.
    :param query: SQL query string
    :param params: Tuple of parameters for the query
    :param fetch: 'one', 'all', or None (for non-SELECT queries)
    """
    connection = get_db_connection()
    if not connection:
        return None
        
    cursor = connection.cursor(dictionary=True) # dictionary=True returns rows as dicts
    result = None
    try:
        cursor.execute(query, params or ())
        if fetch == 'one':
            result = cursor.fetchone()
        elif fetch == 'all':
            result = cursor.fetchall()
        else:
            connection.commit() # Commit changes for INSERT, UPDATE, DELETE
            result = cursor.lastrowid # Useful for getting the ID of a new record
    except Error as e:
        print(f"Query failed: {e}")
    finally:
        cursor.close()
        connection.close()
    return result