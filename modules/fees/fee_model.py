import sqlite3
import database
from ui.utils import generate_receipt_number, get_today_date, URDU_MONTHS

class FeeModel:
    def __init__(self):
        pass
    
    def add_fee(self, data):
        """
        Add a new fee record.
        
        Args:
            data (dict): Contains student_id, month, year, amount, payment_method, remarks
            
        Returns:
            int: New fee record ID
            
        Raises:
            ValueError: If student_id or amount validation fails
            ValueError: If fee record already exists
        """
        # Validate required fields
        if not data.get('student_id'):
            raise ValueError("Student selection is required")
        
        if not data.get('amount') or data.get('amount') <= 0:
            raise ValueError("Amount is required")
        
        # Generate receipt number and set paid date
        receipt_number = generate_receipt_number()
        paid_date = get_today_date()
        
        try:
            with database.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if fee record already exists
                cursor.execute('''
                    SELECT id FROM fees 
                    WHERE student_id = ? AND month = ? AND year = ?
                ''', (data['student_id'], data['month'], data['year']))
                
                if cursor.fetchone():
                    raise ValueError("This fee record already exists")
                
                # Insert new fee record
                cursor.execute('''
                    INSERT INTO fees (
                        student_id, month, year, amount, paid_date, 
                        receipt_number, payment_method, remarks
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    data['student_id'], data['month'], data['year'], 
                    data['amount'], paid_date, receipt_number,
                    data.get('payment_method', ''), data.get('remarks', '')
                ))
                
                return cursor.lastrowid
                
        except sqlite3.IntegrityError:
            raise ValueError("This fee record already exists")
    
    def get_fees_by_student(self, student_id):
        """
        Get all fee records for a student.
        
        Args:
            student_id (int): Student ID
            
        Returns:
            list: Fee records ordered by year DESC, month DESC
        """
        try:
            with database.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, month, year, amount, paid_date, 
                           receipt_number, payment_method, remarks
                    FROM fees 
                    WHERE student_id = ?
                    ORDER BY year DESC, month DESC
                ''', (student_id,))
                
                columns = ['id', 'month', 'year', 'amount', 'paid_date', 
                          'receipt_number', 'payment_method', 'remarks']
                
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            print(f"Error getting fees by student: {e}")
            return []
    
    def get_monthly_collection(self, month, year):
        """
        Get total fee collection for given month and year.
        
        Args:
            month (str): Month name
            year (str): Year
            
        Returns:
            float: Total collection amount
        """
        try:
            with database.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT SUM(amount) FROM fees 
                    WHERE month = ? AND year = ?
                ''', (month, year))
                
                result = cursor.fetchone()[0]
                return float(result) if result else 0.0
                
        except sqlite3.Error as e:
            print(f"Error getting monthly collection: {e}")
            return 0.0
    
    def get_unpaid_months(self, student_id, year):
        """
        Get list of unpaid months for a student in a given year.
        
        Args:
            student_id (int): Student ID
            year (str): Year
            
        Returns:
            list: List of unpaid month names
        """
        try:
            with database.get_connection() as conn:
                cursor = conn.cursor()
                
                # Get paid months for this student and year
                cursor.execute('''
                    SELECT month FROM fees 
                    WHERE student_id = ? AND year = ?
                ''', (student_id, year))
                
                paid_months = {row[0] for row in cursor.fetchall()}
                
                # Return unpaid months
                unpaid_months = []
                for month in URDU_MONTHS:
                    if month not in paid_months:
                        unpaid_months.append(month)
                
                return unpaid_months
                
        except sqlite3.Error as e:
            print(f"Error getting unpaid months: {e}")
            return []
    
    def get_all_fees(self, month=None, year=None):
        """
        Get all fee records with student information.
        
        Args:
            month (str, optional): Filter by month
            year (str, optional): Filter by year
            
        Returns:
            list: Fee records with student information
        """
        try:
            with database.get_connection() as conn:
                cursor = conn.cursor()
                
                query = '''
                    SELECT f.id, s.full_name as student_name, s.registration_number,
                           f.month, f.year, f.amount, f.paid_date, 
                           f.receipt_number, f.payment_method
                    FROM fees f
                    JOIN students s ON f.student_id = s.id
                '''
                
                params = []
                conditions = []
                
                if month:
                    conditions.append("f.month = ?")
                    params.append(month)
                
                if year:
                    conditions.append("f.year = ?")
                    params.append(year)
                
                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                
                query += " ORDER BY f.paid_date DESC"
                
                cursor.execute(query, params)
                
                columns = ['id', 'student_name', 'registration_number', 
                          'month', 'year', 'amount', 'paid_date', 
                          'receipt_number', 'payment_method']
                
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            print(f"Error getting all fees: {e}")
            return []
    
    def delete_fee(self, fee_id):
        """
        Delete a fee record.
        
        Args:
            fee_id (int): Fee record ID
            
        Returns:
            bool: True on success
            
        Raises:
            ValueError: If deletion fails
        """
        try:
            with database.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM fees WHERE id = ?", (fee_id,))
                
                if cursor.rowcount == 0:
                    raise ValueError("Fee record not found")
                
                return True
                
        except sqlite3.Error as e:
            print(f"Error deleting fee: {e}")
            raise ValueError("Error deleting fee record")
    
    def get_students_list(self):
        """
        Get list of active students for dropdown.
        
        Returns:
            list: Students with id, full_name, registration_number, class_name
        """
        try:
            with database.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT id, full_name, registration_number, class_name
                    FROM students 
                    WHERE status = 'active'
                    ORDER BY full_name
                ''')
                
                columns = ['id', 'full_name', 'registration_number', 'class_name']
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            print(f"Error getting students list: {e}")
            return []
    
    def get_payment_methods(self):
        """
        Get list of payment methods.
        
        Returns:
            list: Payment method names
        """
        return ["Cash", "Bank Transfer", "Cheque", "Online"]
