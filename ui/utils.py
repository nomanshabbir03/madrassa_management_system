import os
import re
import datetime
import sqlite3
import random
import string
from PyQt5.QtWidgets import QMessageBox, QApplication
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtCore import Qt

# Urdu numeral mapping
URDU_NUMERALS = {
    '0': '۰',
    '1': '۱', 
    '2': '۲',
    '3': '۳',
    '4': '۴',
    '5': '۵',
    '6': '۶',
    '7': '۷',
    '8': '۸',
    '9': '۹'
}

# Urdu month names
URDU_MONTHS = [
    'جنوری', 'فروری', 'مارچ', 'اپریل', 'مئی', 'جون',
    'جولائی', 'اگست', 'ستمبر', 'اکتوبر', 'نومبر', 'دسمبر'
]

def to_urdu_numerals(number):
    """Convert a number to Urdu/Eastern Arabic numerals."""
    if isinstance(number, int):
        number_str = str(number)
    else:
        number_str = str(number)
    
    urdu_str = ""
    for digit in number_str:
        if digit in URDU_NUMERALS:
            urdu_str += URDU_NUMERALS[digit]
        else:
            urdu_str += digit
    
    return urdu_str

def get_today_date():
    """Return today's date as string in format YYYY-MM-DD."""
    return datetime.date.today().strftime("%Y-%m-%d")

def format_date_urdu(date_str):
    """Format date as DD-MM-YYYY for Urdu readability."""
    try:
        # Expected input: YYYY-MM-DD
        date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        formatted = date_obj.strftime("%d-%m-%Y")
        return to_urdu_numerals(formatted)
    except ValueError:
        return to_urdu_numerals(date_str)

def get_current_month_year():
    """Return current month and year as strings."""
    today = datetime.date.today()
    return (str(today.month).zfill(2), str(today.year))

def get_urdu_month_name(month_number):
    """Get Urdu month name for given month number (1-12)."""
    if 1 <= month_number <= 12:
        return URDU_MONTHS[month_number - 1]
    return ""

def generate_receipt_number():
    """Generate a unique receipt number."""
    today = datetime.date.today()
    date_str = today.strftime("%Y%m%d")
    random_digits = ''.join(random.choices(string.digits, k=4))
    return f"RCP-{date_str}-{random_digits}"

def generate_registration_number(conn):
    """Generate a unique student registration number."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM students")
        count = cursor.fetchone()[0]
        
        current_year = datetime.date.today().year
        next_number = count + 1
        return f"MDS-{current_year}-{str(next_number).zfill(4)}"
    except sqlite3.Error:
        # Fallback if database query fails
        current_year = datetime.date.today().year
        random_digits = ''.join(random.choices(string.digits, k=4))
        return f"MDS-{current_year}-{random_digits}"

def generate_employee_code(conn):
    """Generate a unique employee code."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM employees")
        count = cursor.fetchone()[0]
        
        current_year = datetime.date.today().year
        next_number = count + 1
        return f"EMP-{current_year}-{str(next_number).zfill(4)}"
    except sqlite3.Error:
        # Fallback if database query fails
        current_year = datetime.date.today().year
        random_digits = ''.join(random.choices(string.digits, k=4))
        return f"EMP-{current_year}-{random_digits}"

def validate_phone(phone):
    """Validate Pakistani phone number format (03XX-XXXXXXX)."""
    if not phone:
        return False
    # Remove any dashes or spaces for counting
    digits = re.sub(r'[^\d]', '', phone)
    # Check if starts with 03 and has 11 digits
    return digits.startswith("03") and len(digits) == 11

def validate_cnic(cnic):
    """Validate Pakistani CNIC format (XXXXX-XXXXXXX-X)."""
    if not cnic:
        return False
    pattern = r'^\d{5}-\d{7}-\d{1}$'
    return bool(re.match(pattern, cnic))

def validate_required(value):
    """Check if value is not None and not empty after stripping."""
    if value is None:
        return False
    if isinstance(value, str):
        return len(value.strip()) > 0
    return True

def validate_email(email):
    """Basic email validation."""
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def set_field_error(widget, is_error=True):
    """Set red border for validation errors."""
    if is_error:
        widget.setStyleSheet("border: 2px solid #DC3545;") # COLOR_ERROR
    else:
        widget.setStyleSheet("") # Reset to default stylesheet

def show_error(parent, message):
    """Show error message dialog in Urdu."""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle("خطا")
    msg.setText(message)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

def show_success(parent, message):
    """Show success message dialog in Urdu."""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle("کامیابی")
    msg.setText(message)
    msg.setStandardButtons(QMessageBox.Ok)
    msg.exec_()

def show_confirm(parent, message):
    """Show confirmation dialog with Yes/No buttons in Urdu."""
    msg = QMessageBox(parent)
    msg.setIcon(QMessageBox.Question)
    msg.setWindowTitle("تصدیق")
    msg.setText(message)
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg.setDefaultButton(QMessageBox.No)
    
    # Change button text to Urdu
    msg.button(QMessageBox.Yes).setText("ہاں")
    msg.button(QMessageBox.No).setText("نہیں")
    
    return msg.exec_() == QMessageBox.Yes

def get_urdu_font(size=14, bold=False):
    """Get QFont object for Urdu text."""
    font = QFont("Noto Nastaliq Urdu", size)
    if bold:
        font.setBold(True)
    return font

def clear_table(table_widget):
    """Safely clear all rows from a QTableWidget."""
    if table_widget is not None and hasattr(table_widget, 'rowCount') and table_widget.rowCount() > 0:
        table_widget.setRowCount(0)

def set_table_item_urdu(table_widget, row, col, value):
    """Set table cell value with Urdu formatting."""
    # Convert numbers to Urdu numerals
    if isinstance(value, (int, float)) or (isinstance(value, str) and value.isdigit()):
        display_value = to_urdu_numerals(value)
    else:
        display_value = str(value)
    
    # Create new item if it doesn't exist
    item = table_widget.item(row, col)
    if item is None:
        from PyQt5.QtWidgets import QTableWidgetItem
        item = QTableWidgetItem()
        table_widget.setItem(row, col, item)
    
    # Set item properties
    item.setText(display_value)
    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
    item.setFont(get_urdu_font(13))
    
    # Make item non-editable but selectable
    item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)