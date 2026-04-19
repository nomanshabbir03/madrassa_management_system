import sys
import os
import unittest
import sqlite3

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestMadrassaSystem(unittest.TestCase):
    
    def test_database_connection(self):
        """Test if database can be connected and tables exist."""
        from database import get_connection
        conn = get_connection()
        self.assertIsNotNone(conn)
        
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        
        required_tables = ['students', 'employees', 'attendance', 'fees', 'donations', 'exams', 'results']
        for table in required_tables:
            self.assertIn(table, tables, f"Table {table} is missing from database")
        
        conn.close()

    def test_imports(self):
        """Test if all major modules can be imported without errors."""
        try:
            from modules.students.student_model import StudentModel
            from modules.employees.employee_model import EmployeeModel
            from modules.attendance.attendance_model import AttendanceModel
            from modules.fees.fee_model import FeeModel
            from modules.donations.donations_model import DonationModel
            from modules.exams.exam_model import ExamModel
            from modules.reports.report_generator import ReportGenerator
        except ImportError as e:
            self.fail(f"Import failed: {str(e)}")

    def test_urdu_numeric_conversion(self):
        """Test Urdu numeric utility."""
        from ui.utils import to_urdu_numerals
        self.assertEqual(to_urdu_numerals("123"), "۱۲۳")
        self.assertEqual(to_urdu_numerals(456), "۴۵۶")

    def test_date_standardization(self):
        """Test date conversion utility."""
        from ui.utils import format_date_urdu
        # Assuming YYYY-MM-DD -> DD-MM-YYYY in Urdu Numerals
        self.assertEqual(format_date_urdu("2024-05-15"), "۱۵-۰۵-۲۰۲۴")

if __name__ == '__main__':
    unittest.main()
