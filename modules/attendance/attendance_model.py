import sqlite3
from datetime import datetime
import database


class AttendanceModel:
    def __init__(self):
        pass
    
    def mark_attendance(self, person_id, person_type, date, status, remarks=''):
        """Insert or replace attendance record."""
        try:
            # Validate inputs
            if person_type not in ['student', 'employee']:
                raise ValueError("Invalid person type")
            if status not in ['present', 'absent', 'leave']:
                raise ValueError("Invalid attendance status")
            
            query = """
                INSERT OR REPLACE INTO attendance 
                (person_id, person_type, date, status, remarks)
                VALUES (?, ?, ?, ?, ?)
            """
            
            with database.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (person_id, person_type, date, status, remarks))
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            print(f"Database error in mark_attendance: {e}")
            raise ValueError(" attendance in karnay main error")
    
    def get_attendance_by_date(self, date, person_type):
        """Get attendance for all persons of given type on given date."""
        try:
            if person_type == 'student':
                query = """
                    SELECT a.person_id, s.full_name, s.registration_number, 
                           s.class_name, a.status, a.remarks
                    FROM attendance a
                    JOIN students s ON a.person_id = s.id
                    WHERE a.date = ? AND a.person_type = 'student'
                    ORDER BY s.class_name, s.full_name
                """
            else:  # employee
                query = """
                    SELECT a.person_id, e.full_name, e.employee_code, 
                           e.designation, a.status, a.remarks
                    FROM attendance a
                    JOIN employees e ON a.person_id = e.id
                    WHERE a.date = ? AND a.person_type = 'employee'
                    ORDER BY e.designation, e.full_name
                """
            
            with database.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (date,))
                results = cursor.fetchall()
                
                attendance_list = []
                for row in results:
                    attendance_dict = {
                        'person_id': row[0],
                        'full_name': row[1],
                        'identifier': row[2],  # registration_number or employee_code
                        'class_or_designation': row[3],
                        'status': row[4],
                        'remarks': row[5] if row[5] else ''
                    }
                    attendance_list.append(attendance_dict)
                
                return attendance_list
                
        except sqlite3.Error as e:
            print(f"Database error in get_attendance_by_date: {e}")
            return []
    
    def get_monthly_summary(self, person_id, person_type, month, year):
        """Get monthly attendance summary for a person."""
        try:
            # Format month and year for LIKE query
            date_pattern = f"{year}-{month.zfill(2)}-%"
            
            query = """
                SELECT 
                    SUM(CASE WHEN status = 'present' THEN 1 ELSE 0 END) as present,
                    SUM(CASE WHEN status = 'absent' THEN 1 ELSE 0 END) as absent,
                    SUM(CASE WHEN status = 'leave' THEN 1 ELSE 0 END) as leave,
                    COUNT(*) as total_days
                FROM attendance 
                WHERE person_id = ? AND person_type = ? AND date LIKE ?
            """
            
            with database.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (person_id, person_type, date_pattern))
                result = cursor.fetchone()
                
                return {
                    'present': result[0] if result[0] else 0,
                    'absent': result[1] if result[1] else 0,
                    'leave': result[2] if result[2] else 0,
                    'total_days': result[3] if result[3] else 0
                }
                
        except sqlite3.Error as e:
            print(f"Database error in get_monthly_summary: {e}")
            return {'present': 0, 'absent': 0, 'leave': 0, 'total_days': 0}
    
    def get_today_present_count(self):
        """Get count of present records for today's date."""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            query = "SELECT COUNT(*) FROM attendance WHERE date = ? AND status = 'present'"
            
            with database.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (today,))
                result = cursor.fetchone()
                return result[0] if result[0] else 0
                
        except sqlite3.Error as e:
            print(f"Database error in get_today_present_count: {e}")
            return 0
    
    def bulk_mark_attendance(self, records, date):
        """Insert multiple attendance records in a single transaction."""
        try:
            query = """
                INSERT OR REPLACE INTO attendance 
                (person_id, person_type, date, status, remarks)
                VALUES (?, ?, ?, ?, ?)
            """
            
            with database.get_connection() as conn:
                cursor = conn.cursor()
                
                # Prepare data for bulk insert
                attendance_data = []
                for record in records:
                    attendance_data.append((
                        record['person_id'],
                        record['person_type'],
                        date,
                        record['status'],
                        record.get('remarks', '')
                    ))
                
                cursor.executemany(query, attendance_data)
                conn.commit()
                return len(attendance_data)
                
        except sqlite3.Error as e:
            print(f"Database error in bulk_mark_attendance: {e}")
            raise ValueError(" attendance in karnay main error")
    
    def get_students_by_class(self, class_name):
        """Get list of active students in given class."""
        try:
            query = """
                SELECT id, full_name, registration_number
                FROM students 
                WHERE class_name = ? AND status = 'active'
                ORDER BY full_name
            """
            
            with database.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, (class_name,))
                results = cursor.fetchall()
                
                students = []
                for row in results:
                    students.append({
                        'id': row[0],
                        'full_name': row[1],
                        'registration_number': row[2]
                    })
                
                return students
                
        except sqlite3.Error as e:
            print(f"Database error in get_students_by_class: {e}")
            return []
    
    def get_all_classes(self):
        """Get list of class names from classes table."""
        try:
            query = "SELECT class_name FROM classes ORDER BY class_name"
            
            with database.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                results = cursor.fetchall()
                return [row[0] for row in results]
                
        except sqlite3.Error as e:
            print(f"Database error in get_all_classes: {e}")
            return []
    
    def get_all_employees_list(self):
        """Get list of active employees."""
        try:
            query = """
                SELECT id, full_name, employee_code, designation
                FROM employees 
                WHERE status = 'active'
                ORDER BY designation, full_name
            """
            
            with database.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query)
                results = cursor.fetchall()
                
                employees = []
                for row in results:
                    employees.append({
                        'id': row[0],
                        'full_name': row[1],
                        'employee_code': row[2],
                        'designation': row[3]
                    })
                
                return employees
                
        except sqlite3.Error as e:
            print(f"Database error in get_all_employees_list: {e}")
            return []
