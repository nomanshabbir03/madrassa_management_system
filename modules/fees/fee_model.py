import sqlite3
import random
import string
from datetime import datetime
from database import get_connection
from ui.utils import get_today_date

class FeeModel:
    def __init__(self):
        pass
    
    def get_all_fees(self, filters=None):
        """
        Return all fees with student name joined from students table.
        Support filters: student_id, month, year, payment_method
        Return list of dicts with keys: id, student_id, student_name, amount, month, year, 
        payment_date, payment_method, receipt_number, notes
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT f.id, f.student_id, s.full_name as student_name, 
                           f.amount, f.month, f.year, f.paid_date, 
                           f.payment_method, f.receipt_number, f.remarks
                    FROM fees f
                    JOIN students s ON f.student_id = s.id
                '''
                
                params = []
                conditions = []
                
                if filters:
                    if filters.get('student_id'):
                        conditions.append("f.student_id = ?")
                        params.append(filters['student_id'])
                    if filters.get('month'):
                        conditions.append("f.month = ?")
                        params.append(filters['month'])
                    if filters.get('year'):
                        conditions.append("f.year = ?")
                        params.append(filters['year'])
                    if filters.get('payment_method'):
                        conditions.append("f.payment_method = ?")
                        params.append(filters['payment_method'])
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                
                query += " ORDER BY f.paid_date DESC"
                
                cursor.execute(query, params)
                
                columns = ['id', 'student_id', 'student_name', 'amount', 'month', 'year',
                          'paid_date', 'payment_method', 'receipt_number', 'remarks']
                
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            print(f"تمام فیسز حاصل کرنے میں خرابی: {e}")
            return []
    
    def get_student_fee_history(self, student_id):
        """
        Return all fee records for specific student.
        Order by year DESC, month DESC.
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, amount, month, year, paid_date, 
                           payment_method, receipt_number, remarks
                    FROM fees 
                    WHERE student_id = ?
                    ORDER BY year DESC, month DESC
                ''', (student_id,))
                
                columns = ['id', 'amount', 'month', 'year', 'paid_date',
                          'payment_method', 'receipt_number', 'remarks']
                
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            print(f"طالب علم کی فیس کی تاریخ حاصل کرنے میں خرابی: {e}")
            return []
    
    def get_unpaid_months(self, student_id, year):
        """
        Return list of month numbers (1-12) that are NOT paid for given student and year.
        Compare against fees table where student_id and year match.
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                # Get paid months for this student and year
                cursor.execute('''
                    SELECT month FROM fees 
                    WHERE student_id = ? AND year = ?
                ''', (student_id, str(year)))
                
                paid_months_text = {row[0] for row in cursor.fetchall()}
                
                # Convert text months to numbers for comparison
                paid_months_numbers = set()
                for month_text in paid_months_text:
                    try:
                        # Handle both numeric and text month formats
                        if month_text.isdigit():
                            paid_months_numbers.add(int(month_text))
                        else:
                            # If month is stored as text name, convert to number
                            # This is a fallback - ideally we store as numbers
                            month_map = {
                                'January': 1, 'February': 2, 'March': 3, 'April': 4,
                                'May': 5, 'June': 6, 'July': 7, 'August': 8,
                                'September': 9, 'October': 10, 'November': 11, 'December': 12
                            }
                            if month_text in month_map:
                                paid_months_numbers.add(month_map[month_text])
                    except (ValueError, AttributeError):
                        continue
                
                # Return unpaid months (1-12)
                unpaid_months = []
                for month in range(1, 13):
                    if month not in paid_months_numbers:
                        unpaid_months.append(month)
                
                return unpaid_months
                
        except sqlite3.Error as e:
            print(f"غیر ادا شدہ ماہ حاصل کرنے میں خرابی: {e}")
            return []
    
    def add_fee(self, student_id, amount, month, year, payment_method, notes=""):
        """
        Generate receipt_number format: RCP-YYYYMMDD-XXXX where XXXX is random 4 digits.
        Insert new fee record.
        Return the new fee id and receipt_number.
        """
        try:
            # Generate receipt number
            today = datetime.now()
            date_str = today.strftime("%Y%m%d")
            random_digits = ''.join(random.choices(string.digits, k=4))
            receipt_number = f"RCP-{date_str}-{random_digits}"
            
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO fees (
                        student_id, amount, month, year, paid_date, 
                        payment_method, receipt_number, remarks
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    student_id, amount, str(month), str(year), get_today_date(),
                    payment_method, receipt_number, notes
                ))
                
                fee_id = cursor.lastrowid
                return fee_id, receipt_number
                
        except sqlite3.Error as e:
            print(f"فیس شامل کرنے میں خرابی: {e}")
            raise ValueError("فیس ریکارڈ شامل کرنے میں خرابی")
    
    def update_fee(self, fee_id, **kwargs):
        """
        Update fee record by id.
        Fields: amount, month, year, payment_method, notes
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                # Build dynamic update query
                set_clauses = []
                params = []
                
                for field, value in kwargs.items():
                    if field in ['amount', 'month', 'year', 'payment_method', 'notes']:
                        set_clauses.append(f"{field} = ?")
                        params.append(value)
                
                if not set_clauses:
                    return False
                
                params.append(fee_id)
                
                query = f"UPDATE fees SET {', '.join(set_clauses)} WHERE id = ?"
                cursor.execute(query, params)
                
                return cursor.rowcount > 0
                
        except sqlite3.Error as e:
            print(f"فیس اپ ڈیٹ کرنے میں خرابی: {e}")
            raise ValueError("فیس ریکارڈ اپ ڈیٹ کرنے میں خرابی")
    
    def delete_fee(self, fee_id):
        """
        Hard delete fee record (fees can be hard deleted unlike students/employees).
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM fees WHERE id = ?", (fee_id,))
                
                if cursor.rowcount == 0:
                    raise ValueError("Fee record not found")
                
                return True
                
        except sqlite3.Error as e:
            print(f"فیس حذف کرنے میں خرابی: {e}")
            raise ValueError("فیس ریکارڈ حذف کرنے میں خرابی")
    
    def get_monthly_summary(self, year, month=None):
        """
        If month provided: return total fees for that month.
        If no month: return dict with all 12 months totals for the year.
        Include count of transactions.
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                if month:
                    # Return total for specific month
                    cursor.execute('''
                        SELECT SUM(amount), COUNT(*) 
                        FROM fees 
                        WHERE year = ? AND month = ?
                    ''', (str(year), str(month)))
                    
                    result = cursor.fetchone()
                    return {
                        'total_amount': float(result[0]) if result[0] else 0.0,
                        'transaction_count': result[1] if result[1] else 0
                    }
                else:
                    # Return dict with all 12 months totals
                    monthly_data = {}
                    
                    for month in range(1, 13):
                        cursor.execute('''
                            SELECT SUM(amount), COUNT(*) 
                            FROM fees 
                            WHERE year = ? AND month = ?
                        ''', (str(year), str(month)))
                        
                        result = cursor.fetchone()
                        monthly_data[month] = {
                            'total_amount': float(result[0]) if result[0] else 0.0,
                            'transaction_count': result[1] if result[1] else 0
                        }
                    
                    return monthly_data
                
        except sqlite3.Error as e:
            print(f"ماہانہ خلاصہ حاصل کرنے میں خرابی: {e}")
            return {} if month is None else {'total_amount': 0.0, 'transaction_count': 0}
    
    def get_student_balance(self, student_id):
        """
        Calculate total fees paid vs expected (assume monthly fee is consistent).
        For now, return dict: {'total_paid': X, 'total_months_paid': Y}
        """
        try:
            with get_connection() as conn:
                cursor = conn.cursor()
                
                # Get total paid amount and count of months
                cursor.execute('''
                    SELECT SUM(amount), COUNT(DISTINCT month) 
                    FROM fees 
                    WHERE student_id = ?
                ''', (student_id,))
                
                result = cursor.fetchone()
                
                return {
                    'total_paid': float(result[0]) if result[0] else 0.0,
                    'total_months_paid': result[1] if result[1] else 0
                }
                
        except sqlite3.Error as e:
            print(f"طالب علم کا بیلنس حاصل کرنے میں خرابی: {e}")
            return {'total_paid': 0.0, 'total_months_paid': 0}
