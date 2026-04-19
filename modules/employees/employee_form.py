from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit, 
    QComboBox, QDateEdit, QDoubleSpinBox, QPushButton, QFrame, QScrollArea, 
    QSizePolicy
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from ui.utils import get_urdu_font, show_error, show_success, validate_phone, validate_cnic, validate_required
from ui.styles import COLOR_ACCENT, COLOR_SIDEBAR
from .employee_model import EmployeeModel


class EmployeeForm(QWidget):
    
    def __init__(self, parent=None, employee_id=None, on_save_callback=None):
        super().__init__(parent)
        self.employee_id = employee_id
        self.on_save_callback = on_save_callback
        self.model = EmployeeModel()
        
        # Set RTL layout direction
        self.setLayoutDirection(Qt.RightToLeft)
        
        # Setup UI
        self.setup_ui()
        
        # Load employee data if in edit mode
        if self.employee_id is not None:
            self.load_employee_data()
    
    def setup_ui(self):
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Main container widget
        container = QWidget()
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(20)
        container_layout.setContentsMargins(20, 20, 20, 20)
        
        # Heading
        if self.employee_id is None:
            heading_text = "نیا ملازم داخل کریں"
        else:
            heading_text = "ملازم کی معلومات ترمیم کریں"
            
        self.heading_label = QLabel(heading_text)
        self.heading_label.setObjectName("heading_label")
        heading_font = get_urdu_font(18)
        heading_font.setBold(True)
        self.heading_label.setFont(heading_font)
        self.heading_label.setAlignment(Qt.AlignCenter)
        self.heading_label.setStyleSheet(f"color: {COLOR_ACCENT}; margin-bottom: 10px;")
        container_layout.addWidget(self.heading_label)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        
        # Full Name *
        self.full_name_input = QLineEdit()
        self.full_name_input.setPlaceholderText("ملازم کا پورا نام لکھیں")
        self.full_name_input.setFont(get_urdu_font(14))
        self.full_name_input.setLayoutDirection(Qt.RightToLeft)
        form_layout.addRow("پورا نام *", self.full_name_input)
        
        # Father Name
        self.father_name_input = QLineEdit()
        self.father_name_input.setPlaceholderText("والد کا نام لکھیں")
        self.father_name_input.setFont(get_urdu_font(14))
        self.father_name_input.setLayoutDirection(Qt.RightToLeft)
        form_layout.addRow("والد کا نام", self.father_name_input)
        
        # CNIC *
        self.cnic_input = QLineEdit()
        self.cnic_input.setPlaceholderText("XXXXX-XXXXXXX-X")
        self.cnic_input.setFont(get_urdu_font(14))
        self.cnic_input.setLayoutDirection(Qt.RightToLeft)
        form_layout.addRow("شناختی کارڈ *", self.cnic_input)
        
        # Designation *
        self.designation_input = QComboBox()
        designations = self.model.get_designations()
        self.designation_input.addItems(designations)
        self.designation_input.setFont(get_urdu_font(14))
        self.designation_input.setLayoutDirection(Qt.RightToLeft)
        form_layout.addRow("عہدہ *", self.designation_input)
        
        # Qualification
        self.qualification_input = QLineEdit()
        self.qualification_input.setPlaceholderText("تعلیمی قابلیت لکھیں")
        self.qualification_input.setFont(get_urdu_font(14))
        self.qualification_input.setLayoutDirection(Qt.RightToLeft)
        form_layout.addRow("تعلیم", self.qualification_input)
        
        # Joining Date
        self.joining_date_input = QDateEdit()
        self.joining_date_input.setDate(QDate.currentDate())
        self.joining_date_input.setCalendarPopup(True)
        self.joining_date_input.setFont(get_urdu_font(14))
        self.joining_date_input.setLayoutDirection(Qt.RightToLeft)
        form_layout.addRow("شمولیت کی تاریخ", self.joining_date_input)
        
        # Salary
        self.salary_input = QDoubleSpinBox()
        self.salary_input.setRange(0, 999999)
        self.salary_input.setSuffix(" روپے")
        self.salary_input.setFont(get_urdu_font(14))
        self.salary_input.setLayoutDirection(Qt.RightToLeft)
        form_layout.addRow("تنخواہ", self.salary_input)
        
        # Phone Number
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("03XX-XXXXXXX")
        self.phone_input.setFont(get_urdu_font(14))
        self.phone_input.setLayoutDirection(Qt.RightToLeft)
        form_layout.addRow("فون نمبر", self.phone_input)
        
        # Address
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("مکمل پتہ لکھیں")
        self.address_input.setFont(get_urdu_font(14))
        self.address_input.setLayoutDirection(Qt.RightToLeft)
        form_layout.addRow("پتہ", self.address_input)
        
        container_layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Save button
        self.save_button = QPushButton("محفوظ کریں")
        self.save_button.setFont(get_urdu_font(14))
        self.save_button.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_ACCENT};
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #e6b800;
            }}
        """)
        self.save_button.clicked.connect(self.save_employee)
        
        # Cancel button
        self.cancel_button = QPushButton("منسوخ کریں")
        self.cancel_button.setObjectName("danger_btn")
        self.cancel_button.setFont(get_urdu_font(14))
        self.cancel_button.setStyleSheet("""
            QPushButton#danger_btn {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton#danger_btn:hover {
                background-color: #c82333;
            }
        """)
        self.cancel_button.clicked.connect(self.cancel)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        
        container_layout.addLayout(button_layout)
        container_layout.addStretch()
        
        # Set scroll area content
        scroll_area.setWidget(container)
        
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(scroll_area)
    
    def validate_form(self):
        """Validate form inputs"""
        # Validate full name
        if not validate_required(self.full_name_input.text()):
            show_error(self, "ملازم کا نام لازمی ہے")
            return False
        
        # Validate designation
        if self.designation_input.currentIndex() == -1 or not self.designation_input.currentText():
            show_error(self, "عہدہ کا انتخاب لازمی ہے")
            return False
        
        # Validate CNIC if provided
        cnic_text = self.cnic_input.text().strip()
        if cnic_text and not validate_cnic(cnic_text):
            show_error(self, "شناختی کارڈ نمبر غلط ہے")
            return False
        
        # Validate phone if provided
        phone_text = self.phone_input.text().strip()
        if phone_text and not validate_phone(phone_text):
            show_error(self, "فون نمبر غلط ہے")
            return False
        
        return True
    
    def save_employee(self):
        """Save employee data"""
        if not self.validate_form():
            return
        
        # Build data dictionary
        data = {
            'full_name': self.full_name_input.text().strip(),
            'father_name': self.father_name_input.text().strip(),
            'cnic': self.cnic_input.text().strip(),
            'designation': self.designation_input.currentText(),
            'qualification': self.qualification_input.text().strip(),
            'joining_date': self.joining_date_input.date().toString('yyyy-MM-dd'),
            'salary': self.salary_input.value(),
            'phone_number': self.phone_input.text().strip(),
            'address': self.address_input.text().strip()
        }
        
        try:
            if self.employee_id is None:
                # Add new employee
                self.model.add_employee(data)
            else:
                # Update existing employee
                self.model.update_employee(self.employee_id, data)
            
            show_success(self, "ملازم کی معلومات کامیابی سے محفوظ ہو گئیں")
            
            # Call callback if exists
            if self.on_save_callback:
                self.on_save_callback()
                
        except ValueError as e:
            show_error(self, str(e))
        except Exception as e:
            show_error(self, f"Error saving employee: {str(e)}")
    
    def load_employee_data(self):
        """Load employee data for editing"""
        try:
            employee = self.model.get_employee_by_id(self.employee_id)
            if employee:
                # Populate form fields
                self.full_name_input.setText(employee.get('full_name', ''))
                self.father_name_input.setText(employee.get('father_name', ''))
                self.cnic_input.setText(employee.get('cnic', ''))
                self.qualification_input.setText(employee.get('qualification', ''))
                self.phone_input.setText(employee.get('phone_number', ''))
                self.address_input.setText(employee.get('address', ''))
                
                # Set designation
                designation = employee.get('designation', '')
                index = self.designation_input.findText(designation)
                if index >= 0:
                    self.designation_input.setCurrentIndex(index)
                
                # Set joining date
                if employee.get('joining_date'):
                    date = QDate.fromString(employee['joining_date'], 'yyyy-MM-dd')
                    if date.isValid():
                        self.joining_date_input.setDate(date)
                
                # Set salary
                self.salary_input.setValue(employee.get('salary', 0))
                
        except Exception as e:
            show_error(self, f"ملازم کا ڈیٹا لوڈ کرنے میں خطا: {str(e)}")
    
    def cancel(self):
        """Handle cancel action"""
        if self.on_save_callback:
            self.on_save_callback()
        else:
            self.clear_form()
    
    def clear_form(self):
        """Clear all form fields"""
        self.full_name_input.clear()
        self.father_name_input.clear()
        self.cnic_input.clear()
        self.designation_input.setCurrentIndex(0)
        self.qualification_input.clear()
        self.joining_date_input.setDate(QDate.currentDate())
        self.salary_input.setValue(0)
        self.phone_input.clear()
        self.address_input.clear()
