import sqlite3
import datetime
from database import get_connection
from ui.utils import generate_registration_number


class StudentModel:
    def __init__(self):
        pass

    def add_student(self, data: dict) -> int:
        """Add a new student record to the database."""
        if not data.get('full_name', '').strip():
            raise ValueError("Tlby lm kA nm lzmy hy")
        if not data.get('class_name', '').strip():
            raise ValueError("drjh kA intxAb lzmy hy")
        
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Generate registration number
            registration_number = generate_registration_number(conn)
            
            # Insert student record
            cursor.execute('''
                INSERT INTO students (
                    registration_number, full_name, father_name, date_of_birth,
                    cnic_or_bform, address, phone_number, class_name,
                    admission_date, status, photo_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                registration_number,
                data['full_name'],
                data.get('father_name', ''),
                data.get('date_of_birth', ''),
                data.get('cnic_or_bform', ''),
                data.get('address', ''),
                data.get('phone_number', ''),
                data['class_name'],
                data.get('admission_date', datetime.date.today().strftime('%Y-%m-%d')),
                'active',
                data.get('photo_path', '')
            ))
            
            student_id = cursor.lastrowid
            conn.commit()
            return student_id
            
        except sqlite3.IntegrityError:
            raise ValueError("yh Tlby lm phly sE mwjwd hy")
        except Exception as e:
            raise ValueError(f"Tlby lm zd krny myN xtyA: {str(e)}")
        finally:
            if conn:
                conn.close()

    def get_all_students(self, search=None, class_filter=None, status_filter='active'):
        """Get all students with optional filtering."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            query = '''
                SELECT id, registration_number, full_name, father_name, 
                       class_name, phone_number, admission_date, status
                FROM students
                WHERE 1=1
            '''
            params = []
            
            if search:
                query += ' AND (full_name LIKE ? OR registration_number LIKE ?)'
                params.extend([f'%{search}%', f'%{search}%'])
            
            if class_filter:
                query += ' AND class_name = ?'
                params.append(class_filter)
            
            if status_filter:
                query += ' AND status = ?'
                params.append(status_filter)
            
            query += ' ORDER BY id DESC'
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert to list of dicts
            students = []
            for row in rows:
                students.append({
                    'id': row[0],
                    'registration_number': row[1],
                    'full_name': row[2],
                    'father_name': row[3],
                    'class_name': row[4],
                    'phone_number': row[5],
                    'admission_date': row[6],
                    'status': row[7]
                })
            
            return students
            
        except Exception as e:
            raise ValueError(f"TlbyAm wAps krny myN xtyA: {str(e)}")
        finally:
            if conn:
                conn.close()

    def get_student_by_id(self, student_id: int):
        """Get a single student by ID with all fields."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, registration_number, full_name, father_name, date_of_birth,
                       cnic_or_bform, address, phone_number, class_name, admission_date,
                       status, photo_path
                FROM students WHERE id = ?
            ''', (student_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'registration_number': row[1],
                    'full_name': row[2],
                    'father_name': row[3],
                    'date_of_birth': row[4],
                    'cnic_or_bform': row[5],
                    'address': row[6],
                    'phone_number': row[7],
                    'class_name': row[8],
                    'admission_date': row[9],
                    'status': row[10],
                    'photo_path': row[11]
                }
            return None
            
        except Exception as e:
            raise ValueError(f"Tlby lm wAps krny myN xtyA: {str(e)}")
        finally:
            if conn:
                conn.close()

    def update_student(self, student_id: int, data: dict) -> bool:
        """Update an existing student record."""
        if not data.get('full_name', '').strip():
            raise ValueError("Tlby lm kA nm lzmy hy")
        if not data.get('class_name', '').strip():
            raise ValueError("drjh kA intxAb lzmy hy")
        
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE students SET
                    full_name = ?, father_name = ?, date_of_birth = ?,
                    cnic_or_bform = ?, address = ?, phone_number = ?,
                    class_name = ?, photo_path = ?
                WHERE id = ?
            ''', (
                data['full_name'],
                data.get('father_name', ''),
                data.get('date_of_birth', ''),
                data.get('cnic_or_bform', ''),
                data.get('address', ''),
                data.get('phone_number', ''),
                data['class_name'],
                data.get('photo_path', ''),
                student_id
            ))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            raise ValueError(f"Tlby lm tHyr krny myN xtyA: {str(e)}")
        finally:
            if conn:
                conn.close()

    def delete_student(self, student_id: int) -> bool:
        """Soft delete a student by setting status to 'left'."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE students SET status = 'left' WHERE id = ?
            ''', (student_id,))
            
            conn.commit()
            return cursor.rowcount > 0
            
        except Exception as e:
            raise ValueError("Tlby lm hzf krny myN xtyA")
        finally:
            if conn:
                conn.close()

    def get_classes(self):
        """Get list of all class names from classes table."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT class_name FROM classes ORDER BY class_name')
            rows = cursor.fetchall()
            
            return [row[0] for row in rows if row[0]]
            
        except Exception as e:
            raise ValueError(f"drjyAn wAps krny myN xtyA: {str(e)}")
        finally:
            if conn:
                conn.close()

    def get_student_count(self) -> int:
        """Get total count of active students."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM students WHERE status = ?', ('active',))
            count = cursor.fetchone()[0]
            
            return count
            
        except Exception as e:
            raise ValueError(f"TlbyAm tEdAd wAps krny myN xtyA: {str(e)}")
        finally:
            if conn:
                conn.close()

    def search_students(self, query: str):
        """Search students by name, registration number, or father name."""
        conn = None
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            search_term = f'%{query}%'
            cursor.execute('''
                SELECT id, registration_number, full_name, father_name, 
                       class_name, phone_number, admission_date, status
                FROM students
                WHERE (full_name LIKE ? OR registration_number LIKE ? OR father_name LIKE ?)
                AND status = 'active'
                ORDER BY full_name
            ''', (search_term, search_term, search_term))
            
            rows = cursor.fetchall()
            
            # Convert to list of dicts
            students = []
            for row in rows:
                students.append({
                    'id': row[0],
                    'registration_number': row[1],
                    'full_name': row[2],
                    'father_name': row[3],
                    'class_name': row[4],
                    'phone_number': row[5],
                    'admission_date': row[6],
                    'status': row[7]
                })
            
            return students
            
        except Exception as e:
            raise ValueError(f"TlbyAm tLAs krny myN xtyA: {str(e)}")
        finally:
            if conn:
                conn.close()
