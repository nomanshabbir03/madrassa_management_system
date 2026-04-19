from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QFrame, QStackedWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from .employee_model import EmployeeModel
from .employee_form import EmployeeForm
from ui.utils import get_urdu_font, show_error, show_success
from ui.styles import apply_table_style


class EmployeeList(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = EmployeeModel()
        self.current_form = None
        
        # Set RTL layout direction
        self.setLayoutDirection(Qt.RightToLeft)
        
        # Create stacked widget for switching views
        self.stack = QStackedWidget()
        
        # Setup main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self.stack)
        
        # Setup list view
        self.setup_list_view()
        self.stack.addWidget(self.list_widget)
        
        # Load initial data
        self.load_employees()
    
    def setup_list_view(self):
        # Create list widget
        self.list_widget = QWidget()
        layout = QVBoxLayout(self.list_widget)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header section
        header_layout = QHBoxLayout()
        
        # Heading
        self.heading_label = QLabel("ملازمین کی فہرست")
        self.heading_label.setFont(get_urdu_font(18))
        self.heading_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
        header_layout.addWidget(self.heading_label)
        
        header_layout.addStretch()
        
        # Add button
        self.add_button = QPushButton("نیا ملازم +")
        self.add_button.setFont(get_urdu_font(14))
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.add_button.clicked.connect(self.show_add_form)
        header_layout.addWidget(self.add_button)
        
        layout.addLayout(header_layout)
        
        # Search and filter section
        search_filter_layout = QHBoxLayout()
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("نام یا ملازم کوڈ سے تلاش کریں")
        self.search_input.setFont(get_urdu_font(14))
        self.search_input.setLayoutDirection(Qt.RightToLeft)
        self.search_input.textChanged.connect(self.on_search)
        search_filter_layout.addWidget(self.search_input)
        
        # Designation filter
        self.designation_filter = QComboBox()
        designation_items = ["تمام عہدے"] + self.model.get_designations()
        self.designation_filter.addItems(designation_items)
        self.designation_filter.setFont(get_urdu_font(14))
        self.designation_filter.setLayoutDirection(Qt.RightToLeft)
        self.designation_filter.currentTextChanged.connect(self.on_filter_change)
        search_filter_layout.addWidget(self.designation_filter)
        
        # Status filter
        self.status_filter = QComboBox()
        self.status_filter.addItems(["فعال", "غیر فعال", "تمام"])
        self.status_filter.setFont(get_urdu_font(14))
        self.status_filter.setLayoutDirection(Qt.RightToLeft)
        self.status_filter.currentTextChanged.connect(self.on_filter_change)
        search_filter_layout.addWidget(self.status_filter)
        
        # Refresh button
        self.refresh_button = QPushButton("تازہ کریں")
        self.refresh_button.setFont(get_urdu_font(14))
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.refresh_button.clicked.connect(self.load_employees)
        search_filter_layout.addWidget(self.refresh_button)
        
        layout.addLayout(search_filter_layout)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "شمار", "ملازم کوڈ", "پورا نام", "والد کا نام", 
            "عہدہ", "تنخواہ", "فون نمبر", "اعمال"
        ])
        
        # Apply table styling
        apply_table_style(self.table)
        
        # Set column widths
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # S.No
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Code
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Name
        header.setSectionResizeMode(3, QHeaderView.Stretch)           # Father Name
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Designation
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Salary
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Phone
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Actions
        
        layout.addWidget(self.table)
        
        # Status bar
        self.status_label = QLabel("کل ملازمین: 0")
        self.status_label.setFont(get_urdu_font(12))
        self.status_label.setStyleSheet("color: #7f8c8d; padding: 5px;")
        layout.addWidget(self.status_label)
    
    def load_employees(self):
        """Load employees into the table"""
        try:
            # Check if table and inputs exist
            if not hasattr(self, 'table') or self.table is None:
                return
            
            # Get filter values with safety checks
            search_text = ""
            if hasattr(self, 'search_input') and self.search_input:
                search_text = self.search_input.text().strip()
            
            designation_filter = "All Designations"
            if hasattr(self, 'designation_filter') and self.designation_filter:
                designation_filter = self.designation_filter.currentText()
            
            status_filter = "Active"
            if hasattr(self, 'status_filter') and self.status_filter:
                status_filter = self.status_filter.currentText()
            
            # Map English status to database values
            status_map = {"فعال": "active", "غیر فعال": "left", "تمام": None}
            db_status = status_map.get(status_filter)
            
            # Map designation filter
            db_designation = None if designation_filter == "تمام عہدے" else designation_filter
            
            # Get employees
            employees = self.model.get_all_employees(
                search=search_text if search_text else None,
                designation_filter=db_designation,
                status_filter=db_status
            )
            
            # Populate table
            self.table.setRowCount(len(employees))
            
            for row, employee in enumerate(employees):
                # S.No
                sno_item = QTableWidgetItem(str(row + 1))
                sno_item.setTextAlignment(Qt.AlignCenter)
                sno_item.setFont(get_urdu_font(12))
                self.table.setItem(row, 0, sno_item)
                
                # Employee Code
                code_item = QTableWidgetItem(employee.get('employee_code', ''))
                code_item.setTextAlignment(Qt.AlignCenter)
                code_item.setFont(get_urdu_font(12))
                self.table.setItem(row, 1, code_item)
                
                # Full Name
                name_item = QTableWidgetItem(employee.get('full_name', ''))
                name_item.setFont(get_urdu_font(12))
                self.table.setItem(row, 2, name_item)
                
                # Father Name
                father_item = QTableWidgetItem(employee.get('father_name', ''))
                father_item.setFont(get_urdu_font(12))
                self.table.setItem(row, 3, father_item)
                
                # Designation
                designation_item = QTableWidgetItem(employee.get('designation', ''))
                designation_item.setFont(get_urdu_font(12))
                self.table.setItem(row, 4, designation_item)
                
                # Salary
                salary_item = QTableWidgetItem(f"{employee.get('salary', 0):,.0f}")
                salary_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                salary_item.setFont(get_urdu_font(12))
                self.table.setItem(row, 5, salary_item)
                
                # Phone
                phone_item = QTableWidgetItem(employee.get('phone_number', ''))
                phone_item.setFont(get_urdu_font(12))
                self.table.setItem(row, 6, phone_item)
                
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 2, 5, 2)
                actions_layout.setSpacing(5)
                
                # View button
                view_btn = QPushButton("تفصیل")
                view_btn.setFont(get_urdu_font(10))
                view_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #3498db;
                        color: white;
                        border: none;
                        padding: 4px 8px;
                        border-radius: 3px;
                        font-size: 10px;
                    }
                    QPushButton:hover {
                        background-color: #2980b9;
                    }
                """)
                view_btn.clicked.connect(lambda checked, eid=employee['id']: self.view_employee(eid))
                actions_layout.addWidget(view_btn)
                
                # Edit button
                edit_btn = QPushButton("ترمیم")
                edit_btn.setFont(get_urdu_font(10))
                edit_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f39c12;
                        color: white;
                        border: none;
                        padding: 4px 8px;
                        border-radius: 3px;
                        font-size: 10px;
                    }
                    QPushButton:hover {
                        background-color: #e67e22;
                    }
                """)
                edit_btn.clicked.connect(lambda checked, eid=employee['id']: self.edit_employee(eid))
                actions_layout.addWidget(edit_btn)
                
                # Delete button
                delete_btn = QPushButton("حذف")
                delete_btn.setFont(get_urdu_font(10))
                delete_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border: none;
                        padding: 4px 8px;
                        border-radius: 3px;
                        font-size: 10px;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
                delete_btn.clicked.connect(lambda checked, eid=employee['id']: self.delete_employee(eid))
                actions_layout.addWidget(delete_btn)
                
                self.table.setCellWidget(row, 7, actions_widget)
            
            # Update status with safety check
            if hasattr(self, 'status_label') and self.status_label:
                self.status_label.setText(f"کل ملازمین: {len(employees)}")
            
        except Exception as e:
            show_error(self, f"ملازمین لوڈ کرنے میں خطا: {str(e)}")
    
    def show_add_form(self):
        """Show add employee form"""
        self.current_form = EmployeeForm(self, on_save_callback=self.on_form_saved)
        
        # Add form to stack and show it
        self.stack.addWidget(self.current_form)
        self.stack.setCurrentWidget(self.current_form)
    
    def edit_employee(self, employee_id):
        """Edit employee"""
        self.current_form = EmployeeForm(self, employee_id=employee_id, on_save_callback=self.on_form_saved)
        
        # Add form to stack and show it
        self.stack.addWidget(self.current_form)
        self.stack.setCurrentWidget(self.current_form)
    
    def view_employee(self, employee_id):
        """View employee details"""
        try:
            employee = self.model.get_employee_by_id(employee_id)
            if employee:
                details = f"""
                ملازم کوڈ: {employee.get('employee_code', '')}
                پورا نام: {employee.get('full_name', '')}
                والد کا نام: {employee.get('father_name', '')}
                شناختی کارڈ: {employee.get('cnic', '')}
                عہدہ: {employee.get('designation', '')}
                تعلیم: {employee.get('qualification', '')}
                شمولیت کی تاریخ: {employee.get('joining_date', '')}
                تنخواہ: {employee.get('salary', 0):,.0f}
                فون: {employee.get('phone_number', '')}
                پتہ: {employee.get('address', '')}
                حالت: {employee.get('status', '')}
                """
                QMessageBox.information(self, "ملازم کی تفصیلات", details.strip())
            else:
                show_error(self, "ملازم نہیں ملا")
        except Exception as e:
            show_error(self, f"ملازم کی تفصیلات دیکھنے میں خطا: {str(e)}")
    
    def delete_employee(self, employee_id):
        """Delete employee with confirmation"""
        reply = QMessageBox.question(
            self, 
            "حذف کی تصدیق", 
            "کیا آپ واقعی اس ملازم کو حذف کرنا چاہتے ہیں؟",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                success = self.model.delete_employee(employee_id)
                if success:
                    show_success(self, "ملازم کامیابی سے حذف ہو گیا")
                    self.load_employees()
                else:
                    show_error(self, "ملازم کو حذف کرنے میں ناکام")
            except Exception as e:
                show_error(self, f"ملازم کو حذف کرنے میں خطا: {str(e)}")
    
    def on_form_saved(self):
        """Called when form is saved"""
        # Remove form from stack and show list view
        if self.current_form:
            self.stack.removeWidget(self.current_form)
            self.current_form.deleteLater()
            self.current_form = None
        
        # Show list view and refresh data
        self.stack.setCurrentWidget(self.list_widget)
        self.load_employees()
    
    def on_search(self):
        """Handle search"""
        self.load_employees()
    
    def on_filter_change(self):
        """Handle filter changes"""
        self.load_employees()
