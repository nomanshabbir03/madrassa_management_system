import sqlite3
import os

def migrate_donations_table():
    """Update existing donations table to match new schema."""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'madrassa.db')
    
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Check if table exists and get current schema
            cursor.execute("PRAGMA table_info(donations)")
            columns = [row[1] for row in cursor.fetchall()]
            
            print(f"Current columns: {columns}")
            
            # Add missing columns if they don't exist
            if 'donor_contact' not in columns:
                cursor.execute("ALTER TABLE donations ADD COLUMN donor_contact TEXT")
                print("Added donor_contact column")
            
            if 'donation_type' not in columns:
                cursor.execute("ALTER TABLE donations ADD COLUMN donation_type TEXT")
                print("Added donation_type column")
            
            if 'payment_method' not in columns:
                cursor.execute("ALTER TABLE donations ADD COLUMN payment_method TEXT")
                print("Added payment_method column")
            
            if 'donation_date' not in columns:
                cursor.execute("ALTER TABLE donations ADD COLUMN donation_date TEXT")
                print("Added donation_date column")
            
            if 'receipt_number' not in columns:
                cursor.execute("ALTER TABLE donations ADD COLUMN receipt_number TEXT")
                print("Added receipt_number column")
            
            if 'notes' not in columns:
                cursor.execute("ALTER TABLE donations ADD COLUMN notes TEXT")
                print("Added notes column")
            
            if 'created_at' not in columns:
                cursor.execute("ALTER TABLE donations ADD COLUMN created_at TEXT")
                print("Added created_at column")
            
            # Update existing records to have default values
            cursor.execute("UPDATE donations SET donation_date = date WHERE donation_date IS NULL")
            cursor.execute("UPDATE donations SET donation_type = 'General' WHERE donation_type IS NULL")
            cursor.execute("UPDATE donations SET payment_method = 'Cash' WHERE payment_method IS NULL")
            
            conn.commit()
            print("Migration completed successfully!")
            
    except sqlite3.Error as e:
        print(f"Migration error: {e}")

if __name__ == "__main__":
    migrate_donations_table()
