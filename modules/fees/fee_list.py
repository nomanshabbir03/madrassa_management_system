from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QFrame, 
                             QAbstractItemView, QMessageBox, QDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui.utils import (get_urdu_font, show_error, show_success, 
                      show_confirm, to_urdu_numerals, clear_table, 
                      set_table_item_urdu, get_today_date)
from ui.styles import COLOR_ACCENT
from .fee_model import FeeModel
from .fee_form import FeeForm

# Urdu month names mapping
URDU_MONTHS = {
    1: 'جنوری', 2: 'فروری', 3: 'مارچ', 4: 'اپریل',
    5: 'مئی', 6: 'جون', 7: 'جولائی', 8: 'اگست',
    9: 'ستمبر', 10: 'اکتوبر', 11: 'نومبر', 12: 'دسمبر'
}

class FeeList(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = FeeModel()
        self.fee_form_dialog = None
        self.setup_ui()
        self.load_fees()
    
    def setup_ui(self):
        """Setup the fee list UI with RTL layout."""
        # Vertical layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header: "فیس کی فہرست" with gold accent
        header = QLabel("فیس کی فہرست")
        header.setFont(get_urdu_font(18, bold=True))
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(f"color: {COLOR_ACCENT}; margin-bottom: 15px;")
        header.setLayoutDirection(Qt.RightToLeft)
        main_layout.addWidget(header)
        
        # Filter bar (horizontal)
        filter_bar = QHBoxLayout()
        filter_bar.setSpacing(10)
                
        # Student filter
        student_label = QLabel("طالب علم")
        student_label.setFont(get_urdu_font(12))
        student_label.setLayoutDirection(Qt.RightToLeft)
        filter_bar.addWidget(student_label)
        
        self.student_filter = QComboBox()
        self.student_filter.setFont(get_urdu_font(12))
        self.student_filter.setMinimumHeight(35)
        self.student_filter.setLayoutDirection(Qt.RightToLeft)
        self.student_filter.addItem("تمام", None)
        self.load_students_filter()
        filter_bar.addWidget(self.student_filter)
        
        # Year filter
        year_label = QLabel("سال")
        year_label.setFont(get_urdu_font(12))
        year_label.setLayoutDirection(Qt.RightToLeft)
        filter_bar.addWidget(year_label)
        
        self.year_filter = QComboBox()
        self.year_filter.setFont(get_urdu_font(12))
        self.year_filter.setMinimumHeight(35)
        self.year_filter.setLayoutDirection(Qt.RightToLeft)
        self.year_filter.addItem("تمام", None)
        current_year = int(get_today_date().split('-')[0])
        for year in range(current_year, current_year - 10, -1):
            self.year_filter.addItem(str(year), year)
        filter_bar.addWidget(self.year_filter)
        
        # Month filter
        month_label = QLabel("ماہ")
        month_label.setFont(get_urdu_font(12))
        month_label.setLayoutDirection(Qt.RightToLeft)
        filter_bar.addWidget(month_label)
        
        self.month_filter = QComboBox()
        self.month_filter.setFont(get_urdu_font(12))
        self.month_filter.setMinimumHeight(35)
        self.month_filter.setLayoutDirection(Qt.RightToLeft)
        self.month_filter.addItem("تمام", None)
        for month_num in range(1, 13):
            self.month_filter.addItem(URDU_MONTHS[month_num], month_num)
        filter_bar.addWidget(self.month_filter)
        
        # Search button
        self.search_button = QPushButton("تلاش کریں")
        self.search_button.setFont(get_urdu_font(12))
        self.search_button.setFixedHeight(35)
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.search_button.clicked.connect(self.load_fees)
        filter_bar.addWidget(self.search_button)
        
        # New Entry button
        self.new_entry_button = QPushButton("نیا اندراج")
        self.new_entry_button.setFont(get_urdu_font(12, bold=True))
        self.new_entry_button.setFixedHeight(35)
        self.new_entry_button.setStyleSheet(f"""
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
        self.new_entry_button.clicked.connect(self.on_add_fee)
        filter_bar.addWidget(self.new_entry_button)
        
        filter_bar.addStretch()
        main_layout.addLayout(filter_bar)
        
        # QTableWidget with columns (right to left display)
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "اعمال", "ادائیگی کی تاریخ", "ادائیگی کا طریقہ", "رقم", 
            "سال", "ماہ", "طالب علم کا نام", "رسید نمبر"
        ])
        
        # Table styling
        self.table.setFont(get_urdu_font(12))
        self.table.horizontalHeader().setFont(get_urdu_font(12, bold=True))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Actions
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Date
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Amount
        self.table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Receipt
        
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Set row height
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.verticalHeader().setVisible(False)
        
        # RTL layout for table
        self.table.setLayoutDirection(Qt.RightToLeft)
        
        main_layout.addWidget(self.table)
        
        # Summary footer
        self.summary_frame = QFrame()
        self.summary_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        self.summary_frame.setLayoutDirection(Qt.RightToLeft)
        
        summary_layout = QHBoxLayout(self.summary_frame)
        summary_layout.setContentsMargins(15, 10, 15, 10)
                
        summary_label = QLabel("کل وصول شدہ")
        summary_label.setFont(get_urdu_font(14, bold=True))
        summary_label.setStyleSheet("color: #28a745;")
        summary_layout.addWidget(summary_label)
        
        self.total_label = QLabel("0 روپے")
        self.total_label.setFont(get_urdu_font(14, bold=True))
        self.total_label.setStyleSheet("color: #28a745;")
        summary_layout.addWidget(self.total_label)
        
        summary_layout.addStretch()
        main_layout.addWidget(self.summary_frame)
        
        # Set widget properties
        self.setLayoutDirection(Qt.RightToLeft)
        self.setFont(get_urdu_font(14))
    
    def load_students_filter(self):
        """Load students into filter dropdown."""
        try:
            # Import here to avoid circular imports
            from modules.students.student_model import StudentModel
            student_model = StudentModel()
            students = student_model.get_all_students()
            
            for student in students:
                display_text = f"{student['full_name']} - {student['registration_number']}"
                self.student_filter.addItem(display_text, student['id'])
                
        except Exception as e:
            print(f"Error loading students filter: {e}")
    
    def load_fees(self):
        """Load fees from model, apply filters."""
        # Build filters
        filters = {}
        
        student_id = self.student_filter.currentData()
        if student_id:
            filters['student_id'] = student_id
        
        year = self.year_filter.currentData()
        if year:
            filters['year'] = year
        
        month = self.month_filter.currentData()
        if month:
            filters['month'] = month
        
        # Get fees data
        fees = self.model.get_all_fees(filters)
        
        # Refresh table
        self.refresh_table(fees)
        
        # Update total
        total = self.calculate_total(fees)
        self.total_label.setText(f"{to_urdu_numerals(total)} Rs")
    
    def refresh_table(self, fees):
        """Populate table with data, convert month numbers to Urdu names."""
        # Clear table
        clear_table(self.table)
        
        # Set row count
        self.table.setRowCount(len(fees))
        
        # Populate table
        for row, fee in enumerate(fees):
            # Receipt # (column 7)
            set_table_item_urdu(self.table, row, 7, fee['receipt_number'])
            
            # Student Name (column 6)
            set_table_item_urdu(self.table, row, 6, fee['student_name'])
            
            # Month - show Urdu name (column 5)
            month_name = URDU_MONTHS.get(fee['month'], str(fee['month']))
            set_table_item_urdu(self.table, row, 5, month_name)
            
            # Year (column 4)
            set_table_item_urdu(self.table, row, 4, fee['year'])
            
            # Amount - format with Urdu numerals (column 3)
            set_table_item_urdu(self.table, row, 3, fee['amount'])
            
            # Payment Method (column 2)
            set_table_item_urdu(self.table, row, 2, fee['payment_method'])
            
            # Payment Date (column 1)
            set_table_item_urdu(self.table, row, 1, fee['paid_date'])
            
            # Actions - Edit/Delete buttons (column 0)
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(2, 2, 2, 2)
            actions_layout.setSpacing(5)
                        
            # Edit button
            edit_button = QPushButton("ترمیم")
            edit_button.setFont(get_urdu_font(10))
            edit_button.setFixedHeight(30)
            edit_button.setStyleSheet("""
                QPushButton {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 4px 8px;
                }
                QPushButton:hover {
                    background-color: #0056b3;
                }
            """)
            edit_button.clicked.connect(lambda checked, fee_id=fee['id']: self.on_edit_fee(fee_id))
            actions_layout.addWidget(edit_button)
            
            # Delete button
            delete_button = QPushButton("حذف کریں")
            delete_button.setFont(get_urdu_font(10))
            delete_button.setFixedHeight(30)
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #dc3545;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 4px 8px;
                }
                QPushButton:hover {
                    background-color: #c82333;
                }
            """)
            delete_button.clicked.connect(lambda checked, fee_id=fee['id']: self.on_delete_fee(fee_id))
            actions_layout.addWidget(delete_button)
            
            self.table.setCellWidget(row, 0, actions_widget)
    
    def on_add_fee(self):
        """Open FeeForm as dialog, refresh on save."""
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("فیس شامل کریں")
        dialog.setFixedSize(500, 600)
        dialog.setLayoutDirection(Qt.RightToLeft)
        
        # Create form
        form = FeeForm(dialog)
        form.fee_saved.connect(lambda fee_id: self.on_fee_saved(dialog, fee_id))
        form.cancelled.connect(dialog.reject)
        
        # Set form as dialog's main widget
        layout = QVBoxLayout(dialog)
        layout.addWidget(form)
        
        # Show dialog
        dialog.exec_()
    
    def on_fee_saved(self, dialog, fee_id):
        """Handle fee saved event."""
        dialog.accept()
        self.load_fees()
        show_success(self, "فیس کامیابی سے محفوظ ہو گئی!")
    
    def on_edit_fee(self, fee_id):
        """Open FeeForm with data pre-filled."""
        # Get fee data
        fees = self.model.get_all_fees({'student_id': None})  # Get all fees
        fee_data = None
        for fee in fees:
            if fee['id'] == fee_id:
                fee_data = fee
                break
        
        if not fee_data:
            show_error(self, "فیس ریکارڈ نہیں ملا")
            return
        
        # Create dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("فیس میں ترمیم کریں")
        dialog.setFixedSize(500, 600)
        dialog.setLayoutDirection(Qt.RightToLeft)
        
        # Create form and pre-fill data
        form = FeeForm(dialog)
        # TODO: Implement pre-filling logic in FeeForm
        
        # Set form as dialog's main widget
        layout = QVBoxLayout(dialog)
        layout.addWidget(form)
        
        # Show dialog
        dialog.exec_()
    
    def on_delete_fee(self, fee_id):
        """Confirm dialog then delete."""
        if show_confirm(self, "کیا آپ واقعی حذف کرنا چاہتے ہیں?"):
            try:
                self.model.delete_fee(fee_id)
                show_success(self, "فیس کامیابی سے حذف ہو گئی")
                self.load_fees()
            except Exception as e:
                show_error(self, f"فیس حذف کرنے میں خرابی: {str(e)}")
    
    def calculate_total(self, fees):
        """Sum of visible fees, convert to Urdu numerals."""
        total = sum(fee['amount'] for fee in fees)
        return total
