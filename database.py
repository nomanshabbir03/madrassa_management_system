import sqlite3
import os
from PyQt5.QtWidgets import QMessageBox

def get_connection():
    """Get a database connection with foreign keys enabled."""
    try:
        db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'madrassa.db')
        conn = sqlite3.connect(db_path)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        raise

def initialize_database():
    """Initialize all database tables and seed default data."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            
            # Create students table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS students (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    registration_number TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    father_name TEXT,
                    date_of_birth TEXT,
                    cnic_or_bform TEXT,
                    address TEXT,
                    phone_number TEXT,
                    class_name TEXT,
                    admission_date TEXT,
                    status TEXT DEFAULT 'active',
                    photo_path TEXT
                )
            ''')
            
            # Create employees table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_code TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    father_name TEXT,
                    cnic TEXT,
                    designation TEXT,
                    qualification TEXT,
                    joining_date TEXT,
                    salary REAL,
                    phone_number TEXT,
                    address TEXT,
                    status TEXT DEFAULT 'active'
                )
            ''')
            
            # Create attendance table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    person_id INTEGER NOT NULL,
                    person_type TEXT NOT NULL,
                    date TEXT NOT NULL,
                    status TEXT NOT NULL,
                    remarks TEXT
                )
            ''')
            
            # Create fees table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS fees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER NOT NULL,
                    month TEXT NOT NULL,
                    year TEXT NOT NULL,
                    amount REAL NOT NULL,
                    paid_date TEXT,
                    receipt_number TEXT UNIQUE,
                    payment_method TEXT,
                    remarks TEXT,
                    FOREIGN KEY (student_id) REFERENCES students (id)
                )
            ''')
            
            # Create donations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS donations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    donor_name TEXT NOT NULL,
                    amount REAL NOT NULL,
                    date TEXT NOT NULL,
                    purpose TEXT,
                    remarks TEXT
                )
            ''')
            
            # Create classes table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS classes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    class_name TEXT NOT NULL,
                    description TEXT
                )
            ''')
            
            # Create subjects table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS subjects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    subject_name TEXT NOT NULL,
                    class_id INTEGER,
                    FOREIGN KEY (class_id) REFERENCES classes (id)
                )
            ''')
            
            # Create exams table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    exam_name TEXT NOT NULL,
                    class_id INTEGER,
                    date TEXT,
                    total_marks INTEGER,
                    FOREIGN KEY (class_id) REFERENCES classes (id)
                )
            ''')
            
            # Create results table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS results (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    exam_id INTEGER,
                    student_id INTEGER,
                    subject_id INTEGER,
                    obtained_marks INTEGER,
                    remarks TEXT,
                    FOREIGN KEY (exam_id) REFERENCES exams (id),
                    FOREIGN KEY (student_id) REFERENCES students (id),
                    FOREIGN KEY (subject_id) REFERENCES subjects (id)
                )
            ''')
            
            # Seed default classes
            cursor.execute("SELECT COUNT(*) FROM classes")
            if cursor.fetchone()[0] == 0:
                default_classes = [
                    'ناظرہ', 'حفظ', 'درجہ اول', 'درجہ دوم', 'درجہ سوم', 
                    'درجہ چہارم', 'درجہ پنجم', 'درجہ ششم', 'درجہ ہفتم', 'درجہ ہشتم'
                ]
                for class_name in default_classes:
                    cursor.execute("INSERT INTO classes (class_name) VALUES (?)", (class_name,))
                
                # Get all class IDs for subjects
                cursor.execute("SELECT id FROM classes")
                class_ids = [row[0] for row in cursor.fetchall()]
                
                # Seed default subjects for each class
                default_subjects = [
                    'قرآن پاک', 'تجوید', 'عقیدہ', 'فقہ', 'حدیث', 'سیرت', 'اردو', 'حساب'
                ]
                for class_id in class_ids:
                    for subject_name in default_subjects:
                        cursor.execute(
                            "INSERT INTO subjects (subject_name, class_id) VALUES (?, ?)",
                            (subject_name, class_id)
                        )
            
            conn.commit()
            
    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
        raise

def execute_query(query, params=None):
    """Execute a query and return results."""
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if query.strip().upper().startswith(('SELECT', 'PRAGMA')):
                return cursor.fetchall()
            else:
                conn.commit()
                return cursor.lastrowid if cursor.lastrowid else cursor.rowcount
                
    except sqlite3.Error as e:
        print(f"Query execution error: {e}")
        raise

def show_error_message(title, message):
    """Show error message using PyQt5 QMessageBox."""
    try:
        from PyQt5.QtWidgets import QApplication
        if QApplication.instance():
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle(title)
            msg.setText(message)
            msg.exec_()
    except ImportError:
        print(f"{title}: {message}")

if __name__ == "__main__":
    try:
        initialize_database()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Failed to initialize database: {e}")
        show_error_message("Database Error", f"Failed to initialize database: {e}")