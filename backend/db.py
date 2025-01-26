import sqlite3
import os

DATABASE_FILE = 'twitter.db'  # IMPORTANT: Make sure this matches the filename you want

def get_db_connection():
    print("db.py: get_db_connection() called") # LOG: Connection attempt
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    print("db.py: get_db_connection() - Connection established") # LOG: Connection success
    return conn

def init_db():
    print("db.py: init_db() starting...") # LOG: init_db start
    db_exists = os.path.exists(DATABASE_FILE)
    print(f"db.py: init_db() - Database file exists check: {db_exists}") # LOG: db_exists check result
    conn = get_db_connection()
    cursor = conn.cursor()

    if not db_exists:
        print("db.py: init_db() - Database does not exist. Creating and initializing...") # LOG: No DB exists - creating
        try:
            with open('schema.sql', 'r') as f:
                cursor.executescript(f.read())
            conn.commit()
            print("db.py: init_db() - New database created and schema initialized.") # LOG: DB creation success
        except Exception as e:
            print(f"db.py: init_db() - ERROR during database creation/schema init: {e}") # LOG: DB creation ERROR
            conn.close()
            return # Exit init_db on error
    else:
        print("db.py: init_db() - Database already exists. Skipping schema update.") # LOG: DB exists - skipping update
        # COMMENTED OUT SCHEMA RE-EXECUTION - POTENTIAL CAUSE OF DATA LOSS
        # try: # Attempt to run schema script anyway to update schema
        #     with open('schema.sql', 'r') as f:
        #         cursor.executescript(f.read())
        #     conn.commit()
        #     print("db.py: init_db() - Database schema updated.") # Indicate schema update attempt
        # except sqlite3.OperationalError as e: # Catch potential errors during schema update
        #     print(f"db.py: init_db() - Warning: Could not fully update schema (might be already up-to-date or incompatible changes): {e}")

    conn.close()
    print("db.py: init_db() - Connection closed.") # LOG: Connection close
    print("db.py: init_db() - Database created or checked successfully.") # More accurate message
    print("db.py: init_db() finished.") # LOG: init_db finish

if __name__ == '__main__':
    init_db() # Initialize database if running db.py directly
    print("db.py: __main__ - Database initialized or already exists.")