from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QGridLayout, QComboBox, QSpinBox, QLineEdit, 
                             QPushButton, QTextEdit, QFrame, QShortcut)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIntValidator, QKeySequence

from ui.utils import (get_urdu_font, show_error, show_success, 
                      to_urdu_numerals, validate_required, get_today_date)
from ui.styles import COLOR_ACCENT
from .fee_model import FeeModel

# Urdu month names mapping
URDU_MONTHS = {
    1: 'جنوری', 2: 'فروری', 3: 'مارچ', 4: 'اپریل',
    5: 'مئی', 6: 'جون', 7: 'جولائی', 8: 'اگست',
    9: 'ستمبر', 10: 'اکتوبر', 11: 'نومبر', 12: 'دسمبر'
}

class FeeForm(QWidget):
    fee_saved = pyqtSignal(int)
    cancelled = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = FeeModel()
        self.setup_ui()
        self.setup_shortcuts()
        self.load_students()
    
    def setup_ui(self):
        """Setup the fee form UI with RTL layout."""
        # Main vertical layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
                
        # Title: "فیس وصولی" with gold accent color
        title = QLabel("فیس وصولی")
        title.setFont(get_urdu_font(18, bold=True))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(f"color: {COLOR_ACCENT}; margin-bottom: 15px;")
        title.setLayoutDirection(Qt.RightToLeft)
        main_layout.addWidget(title)
        
        # Form grid with labels on right (Urdu)
        form_grid = QGridLayout()
        form_grid.setSpacing(10)
                
        # Student dropdown
        student_label = QLabel("طالب علم")
        student_label.setFont(get_urdu_font(14))
        student_label.setLayoutDirection(Qt.RightToLeft)
        form_grid.addWidget(student_label, 0, 0, Qt.AlignRight)
        
        self.student_combo = QComboBox()
        self.student_combo.setFont(get_urdu_font(14))
        self.student_combo.setMinimumHeight(35)
        self.student_combo.setLayoutDirection(Qt.RightToLeft)
        self.student_combo.currentTextChanged.connect(self.update_unpaid_months)
        form_grid.addWidget(self.student_combo, 0, 1)
        
        # Month dropdown
        month_label = QLabel("ماہ")
        month_label.setFont(get_urdu_font(14))
        month_label.setLayoutDirection(Qt.RightToLeft)
        form_grid.addWidget(month_label, 1, 0, Qt.AlignRight)
        
        self.month_combo = QComboBox()
        self.month_combo.setFont(get_urdu_font(14))
        self.month_combo.setMinimumHeight(35)
        self.month_combo.setLayoutDirection(Qt.RightToLeft)
        for month_num in range(1, 13):
            self.month_combo.addItem(URDU_MONTHS[month_num], month_num)
        self.month_combo.currentTextChanged.connect(self.update_unpaid_months)
        form_grid.addWidget(self.month_combo, 1, 1)
        
        # Year spinbox
        year_label = QLabel("سال")
        year_label.setFont(get_urdu_font(14))
        year_label.setLayoutDirection(Qt.RightToLeft)
        form_grid.addWidget(year_label, 2, 0, Qt.AlignRight)
        
        self.year_spinbox = QSpinBox()
        self.year_spinbox.setRange(2020, 2030)
        self.year_spinbox.setValue(int(get_today_date().split('-')[0]))
        self.year_spinbox.setFont(get_urdu_font(14))
        self.year_spinbox.setMinimumHeight(35)
        self.year_spinbox.setLayoutDirection(Qt.RightToLeft)
        self.year_spinbox.valueChanged.connect(self.update_unpaid_months)
        form_grid.addWidget(self.year_spinbox, 2, 1)
        
        # Amount input
        amount_label = QLabel("رقم")
        amount_label.setFont(get_urdu_font(14))
        amount_label.setLayoutDirection(Qt.RightToLeft)
        form_grid.addWidget(amount_label, 3, 0, Qt.AlignRight)
        
        self.amount_input = QLineEdit()
        self.amount_input.setFont(get_urdu_font(14))
        self.amount_input.setMinimumHeight(35)
        self.amount_input.setLayoutDirection(Qt.RightToLeft)
        self.amount_input.setValidator(QIntValidator(0, 999999))
        self.amount_input.setPlaceholderText("رقم درج کریں")
        form_grid.addWidget(self.amount_input, 3, 1)
        
        # Payment method dropdown
        payment_label = QLabel("ادائیگی کا طریقہ")
        payment_label.setFont(get_urdu_font(14))
        payment_label.setLayoutDirection(Qt.RightToLeft)
        form_grid.addWidget(payment_label, 4, 0, Qt.AlignRight)
        
        self.payment_combo = QComboBox()
        self.payment_combo.setFont(get_urdu_font(14))
        self.payment_combo.setMinimumHeight(35)
        self.payment_combo.setLayoutDirection(Qt.RightToLeft)
        self.payment_combo.addItems(['نقد', 'بینک ٹرانسفر', 'چیک'])
        form_grid.addWidget(self.payment_combo, 4, 1)
        
        # Receipt number (read-only)
        receipt_label = QLabel("رسید نمبر")
        receipt_label.setFont(get_urdu_font(14))
        receipt_label.setLayoutDirection(Qt.RightToLeft)
        form_grid.addWidget(receipt_label, 5, 0, Qt.AlignRight)
        
        self.receipt_input = QLineEdit()
        self.receipt_input.setFont(get_urdu_font(14))
        self.receipt_input.setMinimumHeight(35)
        self.receipt_input.setLayoutDirection(Qt.RightToLeft)
        self.receipt_input.setReadOnly(True)
        self.receipt_input.setPlaceholderText("محفوظ کرنے پر خودکار")
        form_grid.addWidget(self.receipt_input, 5, 1)
        
        # Notes text area
        notes_label = QLabel("نوٹس")
        notes_label.setFont(get_urdu_font(14))
        notes_label.setLayoutDirection(Qt.RightToLeft)
        form_grid.addWidget(notes_label, 6, 0, Qt.AlignTop)
        
        self.notes_text = QTextEdit()
        self.notes_text.setFont(get_urdu_font(14))
        self.notes_text.setMinimumHeight(80)
        self.notes_text.setMaximumHeight(80)
        self.notes_text.setLayoutDirection(Qt.RightToLeft)
        self.notes_text.setPlaceholderText("اختیاری نوٹس")
        form_grid.addWidget(self.notes_text, 6, 1)
        
        main_layout.addLayout(form_grid)
        
        # "Unpaid Months" section
        self.unpaid_frame = QFrame()
        self.unpaid_frame.setStyleSheet("""
            QFrame {
                background-color: #fff5f5;
                border: 1px solid #ffcccc;
                border-radius: 5px;
                padding: 10px;
                margin: 10px 0;
            }
        """)
        self.unpaid_frame.setLayoutDirection(Qt.RightToLeft)
        self.unpaid_frame.setVisible(False)
        
        unpaid_layout = QHBoxLayout(self.unpaid_frame)
        unpaid_layout.setContentsMargins(10, 5, 10, 5)
                
        unpaid_title = QLabel("غیر ادا شدہ ماہ")
        unpaid_title.setFont(get_urdu_font(12, bold=True))
        unpaid_title.setStyleSheet("color: #DC3545;")
        unpaid_title.setLayoutDirection(Qt.RightToLeft)
        unpaid_layout.addWidget(unpaid_title)
        
        self.unpaid_months_label = QLabel()
        self.unpaid_months_label.setFont(get_urdu_font(12))
        self.unpaid_months_label.setStyleSheet("color: #DC3545;")
        self.unpaid_months_label.setLayoutDirection(Qt.RightToLeft)
        self.unpaid_months_label.setWordWrap(True)
        unpaid_layout.addWidget(self.unpaid_months_label)
        
        unpaid_layout.addStretch()
        main_layout.addWidget(self.unpaid_frame)
        
        # Buttons (right to left order)
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
                
        # Save button (Green)
        self.save_button = QPushButton("محفوظ کریں")
        self.save_button.setFont(get_urdu_font(12, bold=True))
        self.save_button.setFixedHeight(40)
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.save_button.clicked.connect(self.save_fee)
        buttons_layout.addWidget(self.save_button)
        
        # Clear button
        self.clear_button = QPushButton("صاف کریں")
        self.clear_button.setFont(get_urdu_font(12))
        self.clear_button.setFixedHeight(40)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        self.clear_button.clicked.connect(self.clear_form)
        buttons_layout.addWidget(self.clear_button)
        
        # Close button
        self.close_button = QPushButton("بند کریں")
        self.close_button.setFont(get_urdu_font(12))
        self.close_button.setFixedHeight(40)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        self.close_button.clicked.connect(self.close_form)
        buttons_layout.addWidget(self.close_button)
        
        buttons_layout.addStretch()
        main_layout.addLayout(buttons_layout)
        main_layout.addStretch()
        
        self.setLayoutDirection(Qt.RightToLeft)
        self.setFont(get_urdu_font(14))

    def setup_shortcuts(self):
        """Setup shortcuts for the form."""
        self.shortcut_save = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut_save.activated.connect(self.save_fee)
        
        self.shortcut_cancel = QShortcut(QKeySequence("Esc"), self)
        self.shortcut_cancel.activated.connect(self.close_form)
    
    def load_students(self):
        """Populate student dropdown from database."""
        try:
            # Import here to avoid circular imports
            from modules.students.student_model import StudentModel
            student_model = StudentModel()
            students = student_model.get_all_students()
            
            self.student_combo.clear()
            self.student_combo.addItem("طالب علم منتخب کریں", None)
            
            for student in students:
                display_text = f"{student['full_name']} - {student['registration_number']}"
                self.student_combo.addItem(display_text, student['id'])
                
        except Exception as e:
            print(f"Error loading students: {e}")
    
    def update_unpaid_months(self):
        """Fetch and display unpaid months in red when student/year changes."""
        student_id = self.student_combo.currentData()
        year = self.year_spinbox.value()
        
        if not student_id:
            self.unpaid_frame.setVisible(False)
            return
        
        try:
            unpaid_months = self.model.get_unpaid_months(student_id, year)
            
            if unpaid_months:
                unpaid_names = [URDU_MONTHS[month] for month in unpaid_months]
                unpaid_text = ", ".join(unpaid_names)
                self.unpaid_months_label.setText(unpaid_text)
                self.unpaid_frame.setVisible(True)
            else:
                self.unpaid_frame.setVisible(False)
                
        except Exception as e:
            print(f"Error updating unpaid months: {e}")
            self.unpaid_frame.setVisible(False)
    
    def validate_form(self):
        """Check all required fields, show_error if invalid."""
        # Reset errors
        set_field_error(self.student_combo, False)
        set_field_error(self.amount_input, False)
        
        student_id = self.student_combo.currentData()
        if not student_id:
            set_field_error(self.student_combo, True)
            show_error(self, "طالب علم کا انتخاب لازمی ہے")
            return False
        
        amount_text = self.amount_input.text().strip()
        if not amount_text:
            set_field_error(self.amount_input, True)
            show_error(self, "رقم لازمی ہے")
            return False
        
        try:
            amount = float(amount_text)
            if amount <= 0:
                set_field_error(self.amount_input, True)
                show_error(self, "رقم صفر سے زیادہ ہونا چاہیے")
                return False
        except ValueError:
            set_field_error(self.amount_input, True)
            show_error(self, "غلط رقم کا فارمیٹ")
            return False
        
        return True
    
    def save_fee(self):
        """Call fee_model.add_fee(), show_success on completion."""
        if not self.validate_form():
            return
        
        try:
            student_id = self.student_combo.currentData()
            amount = float(self.amount_input.text())
            month = self.month_combo.currentData()
            year = self.year_spinbox.value()
            payment_method = self.payment_combo.currentText()
            notes = self.notes_text.toPlainText().strip()
            
            fee_id, receipt_number = self.model.add_fee(
                student_id, amount, month, year, payment_method, notes
            )
            
            # Update receipt number display
            self.receipt_input.setText(receipt_number)
            
            # Show success message
            show_success(self, f"فیس کامیابی سے محفوظ ہو گئی! رسید: {receipt_number}")
            
            # Emit signal
            self.fee_saved.emit(fee_id)
            
            # Clear form for next entry
            self.clear_form()
            
        except Exception as e:
            show_error(self, f"فیس محفوظ کرنے میں خرابی: {str(e)}")
    
    def clear_form(self):
        """Resets form."""
        self.student_combo.setCurrentIndex(0)
        self.month_combo.setCurrentIndex(0)
        self.year_spinbox.setValue(int(get_today_date().split('-')[0]))
        self.amount_input.clear()
        self.payment_combo.setCurrentIndex(0)
        self.receipt_input.clear()
        self.notes_text.clear()
        self.unpaid_frame.setVisible(False)
    
    def close_form(self):
        """Closes form and emits cancelled signal."""
        self.cancelled.emit()
        if self.parent():
            self.parent().close()
        else:
            self.close()
    
    def generate_receipt_number(self):
        """Format RCP-YYYYMMDD-XXXX (XXXX = random 4 digits)."""
        import random
        import string
        from datetime import datetime
        
        today = datetime.now()
        date_str = today.strftime("%Y%m%d")
        random_digits = ''.join(random.choices(string.digits, k=4))
        return f"RCP-{date_str}-{random_digits}"
