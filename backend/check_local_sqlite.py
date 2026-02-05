
import sqlite3
import os

def check_local_data():
    db_path = 'hackathon.db'
    if not os.path.exists(db_path):
        print(f"Local database {db_path} not found.")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if workflows table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='workflows';")
        if not cursor.fetchone():
            print("Workflows table does not exist in local SQLite database.")
            return

        cursor.execute("SELECT id, name, created_at FROM workflows;")
        rows = cursor.fetchall()
        
        print(f"--- Local SQLite Data Check ---")
        print(f"Total Workflows found in hackathon.db: {len(rows)}")
        for row in rows:
            print(f"ID: {row[0]} | Name: {row[1]} | Created: {row[2]}")
            
        conn.close()
    except Exception as e:
        print(f"Error checking local database: {e}")

if __name__ == "__main__":
    check_local_data()
