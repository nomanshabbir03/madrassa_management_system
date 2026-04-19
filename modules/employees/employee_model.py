import sqlite3
from datetime import datetime
from database import get_connection
from ui.utils import generate_employee_code


class EmployeeModel:
    
    @staticmethod
    def add_employee(data: dict) -> int:
        """Opens connection, inserts a new employee record"""
        if not data.get('full_name'):
            raise ValueError("ملازم کا نام لازمی ہے")
        if not data.get('designation'):
            raise ValueError("عہدہ لازمی ہے")
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            employee_code = generate_employee_code(conn)
            
            cursor.execute("""
                INSERT INTO employees (
                    employee_code, full_name, father_name, cnic, designation, 
                    qualification, joining_date, salary, phone_number, address, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                employee_code,
                data['full_name'],
                data.get('father_name', ''),
                data.get('cnic', ''),
                data['designation'],
                data.get('qualification', ''),
                data.get('joining_date', datetime.now().strftime('%Y-%m-%d')),
                data.get('salary', 0),
                data.get('phone_number', ''),
                data.get('address', ''),
                'active'
            ))
            
            conn.commit()
            return cursor.lastrowid
            
        except sqlite3.IntegrityError:
            raise ValueError("یہ ملازم پہلے سے موجود ہے")
        finally:
            conn.close()
    
    @staticmethod
    def get_all_employees(search=None, designation_filter=None, status_filter='active') -> list:
        """Returns list of dicts with employee information"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            query = """
                SELECT id, employee_code, full_name, father_name, designation, 
                       salary, phone_number, joining_date, status
                FROM employees
                WHERE 1=1
            """
            params = []
            
            if search:
                query += " AND (full_name LIKE ? OR employee_code LIKE ?)"
                params.extend([f'%{search}%', f'%{search}%'])
            
            if designation_filter:
                query += " AND designation = ?"
                params.append(designation_filter)
            
            if status_filter:
                query += " AND status = ?"
                params.append(status_filter)
            
            query += " ORDER BY id DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
            
        finally:
            conn.close()
    
    @staticmethod
    def get_employee_by_id(employee_id: int) -> dict:
        """Returns single employee as dict with ALL fields"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM employees WHERE id = ?", (employee_id,))
            row = cursor.fetchone()
            
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
            
        finally:
            conn.close()
    
    @staticmethod
    def update_employee(employee_id: int, data: dict) -> bool:
        """Updates existing employee record"""
        if not data.get('full_name'):
            raise ValueError("ملازم کا نام لازمی ہے")
        if not data.get('designation'):
            raise ValueError("عہدہ لازمی ہے")
        
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE employees SET
                    full_name = ?, father_name = ?, cnic = ?, designation = ?,
                    qualification = ?, joining_date = ?, salary = ?,
                    phone_number = ?, address = ?
                WHERE id = ?
            """, (
                data['full_name'],
                data.get('father_name', ''),
                data.get('cnic', ''),
                data['designation'],
                data.get('qualification', ''),
                data.get('joining_date', datetime.now().strftime('%Y-%m-%d')),
                data.get('salary', 0),
                data.get('phone_number', ''),
                data.get('address', ''),
                employee_id
            ))
            
            conn.commit()
            return cursor.rowcount > 0
            
        finally:
            conn.close()
    
    @staticmethod
    def delete_employee(employee_id: int) -> bool:
        """Soft delete - sets status to 'left'"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("UPDATE employees SET status = 'left' WHERE id = ?", (employee_id,))
            conn.commit()
            
            if cursor.rowcount == 0:
                raise ValueError("ملازم کو حذف کرنے میں خطا")
            
            return True
            
        except Exception:
            raise ValueError("ملازم کو حذف کرنے میں خطا")
        finally:
            conn.close()
    
    @staticmethod
    def get_designations() -> list:
        """Returns a hardcoded list of Urdu designation strings for dropdown"""
        return ["استاد", "ناظم", "محاسب", "چپراسی", "باورچی", "محافظ", "صفائی کارکن", "دیگر"]
    
    @staticmethod
    def get_employee_count() -> int:
        """Returns total count of active employees as integer"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM employees WHERE status = 'active'")
            return cursor.fetchone()[0]
        finally:
            conn.close()
    
    @staticmethod
    def search_employees(query: str) -> list:
        """Returns employees matching query in full_name, employee_code, or father_name"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM employees 
                WHERE full_name LIKE ? OR employee_code LIKE ? OR father_name LIKE ?
                ORDER BY full_name
            """, (f'%{query}%', f'%{query}%', f'%{query}%'))
            
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
            
        finally:
            conn.close()
