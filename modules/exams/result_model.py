import sqlite3
from datetime import datetime
from database import get_connection

class ResultModel:
    def __init__(self):
        self.conn = get_connection()

    def _get_exam_marks_config(self, exam_id):
        """Internal helper to get total and passing marks for an exam."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT total_marks, passing_marks FROM exams WHERE id = ?", (exam_id,))
        row = cursor.fetchone()
        if row:
            return row[0], row[1]
        return 100, 40 # Defaults

    def _calculate_grade_and_status(self, obtained_marks, total_marks, passing_marks):
        """Internal helper to calculate grade and status."""
        percentage = (obtained_marks / total_marks) * 100
        
        if percentage >= 90: grade = 'A+'
        elif percentage >= 80: grade = 'A'
        elif percentage >= 70: grade = 'B'
        elif percentage >= 60: grade = 'C'
        elif percentage >= 50: grade = 'D'
        else: grade = 'F'
        
        status = 'پاس' if obtained_marks >= passing_marks else 'فیل'
        return grade, status

    def get_all_results(self, exam_id=None, student_id=None):
        """Return all results with student_name and exam_name joined."""
        try:
            cursor = self.conn.cursor()
            query = """
                SELECT r.*, s.full_name as student_name, s.registration_number, e.exam_name
                FROM results r
                JOIN students s ON r.student_id = s.id
                JOIN exams e ON r.exam_id = e.id
                WHERE 1=1
            """
            params = []
            if exam_id:
                query += " AND r.exam_id = ?"
                params.append(exam_id)
            if student_id:
                query += " AND r.student_id = ?"
                params.append(student_id)
            
            cursor.execute(query, params)
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error in get_all_results: {e}")
            return []

    def get_result_by_id(self, result_id):
        """Return single result record as dict."""
        try:
            cursor = self.conn.cursor()
            query = "SELECT * FROM results WHERE id = ?"
            cursor.execute(query, (result_id,))
            row = cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
            return None
        except sqlite3.Error as e:
            print(f"Error in get_result_by_id: {e}")
            return None

    def get_student_results(self, student_id):
        """Return all results for specific student with exam details."""
        try:
            cursor = self.conn.cursor()
            query = """
                SELECT r.*, e.exam_name, e.exam_date, e.total_marks, e.passing_marks
                FROM results r
                JOIN exams e ON r.exam_id = e.id
                WHERE r.student_id = ?
                ORDER BY e.exam_date DESC
            """
            cursor.execute(query, (student_id,))
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error in get_student_results: {e}")
            return []

    def add_result(self, exam_id, student_id, obtained_marks, remarks=""):
        """Insert new result record."""
        try:
            total_marks, passing_marks = self._get_exam_marks_config(exam_id)
            grade, status = self._calculate_grade_and_status(obtained_marks, total_marks, passing_marks)
            
            cursor = self.conn.cursor()
            query = """
                INSERT INTO results (exam_id, student_id, obtained_marks, grade, status, remarks, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(query, (exam_id, student_id, obtained_marks, grade, status, remarks, created_at))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error in add_result: {e}")
            self.conn.rollback()
            return None

    def update_result(self, result_id, obtained_marks, remarks=""):
        """Update result and recalculate grade/status."""
        try:
            cursor = self.conn.cursor()
            # Fetch exam_id first to get marks config
            cursor.execute("SELECT exam_id FROM results WHERE id = ?", (result_id,))
            row = cursor.fetchone()
            if not row: return False
            exam_id = row[0]
            
            total_marks, passing_marks = self._get_exam_marks_config(exam_id)
            grade, status = self._calculate_grade_and_status(obtained_marks, total_marks, passing_marks)
            
            query = """
                UPDATE results 
                SET obtained_marks = ?, grade = ?, status = ?, remarks = ?
                WHERE id = ?
            """
            cursor.execute(query, (obtained_marks, grade, status, remarks, result_id))
            self.conn.commit()
            return self.get_result_by_id(result_id)
        except sqlite3.Error as e:
            print(f"Error in update_result: {e}")
            self.conn.rollback()
            return False

    def delete_result(self, result_id):
        """Hard delete result record."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM results WHERE id = ?", (result_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error in delete_result: {e}")
            self.conn.rollback()
            return False

    def get_exam_statistics(self, exam_id):
        """Return statistics for a specific exam."""
        try:
            cursor = self.conn.cursor()
            query = """
                SELECT 
                    COUNT(*) as total_students,
                    SUM(CASE WHEN status = 'پاس' THEN 1 ELSE 0 END) as passed_count,
                    SUM(CASE WHEN status = 'فیل' THEN 1 ELSE 0 END) as failed_count,
                    MAX(obtained_marks) as highest_marks,
                    MIN(obtained_marks) as lowest_marks,
                    AVG(obtained_marks) as average_marks
                FROM results
                WHERE exam_id = ?
            """
            cursor.execute(query, (exam_id,))
            row = cursor.fetchone()
            if row and row[0] > 0:
                return {
                    'total_students': row[0],
                    'passed_count': row[1] or 0,
                    'failed_count': row[2] or 0,
                    'highest_marks': row[3] or 0,
                    'lowest_marks': row[4] or 0,
                    'average_marks': round(row[5], 2) if row[5] else 0,
                    'pass_percentage': round((row[1] / row[0]) * 100, 2) if row[1] else 0
                }
            return None
        except sqlite3.Error as e:
            print(f"Error in get_exam_statistics: {e}")
            return None

    def get_class_performance(self, class_id):
        """Return average marks for each subject in the class."""
        try:
            cursor = self.conn.cursor()
            query = """
                SELECT s.subject_name, AVG(r.obtained_marks) as avg_marks
                FROM results r
                JOIN exams e ON r.exam_id = e.id
                JOIN subjects s ON e.subject_id = s.id
                WHERE e.class_id = ?
                GROUP BY s.subject_name
            """
            cursor.execute(query, (class_id,))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error in get_class_performance: {e}")
            return []

    def bulk_add_results(self, exam_id, results_list):
        """Add multiple results in single transaction."""
        try:
            total_marks, passing_marks = self._get_exam_marks_config(exam_id)
            cursor = self.conn.cursor()
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            data = []
            for res in results_list:
                grade, status = self._calculate_grade_and_status(res['obtained_marks'], total_marks, passing_marks)
                data.append((
                    exam_id, res['student_id'], res['obtained_marks'], 
                    grade, status, res.get('remarks', ''), created_at
                ))
            
            for res in results_list:
                cursor.execute("DELETE FROM results WHERE exam_id = ? AND student_id = ?", (exam_id, res['student_id']))
                
            query = """
                INSERT INTO results (exam_id, student_id, obtained_marks, grade, status, remarks, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            cursor.executemany(query, data)
            self.conn.commit()
            return len(data)
        except sqlite3.Error as e:
            print(f"Error in bulk_add_results: {e}")
            self.conn.rollback()
            return 0

    def get_students_by_class(self, class_id):
        """Get list of active students in given class."""
        try:
            # We need to find the class_name from class_id since students table uses class_name string
            cursor = self.conn.cursor()
            cursor.execute("SELECT class_name FROM classes WHERE id = ?", (class_id,))
            row = cursor.fetchone()
            if not row: return []
            class_name = row[0]
            
            query = """
                SELECT id, full_name, registration_number
                FROM students 
                WHERE class_name = ? AND status = 'active'
                ORDER BY full_name
            """
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

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()
