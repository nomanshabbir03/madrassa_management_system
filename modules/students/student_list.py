from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
                             QPushButton, QLabel, QLineEdit, QComboBox, QHeaderView, QAbstractItemView, 
                             QFrame, QSizePolicy, QMessageBox)
from PyQt5.QtCore import Qt
from ui.utils import get_urdu_font, show_error, show_success, show_confirm, set_table_item_urdu, clear_table, to_urdu_numerals
from ui.styles import apply_table_style, COLOR_SIDEBAR, COLOR_ACCENT, COLOR_ERROR
from modules.students.student_model import StudentModel
from modules.students.student_form import StudentForm


class StudentList(QWidget):
    def __init__(self):
        super().__init__()
        self.model = StudentModel()
        self.current_form = None
        self.search_input = None
        self.class_filter = None
        self.status_filter = None
        self.table = None
        self.status_label = None
        self.setLayoutDirection(Qt.RightToLeft)
        self.setup_ui()
        self.load_students()

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Top bar with heading and add button
        top_bar = QHBoxLayout()
        
        # Heading
        heading_label = QLabel("طلباء کی فہرست")
        heading_label.setObjectName("heading_label")
        heading_label.setFont(get_urdu_font(18, bold=True))
        heading_label.setStyleSheet(f"color: {COLOR_SIDEBAR};")
        
        # Add button
        add_btn = QPushButton("نیا طالب علم +")
        add_btn.setFont(get_urdu_font(14))
        add_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_ACCENT};
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #B8860B;
            }}
        """)
        add_btn.clicked.connect(self.show_add_form)
        
        top_bar.addWidget(heading_label)
        top_bar.addStretch()
        top_bar.addWidget(add_btn)
        
        main_layout.addLayout(top_bar)
        
        # Filter bar
        filter_frame = QFrame()
        filter_frame.setStyleSheet("""
            QFrame {
                background-color: #F8F9FA;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        filter_layout = QHBoxLayout(filter_frame)
        filter_layout.setSpacing(15)
        
        # Search
        search_label = QLabel("تلاش:")
        search_label.setFont(get_urdu_font(14))
        
        self.search_input = QLineEdit()
        self.search_input.setFont(get_urdu_font(14))
        self.search_input.setPlaceholderText("نام یا رجسٹریشن نمبر سے تلاش کریں")
        self.search_input.setMaximumWidth(300)
        
        # Class filter
        class_label = QLabel("درجہ:")
        class_label.setFont(get_urdu_font(14))
        
        self.class_filter = QComboBox()
        self.class_filter.setFont(get_urdu_font(14))
        self.class_filter.setMaximumWidth(150)
        
        # Status filter
        status_label = QLabel("حالت:")
        status_label.setFont(get_urdu_font(14))
        
        self.status_filter = QComboBox()
        self.status_filter.setFont(get_urdu_font(14))
        self.status_filter.setMaximumWidth(120)
        self.status_filter.addItems(["فعال", "غیر فعال", "تمام"])
        
        # Refresh button
        refresh_btn = QPushButton("تازہ کریں")
        refresh_btn.setFont(get_urdu_font(14))
        refresh_btn.clicked.connect(self.load_students)
        
        filter_layout.addWidget(search_label)
        filter_layout.addWidget(self.search_input)
        filter_layout.addWidget(class_label)
        filter_layout.addWidget(self.class_filter)
        filter_layout.addWidget(status_label)
        filter_layout.addWidget(self.status_filter)
        filter_layout.addWidget(refresh_btn)
        filter_layout.addStretch()
        
        main_layout.addWidget(filter_frame)
        
        # Table (Initialize early to avoid NoneType errors)
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        
        headers = ["شمار", "رجسٹریشن نمبر", "پورا نام", "والد کا نام", "درجہ", "فون نمبر", "داخلہ تاریخ", "اعمال"]
        self.table.setHorizontalHeaderLabels(headers)
        
        # Apply table style
        apply_table_style(self.table)
        
        # Set selection mode
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.resizeSection(0, 50)   # #
        header.resizeSection(1, 150) # Registration
        header.resizeSection(2, 180) # Name
        header.resizeSection(3, 150) # Father Name
        header.resizeSection(4, 120) # Class
        header.resizeSection(5, 120) # Phone
        header.resizeSection(6, 120) # Admission Date
        header.resizeSection(7, 150) # Actions
        
        # Make actions column not resizable
        header.setSectionResizeMode(7, QHeaderView.Fixed)
        
        main_layout.addWidget(self.table)
        
        # Now connect signals and load initial filter data
        self.search_input.textChanged.connect(self.on_search)
        self.class_filter.currentTextChanged.connect(self.on_filter_change)
        self.status_filter.currentTextChanged.connect(self.on_filter_change)
        self.load_classes()
        
        # Status bar
        status_bar = QHBoxLayout()
        
        self.status_label = QLabel("کل طلباء: 0")
        self.status_label.setFont(get_urdu_font(12))
        self.status_label.setStyleSheet("color: gray;")
        
        status_bar.addWidget(self.status_label)
        status_bar.addStretch()
        
        main_layout.addLayout(status_bar)
        
        self.setLayout(main_layout)

    def load_students(self, search=None, class_filter=None, status_filter='active'):
        """Load students into table."""
        try:
            if self.table is None:
                return
            
            students = self.model.get_all_students(search, class_filter, status_filter)
            
            # Clear table
            clear_table(self.table)
            self.table.setRowCount(len(students))
            
            for row, student in enumerate(students):
                # Serial number
                set_table_item_urdu(self.table, row, 0, str(row + 1))
                
                # Registration number
                set_table_item_urdu(self.table, row, 1, student['registration_number'])
                
                # Name
                set_table_item_urdu(self.table, row, 2, student['full_name'])
                
                # Father name
                set_table_item_urdu(self.table, row, 3, student['father_name'])
                
                # Class
                set_table_item_urdu(self.table, row, 4, student['class_name'])
                
                # Phone
                set_table_item_urdu(self.table, row, 5, student['phone_number'])
                
                # Admission date
                set_table_item_urdu(self.table, row, 6, student['admission_date'])
                
                # Actions column
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 2, 5, 2)
                actions_layout.setSpacing(5)
                
                # View button
                view_btn = QPushButton("تفصیل")
                view_btn.setFont(get_urdu_font(10))
                view_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLOR_ACCENT};
                        color: white;
                        padding: 4px 8px;
                        border-radius: 4px;
                        font-size: 10px;
                        min-height: 25px;
                    }}
                """)
                view_btn.clicked.connect(lambda checked, sid=student['id']: self.view_student(sid))
                
                # Edit button
                edit_btn = QPushButton("ترمیم")
                edit_btn.setFont(get_urdu_font(10))
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2D6A4F;
                        color: white;
                        padding: 4px 8px;
                        border-radius: 4px;
                        font-size: 10px;
                        min-height: 25px;
                    }
                """)
                edit_btn.clicked.connect(lambda checked, sid=student['id']: self.edit_student(sid))
                
                # Delete button
                delete_btn = QPushButton("حذف")
                delete_btn.setFont(get_urdu_font(10))
                delete_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {COLOR_ERROR};
                        color: white;
                        padding: 4px 8px;
                        border-radius: 4px;
                        font-size: 10px;
                        min-height: 25px;
                    }}
                """)
                delete_btn.clicked.connect(lambda checked, sid=student['id']: self.delete_student(sid))
                
                actions_layout.addWidget(view_btn)
                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)
                
                self.table.setCellWidget(row, 7, actions_widget)
            
            # Update status label
            count_text = f"کل طلباء: {to_urdu_numerals(len(students))}"
            self.status_label.setText(count_text)
            
        except Exception as e:
            show_error(self, str(e))

    def load_classes(self):
        """Load classes into filter combo box."""
        try:
            classes = self.model.get_classes()
            self.class_filter.clear()
            self.class_filter.addItem("تمام درجات")
            self.class_filter.addItems(classes)
        except Exception as e:
            show_error(self, str(e))

    def on_search(self):
        """Handle search input change."""
        try:
            search_text = ""
            if self.search_input:
                search_text = self.search_input.text().strip()
            self.load_students(search=search_text if search_text else None)
        except Exception as e:
            print(f"Error in search: {e}")
            # Fallback to loading all students
            self.load_students()

    def on_filter_change(self):
        """Handle filter change."""
        try:
            # Get class filter
            class_filter = None
            if self.class_filter:
                class_filter = self.class_filter.currentText()
                class_filter = None if class_filter == "تمام درجات" else class_filter
            
            # Get status filter
            status_filter = None
            if self.status_filter:
                status_filter = self.status_filter.currentText()
                if status_filter == "فعال":
                    status_filter = 'active'
                elif status_filter == "غیر فعال":
                    status_filter = 'left'
                else:
                    status_filter = None
            
            self.load_students(class_filter=class_filter, status_filter=status_filter)
        except Exception as e:
            print(f"Error in filter change: {e}")
            # Fallback to loading all students
            self.load_students()

    def show_add_form(self):
        """Show add student form."""
        form = StudentForm(on_save_callback=self.on_form_saved)
        self.current_form = form
        
        # Replace current content with form
        layout = self.layout()
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget and widget != self.current_form:
                widget.hide()
        
        layout.addWidget(form)

    def edit_student(self, student_id):
        """Show edit student form."""
        form = StudentForm(student_id=student_id, on_save_callback=self.on_form_saved)
        self.current_form = form
        
        # Replace current content with form
        layout = self.layout()
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget and widget != self.current_form:
                widget.hide()
        
        layout.addWidget(form)

    def view_student(self, student_id):
        """Show student details in message box."""
        try:
            student = self.model.get_student_by_id(student_id)
            if not student:
                show_error(self, "طالب علم نہیں ملا")
                return
            
            # Format student details
            details = f"""
            <b>طالب علم کی تفصیل</b><br><br>
            <b>رجسٹریشن نمبر:</b> {student['registration_number']}<br>
            <b>پورا نام:</b> {student['full_name']}<br>
            <b>والد کا نام:</b> {student['father_name']}<br>
            <b>تاریخ پیدائش:</b> {student['date_of_birth']}<br>
            <b>شناختی کارڈ:</b> {student['cnic_or_bform']}<br>
            <b>درجہ:</b> {student['class_name']}<br>
            <b>داخلہ کی تاریخ:</b> {student['admission_date']}<br>
            <b>فون نمبر:</b> {student['phone_number']}<br>
            <b>پتہ:</b> {student['address']}<br>
            <b>حالت:</b> {'فعال' if student['status'] == 'active' else 'چھکا گیا'}
            """
            
            msg = QMessageBox(self)
            msg.setWindowTitle("طالب علم تفصیل")
            msg.setTextFormat(Qt.RichText)
            msg.setText(details)
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setFont(get_urdu_font(12))
            msg.exec_()
            
        except Exception as e:
            show_error(self, str(e))

    def delete_student(self, student_id):
        """Delete student after confirmation."""
        if not show_confirm(self, "کیا آپ واقعی اس طالب علم کو حذف کرنا چاہتے ہیں?"):
            return
        
        try:
            self.model.delete_student(student_id)
            show_success(self, "طالب علم کامیابی سے حذف ہو گیا")
            self.load_students()
        except Exception as e:
            show_error(self, str(e))

    def on_form_saved(self):
        """Handle form save callback."""
        self.show_table_view()
        self.load_students()

    def show_table_view(self):
        """Show table view and hide form."""
        if self.current_form:
            self.current_form.hide()
            self.current_form = None
        
        # Show all table widgets
        layout = self.layout()
        for i in range(layout.count()):
            widget = layout.itemAt(i).widget()
            if widget:
                widget.show()
