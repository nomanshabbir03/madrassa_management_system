import sqlite3
from datetime import datetime, date, timedelta
from database import get_connection

class ExamModel:
    def __init__(self):
        self.conn = get_connection()

    def get_all_exams(self, filters=None):
        """Return all exams with class_name and subject_name joined."""
        try:
            cursor = self.conn.cursor()
            query = """
                SELECT e.*, c.class_name, s.subject_name
                FROM exams e
                JOIN classes c ON e.class_id = c.id
                JOIN subjects s ON e.subject_id = s.id
                WHERE 1=1
            """
            params = []
            if filters:
                if filters.get('class_id'):
                    query += " AND e.class_id = ?"
                    params.append(filters['class_id'])
                if filters.get('subject_id'):
                    query += " AND e.subject_id = ?"
                    params.append(filters['subject_id'])
                if filters.get('exam_type'):
                    query += " AND e.exam_type = ?"
                    params.append(filters['exam_type'])
                if filters.get('date_from'):
                    query += " AND e.exam_date >= ?"
                    params.append(filters['date_from'])
                if filters.get('date_to'):
                    query += " AND e.exam_date <= ?"
                    params.append(filters['date_to'])
            
            query += " ORDER BY e.exam_date DESC"
            cursor.execute(query, params)
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error in get_all_exams: {e}")
            return []

    def get_exam_by_id(self, exam_id):
        """Return single exam record as dict with class_name and subject_name."""
        try:
            cursor = self.conn.cursor()
            query = """
                SELECT e.*, c.class_name, s.subject_name
                FROM exams e
                JOIN classes c ON e.class_id = c.id
                JOIN subjects s ON e.subject_id = s.id
                WHERE e.id = ?
            """
            cursor.execute(query, (exam_id,))
            row = cursor.fetchone()
            if row:
                columns = [column[0] for column in cursor.description]
                return dict(zip(columns, row))
            return None
        except sqlite3.Error as e:
            print(f"Error in get_exam_by_id: {e}")
            return None

    def add_exam(self, exam_name, class_id, subject_id, exam_date, total_marks, passing_marks, exam_type):
        """Insert new exam record."""
        try:
            cursor = self.conn.cursor()
            query = """
                INSERT INTO exams (exam_name, class_id, subject_id, exam_date, total_marks, passing_marks, exam_type, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(query, (exam_name, class_id, subject_id, exam_date, total_marks, passing_marks, exam_type, created_at))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error in add_exam: {e}")
            self.conn.rollback()
            return None

    def update_exam(self, exam_id, **kwargs):
        """Update exam record by id."""
        try:
            if not kwargs:
                return False
            cursor = self.conn.cursor()
            fields = []
            params = []
            for key, value in kwargs.items():
                fields.append(f"{key} = ?")
                params.append(value)
            
            params.append(exam_id)
            query = f"UPDATE exams SET {', '.join(fields)} WHERE id = ?"
            cursor.execute(query, params)
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error in update_exam: {e}")
            self.conn.rollback()
            return False

    def delete_exam(self, exam_id):
        """Hard delete exam record (also cascade delete related results)."""
        try:
            cursor = self.conn.cursor()
            # Results are deleted manually since foreign keys might not be enabled or set up for cascade in all environments
            cursor.execute("DELETE FROM results WHERE exam_id = ?", (exam_id,))
            cursor.execute("DELETE FROM exams WHERE id = ?", (exam_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error in delete_exam: {e}")
            self.conn.rollback()
            return False

    def get_exams_by_class(self, class_id):
        """Return all exams for specific class."""
        try:
            cursor = self.conn.cursor()
            query = "SELECT * FROM exams WHERE class_id = ? ORDER BY exam_date DESC"
            cursor.execute(query, (class_id,))
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error in get_exams_by_class: {e}")
            return []

    def get_exam_types_summary(self):
        """Return count of exams by type: {'ماہانہ': X, 'سہ ماہی': Y, ...}."""
        try:
            cursor = self.conn.cursor()
            query = "SELECT exam_type, COUNT(*) as count FROM exams GROUP BY exam_type"
            cursor.execute(query)
            results = cursor.fetchall()
            summary = {'ماہانہ': 0, 'سہ ماہی': 0, 'ششماہی': 0, 'سالانہ': 0}
            for row in results:
                if row[0] in summary:
                    summary[row[0]] = row[1]
            return summary
        except sqlite3.Error as e:
            print(f"Error in get_exam_types_summary: {e}")
            return {}

    def get_upcoming_exams(self, days=7):
        """Return exams scheduled within next N days from today."""
        try:
            today = date.today().strftime("%Y-%m-%d")
            future_date = (date.today() + timedelta(days=days)).strftime("%Y-%m-%d")
            cursor = self.conn.cursor()
            query = """
                SELECT e.*, c.class_name, s.subject_name
                FROM exams e
                JOIN classes c ON e.class_id = c.id
                JOIN subjects s ON e.subject_id = s.id
                WHERE e.exam_date >= ? AND e.exam_date <= ?
                ORDER BY e.exam_date ASC
            """
            cursor.execute(query, (today, future_date))
            columns = [column[0] for column in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Error in get_upcoming_exams: {e}")
            return []

    def get_this_month_exams_count(self):
        """Return count of exams in the current month."""
        try:
            today = date.today()
            first_day = today.replace(day=1).strftime("%Y-%m-%d")
            # Handling end of month for next month calculation or just using string matching
            month_pattern = today.strftime("%Y-%m-") + "%"
            
            cursor = self.conn.cursor()
            query = "SELECT COUNT(*) FROM exams WHERE exam_date LIKE ?"
            cursor.execute(query, (month_pattern,))
            result = cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            print(f"Error in get_this_month_exams_count: {e}")
            return 0

    def get_classes(self):
        """Get list of all classes."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, class_name FROM classes ORDER BY class_name")
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error in get_classes: {e}")
            return []

    def get_subjects_by_class(self, class_id):
        """Get list of subjects for a specific class."""
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT id, subject_name FROM subjects WHERE class_id = ? ORDER BY subject_name", (class_id,))
            return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error in get_subjects_by_class: {e}")
            return []
            
    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()
