from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QComboBox, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QFrame, 
                             QAbstractItemView, QMessageBox)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from ui.utils import get_urdu_font, show_error, show_success, show_confirm, to_urdu_numerals, clear_table, set_table_item_urdu, URDU_MONTHS, get_today_date
from ui.styles import COLOR_ACCENT
from .fee_model import FeeModel
from .fee_form import FeeForm

class FeeList(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = FeeModel()
        self.fee_form = None
        self.setup_ui()
        self.load_fees()
    
    def setup_ui(self):
        """Setup the fee list UI."""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Heading
        heading = QLabel("Fee History")
        heading.setFont(get_urdu_font(18, bold=True))
        heading.setAlignment(Qt.AlignCenter)
        heading.setStyleSheet(f"color: {COLOR_ACCENT}; margin-bottom: 10px;")
        main_layout.addWidget(heading)
        
        # Top bar with controls
        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)
        
        # New fee button
        self.new_fee_button = QPushButton("+ New Fee")
        self.new_fee_button.setFont(get_urdu_font(12, bold=True))
        self.new_fee_button.setFixedHeight(40)
        self.new_fee_button.setStyleSheet(f"""
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
        self.new_fee_button.clicked.connect(self.open_fee_form)
        top_bar.addWidget(self.new_fee_button)
        
        # Month filter
        self.month_filter = QComboBox()
        self.month_filter.setFont(get_urdu_font(12))
        self.month_filter.setMinimumHeight(40)
        self.month_filter.addItem("All Months", None)
        self.month_filter.addItems(URDU_MONTHS)
        self.month_filter.currentTextChanged.connect(self.load_fees)
        top_bar.addWidget(self.month_filter)
        
        # Year filter
        self.year_filter = QComboBox()
        self.year_filter.setFont(get_urdu_font(12))
        self.year_filter.setMinimumHeight(40)
        self.year_filter.addItem("All Years", None)
        current_year = int(get_today_date().split('-')[0])
        for year in range(current_year, current_year - 5, -1):
            self.year_filter.addItem(str(year), str(year))
        self.year_filter.currentTextChanged.connect(self.load_fees)
        top_bar.addWidget(self.year_filter)
        
        # Refresh button
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setFont(get_urdu_font(12))
        self.refresh_button.setFixedHeight(40)
        self.refresh_button.setStyleSheet("""
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
        self.refresh_button.clicked.connect(self.load_fees)
        top_bar.addWidget(self.refresh_button)
        
        top_bar.addStretch()
        main_layout.addLayout(top_bar)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "S.No", "Student", "Month", "Year", "Amount", "Receipt No.", "Actions"
        ])
        
        # Table styling
        self.table.setFont(get_urdu_font(12))
        self.table.horizontalHeader().setFont(get_urdu_font(12, bold=True))
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)  # S.No
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Amount
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Receipt
        self.table.horizontalHeader().setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Actions
        
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        # Set row height
        self.table.verticalHeader().setDefaultSectionSize(40)
        self.table.verticalHeader().setVisible(False)
        
        main_layout.addWidget(self.table)
        
        # Total bar
        self.total_frame = QFrame()
        self.total_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        total_layout = QHBoxLayout(self.total_frame)
        total_layout.setContentsMargins(15, 10, 15, 10)
        
        total_label = QLabel("Total Collection:")
        total_label.setFont(get_urdu_font(14, bold=True))
        total_label.setStyleSheet("color: #495057;")
        total_layout.addWidget(total_label)
        
        self.total_amount_label = QLabel("0 Rs")
        self.total_amount_label.setFont(get_urdu_font(14, bold=True))
        self.total_amount_label.setStyleSheet(f"color: {COLOR_ACCENT};")
        total_layout.addWidget(self.total_amount_label)
        
        total_layout.addStretch()
        main_layout.addWidget(self.total_frame)
    
    def load_fees(self):
        """Load fees into the table."""
        # Clear table
        clear_table(self.table)
        
        # Get filter values
        month = self.month_filter.currentData()
        year = self.year_filter.currentData()
        
        # Get fees data
        fees = self.model.get_all_fees(month, year)
        
        # Set row count
        self.table.setRowCount(len(fees))
        
        # Populate table
        total_amount = 0
        for row, fee in enumerate(fees):
            # S.No
            set_table_item_urdu(self.table, row, 0, row + 1)
            
            # Student name
            set_table_item_urdu(self.table, row, 1, fee['student_name'])
            
            # Month
            set_table_item_urdu(self.table, row, 2, fee['month'])
            
            # Year
            set_table_item_urdu(self.table, row, 3, fee['year'])
            
            # Amount
            amount = fee['amount']
            set_table_item_urdu(self.table, row, 4, amount)
            total_amount += amount
            
            # Receipt number
            set_table_item_urdu(self.table, row, 5, fee['receipt_number'])
            
            # Actions (Delete button)
            delete_button = QPushButton("Delete")
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
            delete_button.clicked.connect(lambda checked, fee_id=fee['id']: self.delete_fee(fee_id))
            
            self.table.setCellWidget(row, 6, delete_button)
        
        # Update total
        self.total_amount_label.setText(f"{to_urdu_numerals(total_amount)} Rs")
    
    def open_fee_form(self):
        """Open fee form dialog."""
        if self.fee_form is None:
            self.fee_form = FeeForm(self)
            self.fee_form.set_save_callback(self.on_fee_saved)
        
        self.fee_form.reset_form()
        self.fee_form.show()
    
    def on_fee_saved(self):
        """Handle fee saved event."""
        self.load_fees()
        if self.fee_form:
            self.fee_form.close()
    
    def delete_fee(self, fee_id):
        """Delete a fee record."""
        if show_confirm(self, "Are you sure you want to delete this fee record?"):
            try:
                self.model.delete_fee(fee_id)
                show_success(self, "Fee record deleted successfully")
                self.load_fees()
            except ValueError as e:
                show_error(self, str(e))
            except Exception as e:
                show_error(self, f"Error deleting fee: {str(e)}")
    
    def refresh(self):
        """Refresh the fee list."""
        self.load_fees()
