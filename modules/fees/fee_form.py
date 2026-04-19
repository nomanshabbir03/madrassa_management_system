from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFormLayout, QComboBox, QDoubleSpinBox, 
                             QLineEdit, QPushButton, QFrame, QApplication)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui.utils import get_urdu_font, show_error, show_success, get_today_date, URDU_MONTHS
from ui.styles import COLOR_ACCENT
from .fee_model import FeeModel

class FeeForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = FeeModel()
        self.on_save_callback = None
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the fee form UI."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Heading
        heading = QLabel("Collect Fee")
        heading.setFont(get_urdu_font(18, bold=True))
        heading.setAlignment(Qt.AlignCenter)
        heading.setStyleSheet(f"color: {COLOR_ACCENT}; margin-bottom: 10px;")
        main_layout.addWidget(heading)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setLayoutDirection(Qt.RightToLeft)
        
        # Student dropdown
        self.student_combo = QComboBox()
        self.student_combo.setFont(get_urdu_font(12))
        self.student_combo.setMinimumHeight(35)
        self.student_combo.currentIndexChanged.connect(self.on_student_changed)
        form_layout.addRow("Student *", self.student_combo)
        
        # Month dropdown
        self.month_combo = QComboBox()
        self.month_combo.setFont(get_urdu_font(12))
        self.month_combo.setMinimumHeight(35)
        self.month_combo.addItems(URDU_MONTHS)
        form_layout.addRow("Month *", self.month_combo)
        
        # Year dropdown
        self.year_combo = QComboBox()
        self.year_combo.setFont(get_urdu_font(12))
        self.year_combo.setMinimumHeight(35)
        current_year = int(get_today_date().split('-')[0])
        for year in range(current_year, current_year - 5, -1):
            self.year_combo.addItem(str(year))
        form_layout.addRow("Year *", self.year_combo)
        
        # Amount input
        self.amount_spinbox = QDoubleSpinBox()
        self.amount_spinbox.setRange(0, 99999)
        self.amount_spinbox.setSuffix(" Rs")
        self.amount_spinbox.setFont(get_urdu_font(12))
        self.amount_spinbox.setMinimumHeight(35)
        form_layout.addRow("Amount *", self.amount_spinbox)
        
        # Payment method dropdown
        self.payment_combo = QComboBox()
        self.payment_combo.setFont(get_urdu_font(12))
        self.payment_combo.setMinimumHeight(35)
        self.payment_combo.addItems(self.model.get_payment_methods())
        form_layout.addRow("Payment Method", self.payment_combo)
        
        # Remarks input
        self.remarks_input = QLineEdit()
        self.remarks_input.setFont(get_urdu_font(12))
        self.remarks_input.setMinimumHeight(35)
        self.remarks_input.setPlaceholderText("Additional notes")
        form_layout.addRow("Notes", self.remarks_input)
        
        main_layout.addLayout(form_layout)
        
        # Unpaid months display frame
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
        self.unpaid_frame.setVisible(False)
        
        unpaid_layout = QHBoxLayout(self.unpaid_frame)
        unpaid_layout.setContentsMargins(10, 5, 10, 5)
        
        unpaid_label = QLabel("Unpaid Months:")
        unpaid_label.setFont(get_urdu_font(11, bold=True))
        unpaid_label.setStyleSheet("color: #d32f2f;")
        unpaid_layout.addWidget(unpaid_label)
        
        self.unpaid_months_label = QLabel()
        self.unpaid_months_label.setFont(get_urdu_font(11))
        self.unpaid_months_label.setStyleSheet("color: #d32f2f;")
        self.unpaid_months_label.setWordWrap(True)
        unpaid_layout.addWidget(self.unpaid_months_label)
        
        unpaid_layout.addStretch()
        main_layout.addWidget(self.unpaid_frame)
        
        # Receipt number preview
        self.receipt_label = QLabel("Receipt Number: Auto")
        self.receipt_label.setFont(get_urdu_font(11))
        self.receipt_label.setStyleSheet("color: #666; font-style: italic;")
        main_layout.addWidget(self.receipt_label)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        self.save_button = QPushButton("Collect Fee")
        self.save_button.setFont(get_urdu_font(12, bold=True))
        self.save_button.setFixedHeight(40)
        self.save_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_ACCENT};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
            }}
            QPushButton:hover {{
                background-color: #2D6A4F;
            }}
        """)
        self.save_button.clicked.connect(self.save_fee)
        buttons_layout.addWidget(self.save_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFont(get_urdu_font(12))
        self.cancel_button.setFixedHeight(40)
        self.cancel_button.setStyleSheet("""
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
        self.cancel_button.clicked.connect(self.close)
        buttons_layout.addWidget(self.cancel_button)
        
        buttons_layout.addStretch()
        main_layout.addLayout(buttons_layout)
        main_layout.addStretch()
        
        # Load students
        self.load_students()
    
    def load_students(self):
        """Load students into the dropdown."""
        students = self.model.get_students_list()
        self.student_combo.clear()
        self.student_combo.addItem("Select Student", None)
        
        for student in students:
            display_text = f"{student['full_name']} - {student['registration_number']}"
            self.student_combo.addItem(display_text, student['id'])
    
    def on_student_changed(self):
        """Handle student selection change."""
        student_id = self.student_combo.currentData()
        
        if not student_id:
            self.unpaid_frame.setVisible(False)
            return
        
        current_year = self.year_combo.currentText()
        unpaid_months = self.model.get_unpaid_months(student_id, current_year)
        
        if unpaid_months:
            self.unpaid_frame.setVisible(True)
            unpaid_text = ", ".join(unpaid_months)
            self.unpaid_months_label.setText(unpaid_text)
        else:
            self.unpaid_frame.setVisible(False)
    
    def validate_form(self):
        """Validate the form data."""
        student_id = self.student_combo.currentData()
        if not student_id:
            show_error(self, "Student selection is required")
            return False
        
        amount = self.amount_spinbox.value()
        if amount <= 0:
            show_error(self, "Amount is required")
            return False
        
        return True
    
    def save_fee(self):
        """Save the fee record."""
        if not self.validate_form():
            return
        
        try:
            # Build data dictionary
            data = {
                'student_id': self.student_combo.currentData(),
                'month': self.month_combo.currentText(),
                'year': self.year_combo.currentText(),
                'amount': self.amount_spinbox.value(),
                'payment_method': self.payment_combo.currentText(),
                'remarks': self.remarks_input.text()
            }
            
            # Save fee
            fee_id = self.model.add_fee(data)
            
            # Get receipt number for display
            fee_record = self.model.get_fees_by_student(data['student_id'])
            receipt_number = fee_record[0]['receipt_number'] if fee_record else "Unknown"
            
            # Show success message
            show_success(self, f"Fee collected successfully - Receipt Number: {receipt_number}")
            
            # Call callback if exists
            if self.on_save_callback:
                self.on_save_callback()
            
            # Reset form
            self.reset_form()
            
        except ValueError as e:
            show_error(self, str(e))
        except Exception as e:
            show_error(self, f"Error saving fee: {str(e)}")
    
    def reset_form(self):
        """Reset the form to initial state."""
        self.student_combo.setCurrentIndex(0)
        self.month_combo.setCurrentIndex(0)
        current_year = int(get_today_date().split('-')[0])
        for i in range(self.year_combo.count()):
            if self.year_combo.itemText(i) == str(current_year):
                self.year_combo.setCurrentIndex(i)
                break
        self.amount_spinbox.setValue(0)
        self.payment_combo.setCurrentIndex(0)
        self.remarks_input.clear()
        self.unpaid_frame.setVisible(False)
    
    def set_save_callback(self, callback):
        """Set callback function to be called after successful save."""
        self.on_save_callback = callback
