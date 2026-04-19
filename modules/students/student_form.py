from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, QLineEdit, 
                             QComboBox, QDateEdit, QPushButton, QFileDialog, QFrame, 
                             QScrollArea, QSizePolicy)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt, QDate
from ui.utils import get_urdu_font, show_error, show_success, validate_phone, validate_required
from ui.styles import COLOR_ACCENT, COLOR_SIDEBAR
from modules.students.student_model import StudentModel
import os


class StudentForm(QWidget):
    def __init__(self, parent=None, student_id=None, on_save_callback=None):
        super().__init__(parent)
        self.model = StudentModel()
        self.student_id = student_id
        self.on_save_callback = on_save_callback
        self.photo_path = None
        self.setLayoutDirection(Qt.RightToLeft)
        self.setup_ui()
        
        if student_id is not None:
            self.load_student_data()

    def setup_ui(self):
        # Main layout with scroll area
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Create scroll widget
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(20)
        
        # Heading
        is_edit_mode = self.student_id is not None
        heading_text = "طالب علم کی ترمیم کریں" if is_edit_mode else "نیا طالب علم داخل کریں"
        
        heading_label = QLabel(heading_text)
        heading_label.setObjectName("heading_label")
        heading_label.setFont(get_urdu_font(18, bold=True))
        heading_label.setStyleSheet(f"color: {COLOR_SIDEBAR};")
        heading_label.setAlignment(Qt.AlignCenter)
        scroll_layout.addWidget(heading_label)
        
        # Form layout
        form_layout = QFormLayout()
        form_layout.setSpacing(15)
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFormAlignment(Qt.AlignRight)
        
        # Full Name
        self.full_name_edit = QLineEdit()
        self.full_name_edit.setObjectName("full_name")
        self.full_name_edit.setFont(get_urdu_font(14))
        self.full_name_edit.setPlaceholderText("طالب علم کا پورا نام لکھیں")
        self.full_name_edit.setLayoutDirection(Qt.RightToLeft)
        form_layout.addRow("پورا نام *:", self.full_name_edit)
        
        # Father Name
        self.father_name_edit = QLineEdit()
        self.father_name_edit.setObjectName("father_name")
        self.father_name_edit.setFont(get_urdu_font(14))
        self.father_name_edit.setPlaceholderText("والد کا نام لکھیں")
        self.father_name_edit.setLayoutDirection(Qt.RightToLeft)
        form_layout.addRow("والد کا نام:", self.father_name_edit)
        
        # Date of Birth
        self.dob_edit = QDateEdit()
        self.dob_edit.setObjectName("dob")
        self.dob_edit.setFont(get_urdu_font(14))
        self.dob_edit.setCalendarPopup(True)
        self.dob_edit.setDisplayFormat("dd/MM/yyyy")
        self.dob_edit.setDate(QDate.currentDate().addYears(-10))
        self.dob_edit.setLayoutDirection(Qt.RightToLeft)
        form_layout.addRow("تاریخ پیدائش:", self.dob_edit)
        
        # CNIC / B-Form
        self.cnic_edit = QLineEdit()
        self.cnic_edit.setObjectName("cnic")
        self.cnic_edit.setFont(get_urdu_font(14))
        self.cnic_edit.setPlaceholderText("XXXXX-XXXXXXX-X")
        self.cnic_edit.setLayoutDirection(Qt.RightToLeft)
        form_layout.addRow("شناختی کارڈ / بی-فارم:", self.cnic_edit)
        
        # Class
        self.class_combo = QComboBox()
        self.class_combo.setObjectName("class_name")
        self.class_combo.setFont(get_urdu_font(14))
        self.class_combo.setLayoutDirection(Qt.RightToLeft)
        self.load_classes()
        form_layout.addRow("درجہ *:", self.class_combo)
        
        # Admission Date
        self.admission_date_edit = QDateEdit()
        self.admission_date_edit.setObjectName("admission_date")
        self.admission_date_edit.setFont(get_urdu_font(14))
        self.admission_date_edit.setCalendarPopup(True)
        self.admission_date_edit.setDate(QDate.currentDate())
        self.admission_date_edit.setLayoutDirection(Qt.RightToLeft)
        form_layout.addRow("داخلہ کی تاریخ:", self.admission_date_edit)
        
        # Phone Number
        self.phone_edit = QLineEdit()
        self.phone_edit.setObjectName("phone")
        self.phone_edit.setFont(get_urdu_font(14))
        self.phone_edit.setPlaceholderText("03XX-XXXXXXX")
        self.phone_edit.setLayoutDirection(Qt.RightToLeft)
        form_layout.addRow("فون نمبر:", self.phone_edit)
        
        # Address
        self.address_edit = QLineEdit()
        self.address_edit.setObjectName("address")
        self.address_edit.setFont(get_urdu_font(14))
        self.address_edit.setPlaceholderText("مکمل پتہ لکھیں")
        self.address_edit.setLayoutDirection(Qt.RightToLeft)
        form_layout.addRow("پتہ:", self.address_edit)
        
        # Photo section
        photo_layout = QVBoxLayout()
        
        # Photo button
        self.photo_btn = QPushButton("تصویر منتخب کریں")
        self.photo_btn.setFont(get_urdu_font(14))
        self.photo_btn.clicked.connect(self.select_photo)
        photo_layout.addWidget(self.photo_btn)
        
        # Photo preview
        self.photo_label = QLabel("تصویر نہیں")
        self.photo_label.setFixedSize(120, 120)
        self.photo_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #ccc;
                border-radius: 8px;
                background-color: #f9f9f9;
            }
        """)
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.photo_label.setFont(get_urdu_font(12))
        photo_layout.addWidget(self.photo_label)
        
        form_layout.addRow("تصویر:", photo_layout)
        
        scroll_layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Save button
        self.save_btn = QPushButton("محفوظ کریں")
        self.save_btn.setFont(get_urdu_font(14))
        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_ACCENT};
                color: white;
                padding: 12px 30px;
                border-radius: 8px;
                font-weight: bold;
                min-height: 40px;
            }}
            QPushButton:hover {{
                background-color: #B8860B;
            }}
        """)
        self.save_btn.clicked.connect(self.save_student)
        
        # Cancel button
        self.cancel_btn = QPushButton("منسوخ کریں")
        self.cancel_btn.setFont(get_urdu_font(14))
        self.cancel_btn.setObjectName("danger_btn")
        self.cancel_btn.setStyleSheet("""
            QPushButton#danger_btn {
                background-color: #DC3545;
                color: white;
                padding: 12px 30px;
                border-radius: 8px;
                font-weight: bold;
                min-height: 40px;
            }
            QPushButton#danger_btn:hover {
                background-color: #C82333;
            }
        """)
        self.cancel_btn.clicked.connect(self.cancel)
        
        button_layout.addStretch()
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        
        scroll_layout.addLayout(button_layout)
        scroll_layout.addStretch()
        
        # Set scroll area content
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)

    def load_classes(self):
        """Load classes into combo box."""
        try:
            classes = self.model.get_classes()
            self.class_combo.clear()
            self.class_combo.addItem("درجہ انتخاب کریں")
            self.class_combo.addItems(classes)
        except Exception as e:
            show_error(self, str(e))

    def select_photo(self):
        """Open file dialog to select photo."""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "تصویر انتخاب کریں", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        
        if file_path:
            self.photo_path = file_path
            # Update photo preview
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.photo_label.setPixmap(scaled_pixmap)
                self.photo_label.setText("")

    def validate_form(self):
        """Validate form fields."""
        # Check full name
        full_name = self.full_name_edit.text().strip()
        if not validate_required(full_name):
            show_error(self, "طالب علم کا نام لازمی ہے")
            return False
        
        # Check class selection
        class_name = self.class_combo.currentText()
        if class_name == "درجہ انتخاب کریں" or not class_name.strip():
            show_error(self, "درجہ کا انتخاب لازمی ہے")
            return False
        
        # Check phone if provided
        phone = self.phone_edit.text().strip()
        if phone and not validate_phone(phone):
            show_error(self, "فون نمبر غلط ہے - 10 یا 11 ہندسے درکار ہیں")
            return False
        
        return True

    def save_student(self):
        """Save student data."""
        if not self.validate_form():
            return
        
        try:
            # Build data dictionary
            data = {
                'full_name': self.full_name_edit.text().strip(),
                'father_name': self.father_name_edit.text().strip(),
                'date_of_birth': self.dob_edit.date().toString("yyyy-MM-dd"),
                'cnic_or_bform': self.cnic_edit.text().strip(),
                'class_name': self.class_combo.currentText(),
                'admission_date': self.admission_date_edit.date().toString("yyyy-MM-dd"),
                'phone_number': self.phone_edit.text().strip(),
                'address': self.address_edit.text().strip(),
                'photo_path': self.photo_path or ''
            }
            
            if self.student_id is None:
                # Add new student
                self.model.add_student(data)
            else:
                # Update existing student
                self.model.update_student(self.student_id, data)
            
            show_success(self, "طالب علم کی معلومات کامیابی سے محفوظ ہو گئیں")
            
            # Call callback if exists
            if self.on_save_callback:
                self.on_save_callback()
            
        except ValueError as e:
            show_error(self, str(e))
        except Exception as e:
            show_error(self, f"طالب علم محفوظ کرنے میں خطا: {str(e)}")

    def load_student_data(self):
        """Load existing student data for editing."""
        try:
            student = self.model.get_student_by_id(self.student_id)
            if student:
                # Populate form fields
                self.full_name_edit.setText(student['full_name'])
                self.father_name_edit.setText(student['father_name'])
                self.phone_edit.setText(student['phone_number'])
                self.cnic_edit.setText(student['cnic_or_bform'])
                self.address_edit.setText(student['address'])
                
                # Set class
                index = self.class_combo.findText(student['class_name'])
                if index >= 0:
                    self.class_combo.setCurrentIndex(index)
                
                # Set dates
                if student['date_of_birth']:
                    dob = QDate.fromString(student['date_of_birth'], "yyyy-MM-dd")
                    if dob.isValid():
                        self.dob_edit.setDate(dob)
                
                if student['admission_date']:
                    admission = QDate.fromString(student['admission_date'], "yyyy-MM-dd")
                    if admission.isValid():
                        self.admission_date_edit.setDate(admission)
                
                # Load photo if exists
                if student.get('photo_path') and os.path.exists(student['photo_path']):
                    self.photo_path = student['photo_path']
                    pixmap = QPixmap(self.photo_path)
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        self.photo_label.setPixmap(scaled_pixmap)
                        self.photo_label.setText("")
                        
        except Exception as e:
            show_error(self, f"طالب علم واپس کرنے میں خطا: {str(e)}")

    def cancel(self):
        """Handle cancel action."""
        if self.on_save_callback:
            self.on_save_callback()
        else:
            self.clear_form()

    def clear_form(self):
        """Clear all form fields."""
        self.full_name_edit.clear()
        self.father_name_edit.clear()
        self.cnic_edit.clear()
        self.phone_edit.clear()
        self.address_edit.clear()
        self.class_combo.setCurrentIndex(0)
        self.dob_edit.setDate(QDate.currentDate().addYears(-10))
        self.admission_date_edit.setDate(QDate.currentDate())
        
        # Clear photo
        self.photo_path = None
        self.photo_label.clear()
        self.photo_label.setText("تصویر نہیں")
