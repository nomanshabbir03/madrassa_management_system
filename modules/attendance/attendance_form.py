from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QTableWidget, QTableWidgetItem,
                             QDateEdit, QHeaderView, QSpinBox, QShortcut)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QKeySequence
from .attendance_model import AttendanceModel
from ui.utils import get_urdu_font, show_error, show_success, get_today_date
from ui.styles import apply_table_style
from ui.styles import COLOR_SUCCESS


class AttendanceWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.model = AttendanceModel()
        self.setLayoutDirection(Qt.RightToLeft)
        self.setup_ui()
        self.setup_shortcuts()
    
    def setup_ui(self):
        """Setup the UI for attendance marking."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Heading
        heading_label = QLabel("حاضری درج کریں")
        heading_label.setObjectName("heading_label")
        heading_label.setFont(get_urdu_font(18, bold=True))
        heading_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(heading_label)
        
        # Top controls bar
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(15)
        
        # Date input
        date_label = QLabel("تاریخ:")
        date_label.setFont(get_urdu_font(14))
        self.date_input = QDateEdit()
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setCalendarPopup(True)
        self.date_input.setFont(get_urdu_font(14))
        self.date_input.setFixedWidth(150)
        
        # Person type combo
        type_label = QLabel("قسم:")
        type_label.setFont(get_urdu_font(14))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["طلباء", "ملازمین"])
        self.type_combo.setFont(get_urdu_font(14))
        self.type_combo.setFixedWidth(120)
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        
        # Class combo (only for students)
        class_label = QLabel("درجہ:")
        class_label.setFont(get_urdu_font(14))
        self.class_combo = QComboBox()
        self.class_combo.setFont(get_urdu_font(14))
        self.class_combo.setFixedWidth(120)
        
        # Buttons
        self.load_btn = QPushButton("حاضری لوڈ کریں")
        self.load_btn.setFont(get_urdu_font(12))
        self.load_btn.setStyleSheet(f"background-color: {COLOR_SUCCESS}; color: white;")
        self.load_btn.clicked.connect(self.load_attendance_list)
        
        self.mark_all_btn = QPushButton("تمام حاضر")
        self.mark_all_btn.setFont(get_urdu_font(12))
        self.mark_all_btn.setStyleSheet("background-color: #28A745; color: white;")
        self.mark_all_btn.clicked.connect(self.mark_all_present)
        
        self.save_btn = QPushButton("محفوظ کریں")
        self.save_btn.setFont(get_urdu_font(12))
        self.save_btn.setStyleSheet("background-color: #28A745; color: white;")
        self.save_btn.clicked.connect(self.save_attendance)
        
        # Add controls to layout
        controls_layout.addWidget(date_label)
        controls_layout.addWidget(self.date_input)
        controls_layout.addWidget(type_label)
        controls_layout.addWidget(self.type_combo)
        controls_layout.addWidget(class_label)
        controls_layout.addWidget(self.class_combo)
        controls_layout.addStretch()
        controls_layout.addWidget(self.load_btn)
        controls_layout.addWidget(self.mark_all_btn)
        controls_layout.addWidget(self.save_btn)
        
        main_layout.addLayout(controls_layout)
        
        # Attendance table
        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(5)
        self.attendance_table.setHorizontalHeaderLabels([
            "شمار", "شناخت", "نام", "درجہ/عہدہ", "حاضری"
        ])
        apply_table_style(self.attendance_table)
        main_layout.addWidget(self.attendance_table)
        
        # Summary bar
        summary_layout = QHBoxLayout()
        summary_layout.setSpacing(30)
        
        self.present_label = QLabel("حاضر: ۰")
        self.present_label.setFont(get_urdu_font(14, bold=True))
        self.present_label.setStyleSheet("color: #28A745;")
        
        self.absent_label = QLabel("غیر حاضر: ۰")
        self.absent_label.setFont(get_urdu_font(14, bold=True))
        self.absent_label.setStyleSheet("color: #DC3545;")
        
        self.leave_label = QLabel("رخصت: ۰")
        self.leave_label.setFont(get_urdu_font(14, bold=True))
        self.leave_label.setStyleSheet("color: #FFC107;")
        
        summary_layout.addStretch()
        summary_layout.addWidget(self.present_label)
        summary_layout.addWidget(self.absent_label)
        summary_layout.addWidget(self.leave_label)
        summary_layout.addStretch()
        
        main_layout.addLayout(summary_layout)
        
        # Initially hide class combo (will be shown based on type selection)
        class_label.hide()
        self.class_combo.hide()
        
        # Load initial data
        self.load_classes()
    
    def load_classes(self):
        """Load classes into class combo box."""
        try:
            classes = self.model.get_all_classes()
            self.class_combo.clear()
            self.class_combo.addItems(classes)
        except Exception as e:
            print(f"Error loading classes: {e}")
    
    def on_type_changed(self):
        """Handle person type selection change."""
        selected_type = self.type_combo.currentText()
        
        if selected_type == "طلباء":
            # Show class combo for students
            self.class_combo.parent().show() if self.class_combo.parent() else None
            self.class_combo.show()
        else:
            # Hide class combo for employees
            self.class_combo.hide()
        
        # Clear table when type changes
        self.clear_table()
    
    def load_attendance_list(self):
        """Load attendance list based on selected criteria."""
        try:
            date = self.date_input.date().toString("yyyy-MM-dd")
            person_type = "student" if self.type_combo.currentText() == " Talba" else "employee"
            
            if person_type == "student":
                class_name = self.class_combo.currentText()
                persons = self.model.get_students_by_class(class_name)
            else:
                persons = self.model.get_all_employees_list()
            
            # Check existing attendance for this date
            existing_attendance = {}
            attendance_records = self.model.get_attendance_by_date(date, person_type)
            for record in attendance_records:
                existing_attendance[record['person_id']] = record['status']
            
            # Populate table
            self.populate_table(persons, existing_attendance)
            
        except Exception as e:
            show_error(self, f"حاضری لوڈ کرنے میں خطا: {str(e)}")
    
    def populate_table(self, persons, existing_attendance):
        """Populate attendance table with persons."""
        self.clear_table()
        self.attendance_table.setRowCount(len(persons))
        
        for row, person in enumerate(persons):
            # Serial number
            self.set_table_item(row, 0, str(row + 1))
            
            # Identifier (registration number or employee code)
            identifier = person.get('registration_number') or person.get('employee_code', '')
            self.set_table_item(row, 1, identifier)
            
            # Name
            self.set_table_item(row, 2, person['full_name'])
            
            # Class or designation
            class_or_designation = person.get('class_name') or person.get('designation', '')
            self.set_table_item(row, 3, class_or_designation)
            
            # Attendance status combo
            status_combo = QComboBox()
            status_combo.addItems(["حاضر", "غیر حاضر", "رخصت"])
            status_combo.setFont(get_urdu_font(13))
            
            # Set existing status if available
            if person['id'] in existing_attendance:
                status = existing_attendance[person['id']]
                if status == 'present':
                    status_combo.setCurrentText("حاضر")
                elif status == 'absent':
                    status_combo.setCurrentText("غیر حاضر")
                elif status == 'leave':
                    status_combo.setCurrentText("رخصت")
            
            # Store person_id in combo for later use
            status_combo.person_id = person['id']
            status_combo.currentTextChanged.connect(self.update_summary)
            
            self.attendance_table.setCellWidget(row, 4, status_combo)
        
        # Update summary
        self.update_summary()
        
        # Empty state msg
        if len(persons) == 0:
            show_error(self, "کوئی ریکارڈ نہیں ملا")

    def setup_shortcuts(self):
        """Setup shortcuts for attendance."""
        self.shortcut_save = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut_save.activated.connect(self.save_attendance)
        
        self.shortcut_refresh = QShortcut(QKeySequence("F5"), self)
        self.shortcut_refresh.activated.connect(self.load_attendance_list)
    
    def set_table_item(self, row, col, value):
        """Set table item with Urdu formatting."""
        item = QTableWidgetItem(str(value))
        item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
        item.setFont(get_urdu_font(13))
        item.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEnabled)
        self.attendance_table.setItem(row, col, item)
    
    def clear_table(self):
        """Clear the attendance table."""
        self.attendance_table.setRowCount(0)
        self.update_summary()
    
    def mark_all_present(self):
        """Mark all persons as present."""
        for row in range(self.attendance_table.rowCount()):
            status_combo = self.attendance_table.cellWidget(row, 4)
            if status_combo:
                status_combo.setCurrentText("Haazir")
        self.update_summary()
    
    def save_attendance(self):
        """Save attendance records."""
        try:
            date = self.date_input.date().toString("yyyy-MM-dd")
            person_type = "student" if self.type_combo.currentText() == " Talba" else "employee"
            
            records = []
            for row in range(self.attendance_table.rowCount()):
                status_combo = self.attendance_table.cellWidget(row, 4)
                if status_combo:
                    urdu_status = status_combo.currentText()
                    # Convert Urdu status to English
                    if urdu_status == "حاضر":
                        status = "present"
                    elif urdu_status == "غیر حاضر":
                        status = "absent"
                    else:  # رخصت
                        status = "leave"
                    
                    records.append({
                        'person_id': status_combo.person_id,
                        'person_type': person_type,
                        'status': status,
                        'remarks': ''
                    })
            
            # Save records
            count = self.model.bulk_mark_attendance(records, date)
            show_success(self, f"حاضری کامیابی سے محفوظ ہو گئی ({count} ریکارڈز)")
            
        except Exception as e:
            show_error(self, f"حاضری محفوظ کرنے میں خطا: {str(e)}")
    
    def update_summary(self):
        """Update attendance summary labels."""
        present = 0
        absent = 0
        leave = 0
        
        for row in range(self.attendance_table.rowCount()):
            status_combo = self.attendance_table.cellWidget(row, 4)
            if status_combo:
                status = status_combo.currentText()
                if status == "حاضر":
                    present += 1
                elif status == "غیر حاضر":
                    absent += 1
                elif status == "رخصت":
                    leave += 1
        
        # Update labels with Urdu numerals
        from ui.utils import to_urdu_numerals
        self.present_label.setText(f"حاضر: {to_urdu_numerals(present)}")
        self.absent_label.setText(f"غیر حاضر: {to_urdu_numerals(absent)}")
        self.leave_label.setText(f"رخصت: {to_urdu_numerals(leave)}")
