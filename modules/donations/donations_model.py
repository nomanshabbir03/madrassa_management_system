import sqlite3
import datetime
import random
import string
from database import get_connection


class DonationModel:
    def __init__(self):
        """Initialize database connection."""
        self.conn = get_connection()
    
    def get_all_donations(self, filters=None):
        """Return all donations with optional filters."""
        try:
            cursor = self.conn.cursor()
            
            query = """
                SELECT id, donor_name, donor_contact, amount, donation_type, 
                       payment_method, donation_date, receipt_number, notes, created_at
                FROM donations
                WHERE 1=1
            """
            params = []
            
            if filters:
                if filters.get('donor_name'):
                    query += " AND donor_name LIKE ?"
                    params.append(f"%{filters['donor_name']}%")
                
                if filters.get('donation_type'):
                    query += " AND donation_type = ?"
                    params.append(filters['donation_type'])
                
                if filters.get('payment_method'):
                    query += " AND payment_method = ?"
                    params.append(filters['payment_method'])
                
                if filters.get('date_range'):
                    start_date, end_date = filters['date_range']
                    query += " AND donation_date BETWEEN ? AND ?"
                    params.extend([start_date, end_date])
            
            query += " ORDER BY donation_date DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            columns = [desc[0] for desc in cursor.description]
            donations = []
            
            for row in rows:
                donation = dict(zip(columns, row))
                donations.append(donation)
            
            return donations
            
        except sqlite3.Error as e:
            print(f"Error getting donations: {e}")
            return []
    
    def get_donation_by_id(self, donation_id):
        """Return single donation record as dict."""
        try:
            cursor = self.conn.cursor()
            
            query = """
                SELECT id, donor_name, donor_contact, amount, donation_type, 
                       payment_method, donation_date, receipt_number, notes, created_at
                FROM donations
                WHERE id = ?
            """
            
            cursor.execute(query, (donation_id,))
            row = cursor.fetchone()
            
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            
            return None
            
        except sqlite3.Error as e:
            print(f"Error getting donation by ID: {e}")
            return None
    
    def add_donation(self, donor_name, amount, donation_type, payment_method, 
                    donor_contact="", notes=""):
        """Add new donation record."""
        try:
            cursor = self.conn.cursor()
            
            # Generate receipt number
            receipt_number = self.generate_receipt_number()
            
            # Get current date
            donation_date = datetime.date.today().strftime("%Y-%m-%d")
            created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            query = """
                INSERT INTO donations 
                (donor_name, donor_contact, amount, donation_type, payment_method, 
                 donation_date, receipt_number, notes, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(query, (
                donor_name, donor_contact, amount, donation_type, payment_method,
                donation_date, receipt_number, notes, created_at
            ))
            
            self.conn.commit()
            donation_id = cursor.lastrowid
            
            return donation_id, receipt_number
            
        except sqlite3.Error as e:
            print(f"Error adding donation: {e}")
            self.conn.rollback()
            return None, None
    
    def update_donation(self, donation_id, **kwargs):
        """Update donation record by id."""
        try:
            cursor = self.conn.cursor()
            
            # Build dynamic update query
            update_fields = []
            params = []
            
            allowed_fields = [
                'donor_name', 'donor_contact', 'amount', 'donation_type', 
                'payment_method', 'notes'
            ]
            
            for field, value in kwargs.items():
                if field in allowed_fields and value is not None:
                    update_fields.append(f"{field} = ?")
                    params.append(value)
            
            if not update_fields:
                return False
            
            params.append(donation_id)
            
            query = f"UPDATE donations SET {', '.join(update_fields)} WHERE id = ?"
            
            cursor.execute(query, params)
            self.conn.commit()
            
            return cursor.rowcount > 0
            
        except sqlite3.Error as e:
            print(f"Error updating donation: {e}")
            self.conn.rollback()
            return False
    
    def delete_donation(self, donation_id):
        """Hard delete donation record."""
        try:
            cursor = self.conn.cursor()
            
            query = "DELETE FROM donations WHERE id = ?"
            cursor.execute(query, (donation_id,))
            self.conn.commit()
            
            return cursor.rowcount > 0
            
        except sqlite3.Error as e:
            print(f"Error deleting donation: {e}")
            self.conn.rollback()
            return False
    
    def get_donations_by_type(self, donation_type=None):
        """Get donations grouped by type with totals."""
        try:
            cursor = self.conn.cursor()
            
            if donation_type:
                # Get specific type donations
                query = """
                    SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total_amount
                    FROM donations
                    WHERE donation_type = ?
                """
                cursor.execute(query, (donation_type,))
                row = cursor.fetchone()
                
                return {
                    donation_type: {
                        'count': row[0],
                        'total_amount': row[1]
                    }
                }
            else:
                # Get all types with totals
                query = """
                    SELECT donation_type, COUNT(*) as count, COALESCE(SUM(amount), 0) as total_amount
                    FROM donations
                    GROUP BY donation_type
                    ORDER BY total_amount DESC
                """
                cursor.execute(query)
                rows = cursor.fetchall()
                
                result = {}
                for row in rows:
                    result[row[0]] = {
                        'count': row[1],
                        'total_amount': row[2]
                    }
                
                return result
                
        except sqlite3.Error as e:
            print(f"Error getting donations by type: {e}")
            return {} if donation_type is None else {'count': 0, 'total_amount': 0}
    
    def get_monthly_summary(self, year, month=None):
        """Get monthly donation summary."""
        try:
            cursor = self.conn.cursor()
            
            if month:
                # Get specific month
                query = """
                    SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total_amount
                    FROM donations
                    WHERE strftime('%Y', donation_date) = ? 
                    AND strftime('%m', donation_date) = ?
                """
                cursor.execute(query, (str(year), str(month).zfill(2)))
                row = cursor.fetchone()
                
                return {
                    'count': row[0],
                    'total_amount': row[1]
                }
            else:
                # Get all 12 months for the year
                query = """
                    SELECT strftime('%m', donation_date) as month,
                           COUNT(*) as count, 
                           COALESCE(SUM(amount), 0) as total_amount
                    FROM donations
                    WHERE strftime('%Y', donation_date) = ?
                    GROUP BY strftime('%m', donation_date)
                    ORDER BY month
                """
                cursor.execute(query, (str(year),))
                rows = cursor.fetchall()
                
                result = {}
                for row in rows:
                    result[int(row[0])] = {
                        'count': row[1],
                        'total_amount': row[2]
                    }
                
                return result
                
        except sqlite3.Error as e:
            print(f"Error getting monthly summary: {e}")
            return {} if month is None else {'count': 0, 'total_amount': 0}
    
    def get_donor_history(self, donor_name):
        """Return all donations by specific donor name."""
        try:
            cursor = self.conn.cursor()
            
            query = """
                SELECT id, donor_name, donor_contact, amount, donation_type, 
                       payment_method, donation_date, receipt_number, notes, created_at
                FROM donations
                WHERE donor_name = ?
                ORDER BY donation_date DESC
            """
            
            cursor.execute(query, (donor_name,))
            rows = cursor.fetchall()
            
            columns = [desc[0] for desc in cursor.description]
            donations = []
            
            for row in rows:
                donation = dict(zip(columns, row))
                donations.append(donation)
            
            return donations
            
        except sqlite3.Error as e:
            print(f"Error getting donor history: {e}")
            return []
    
    def search_donors(self, search_term):
        """Search donor names and contacts with LIKE."""
        try:
            cursor = self.conn.cursor()
            
            query = """
                SELECT DISTINCT donor_name, donor_contact
                FROM donations
                WHERE donor_name LIKE ? OR donor_contact LIKE ?
                ORDER BY donor_name
            """
            
            search_pattern = f"%{search_term}%"
            cursor.execute(query, (search_pattern, search_pattern))
            rows = cursor.fetchall()
            
            donors = []
            for row in rows:
                donors.append({
                    'donor_name': row[0],
                    'donor_contact': row[1]
                })
            
            return donors
            
        except sqlite3.Error as e:
            print(f"Error searching donors: {e}")
            return []
    
    def generate_receipt_number(self):
        """Generate unique receipt number format: DON-YYYYMMDD-XXXX."""
        today = datetime.date.today()
        date_str = today.strftime("%Y%m%d")
        random_digits = ''.join(random.choices(string.digits, k=4))
        return f"DON-{date_str}-{random_digits}"
    
    def get_summary_statistics(self):
        """Get summary statistics for dashboard."""
        try:
            cursor = self.conn.cursor()
            
            # Total donations
            cursor.execute("SELECT COUNT(*) FROM donations")
            total_count = cursor.fetchone()[0]
            
            # Total amount
            cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM donations")
            total_amount = cursor.fetchone()[0]
            
            # Today's donations
            today = datetime.date.today().strftime("%Y-%m-%d")
            cursor.execute("SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM donations WHERE donation_date = ?", (today,))
            today_stats = cursor.fetchone()
            
            # This month's donations
            current_month = datetime.date.today().strftime("%Y-%m")
            cursor.execute("SELECT COUNT(*), COALESCE(SUM(amount), 0) FROM donations WHERE strftime('%Y-%m', donation_date) = ?", (current_month,))
            month_stats = cursor.fetchone()
            
            return {
                'total_count': total_count,
                'total_amount': total_amount,
                'today_count': today_stats[0],
                'today_amount': today_stats[1],
                'month_count': month_stats[0],
                'month_amount': month_stats[1]
            }
            
        except sqlite3.Error as e:
            print(f"Error getting summary statistics: {e}")
            return {
                'total_count': 0,
                'total_amount': 0,
                'today_count': 0,
                'today_amount': 0,
                'month_count': 0,
                'month_amount': 0
            }
    
    def close_connection(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
