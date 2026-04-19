from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget,
                             QTableWidgetItem, QDateEdit, QHeaderView, QFrame,
                             QSizePolicy, QAbstractItemView)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont

from ui.utils import (get_urdu_font, show_error, show_success, to_urdu_numerals,
                     format_date_urdu, clear_table, set_table_item_urdu, show_confirm)
from .donations_model import DonationModel
from .donations_form import DonationForm


class DonationList(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = DonationModel()
        self.current_donations = []
        
        self.setup_ui()
        self.setLayoutDirection(Qt.RightToLeft)
        self.load_donations()
        self.update_summary_cards()
    
    def setup_ui(self):
        """Setup the donations list UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header
        header_label = QLabel("عطیات کی فہرست")
        header_label.setFont(get_urdu_font(20, bold=True))
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("color: #D4A017; margin-bottom: 10px;")
        main_layout.addWidget(header_label)
        
        # Filter bar
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(10)
        
        # Donor filter
        donor_label = QLabel("عطیہ دہندہ:")
        donor_label.setFont(get_urdu_font(12))
        self.donor_filter = QLineEdit()
        self.donor_filter.setFont(get_urdu_font(12))
        self.donor_filter.setPlaceholderText("نام تلاش کریں...")
        self.donor_filter.setFixedWidth(150)
        
        # Type filter
        type_label = QLabel("قسم:")
        type_label.setFont(get_urdu_font(12))
        self.type_filter = QComboBox()
        self.type_filter.setFont(get_urdu_font(12))
        self.type_filter.addItems(["تمام", "عام", "زکوٰۃ", "صدقہ", "فترہ", "تعمیر", "دیگر"])
        self.type_filter.setFixedWidth(120)
        
        # Method filter
        method_label = QLabel("طریقہ:")
        method_label.setFont(get_urdu_font(12))
        self.method_filter = QComboBox()
        self.method_filter.setFont(get_urdu_font(12))
        self.method_filter.addItems(["تمام", "نقد", "بینک ٹرانزفر", "چیک"])
        self.method_filter.setFixedWidth(120)
        
        # Date filters
        from_label = QLabel("تاریخ سے:")
        from_label.setFont(get_urdu_font(12))
        self.from_date = QDateEdit()
        self.from_date.setFont(get_urdu_font(12))
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        self.from_date.setCalendarPopup(True)
        self.from_date.setFixedWidth(120)
        
        to_label = QLabel("تاریخ تک:")
        to_label.setFont(get_urdu_font(12))
        self.to_date = QDateEdit()
        self.to_date.setFont(get_urdu_font(12))
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setCalendarPopup(True)
        self.to_date.setFixedWidth(120)
        
        # Search button
        search_button = QPushButton("تلاش کریں")
        search_button.setFont(get_urdu_font(12))
        search_button.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        search_button.clicked.connect(self.apply_filters)
        
        # New donation button
        new_button = QPushButton("نیا عطیہ")
        new_button.setFont(get_urdu_font(12))
        new_button.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        new_button.clicked.connect(self.on_add_donation)
        
        # Add widgets to filter layout
        filter_layout.addWidget(donor_label)
        filter_layout.addWidget(self.donor_filter)
        filter_layout.addWidget(type_label)
        filter_layout.addWidget(self.type_filter)
        filter_layout.addWidget(method_label)
        filter_layout.addWidget(self.method_filter)
        filter_layout.addWidget(from_label)
        filter_layout.addWidget(self.from_date)
        filter_layout.addWidget(to_label)
        filter_layout.addWidget(self.to_date)
        filter_layout.addWidget(search_button)
        filter_layout.addWidget(new_button)
        filter_layout.addStretch()
        
        main_layout.addLayout(filter_layout)
        
        # Summary cards
        cards_layout = QGridLayout()
        cards_layout.setSpacing(10)
        
        # Total donations card
        self.total_count_card = self.create_summary_card("کل عطیات", "0", "#007BFF")
        cards_layout.addWidget(self.total_count_card, 0, 0)
        
        # Total amount card
        self.total_amount_card = self.create_summary_card("کل رقم", "0", "#28A745")
        cards_layout.addWidget(self.total_amount_card, 0, 1)
        
        # Today's donations card
        self.today_card = self.create_summary_card("آج کے عطیات", "0", "#17A2B8")
        cards_layout.addWidget(self.today_card, 0, 2)
        
        # This month card
        self.month_card = self.create_summary_card("اس ماہ", "0", "#FFC107")
        cards_layout.addWidget(self.month_card, 0, 3)
        
        main_layout.addLayout(cards_layout)
        
        # ٹیبل
        self.table = QTableWidget()
        self.table.setFont(get_urdu_font(12))
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels(["رسید نمبر", "عطیہ دہندہ", "رقم", "قسم", "طریقہ", "تاریخ", "رابطہ", "عمل"])
        
        # Configure table
        header = self.table.horizontalHeader()
        header.setFont(get_urdu_font(12, bold=True))
        header.setSectionResizeMode(1, QHeaderView.Stretch)  # Donor name stretches
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Amount
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Type
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # Method
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(6, QHeaderView.ResizeToContents)  # Contact
        header.setSectionResizeMode(7, QHeaderView.ResizeToContents)  # Actions
        
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        
        main_layout.addWidget(self.table)
        
        # Footer with total
        footer_layout = QHBoxLayout()
        self.total_label = QLabel("کل رقم: 0 روپے")
        self.total_label.setFont(get_urdu_font(14, bold=True))
        self.total_label.setStyleSheet("color: #28A745;")
        footer_layout.addWidget(self.total_label)
        footer_layout.addStretch()
        
        main_layout.addLayout(footer_layout)
    
    def create_summary_card(self, title, value, color):
        """Create a summary card widget."""
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 2px solid {color};
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel(title)
        title_label.setFont(get_urdu_font(12))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {color};")
        
        value_label = QLabel(value)
        value_label.setFont(get_urdu_font(16, bold=True))
        value_label.setAlignment(Qt.AlignCenter)
        value_label.setStyleSheet(f"color: {color};")
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return card
    
    def load_donations(self):
        """Load donations from model."""
        try:
            self.current_donations = self.model.get_all_donations()
            self.refresh_table()
        except Exception as e:
            show_error(self, f"عطیات لوڈ کرنے میں خرابی: {str(e)}")
    
    def refresh_table(self):
        """Refresh table with current donations."""
        clear_table(self.table)
        self.table.setRowCount(len(self.current_donations))
        
        total_amount = 0
        
        for row, donation in enumerate(self.current_donations):
            # Receipt number
            set_table_item_urdu(self.table, row, 0, donation['receipt_number'] or '')
            
            # Donor name
            set_table_item_urdu(self.table, row, 1, donation['donor_name'] or '')
            
            # Amount
            amount = donation['amount'] or 0
            set_table_item_urdu(self.table, row, 2, f"{amount:.2f}")
            total_amount += amount
            
            # Type
            set_table_item_urdu(self.table, row, 3, donation['donation_type'] or '')
            
            # Method
            set_table_item_urdu(self.table, row, 4, donation['payment_method'] or '')
            
            # Date
            date_str = donation['donation_date'] or ''
            if date_str:
                formatted_date = format_date_urdu(date_str)
                set_table_item_urdu(self.table, row, 5, formatted_date)
            else:
                set_table_item_urdu(self.table, row, 5, '')
            
            # Contact
            set_table_item_urdu(self.table, row, 6, donation['donor_contact'] or '')
            
            # Actions
            actions_widget = self.create_actions_widget(donation['id'])
            self.table.setCellWidget(row, 7, actions_widget)
        
        # Update total
        self.total_label.setText(f"کل رقم: {to_urdu_numerals(f'{total_amount:.2f}')} روپے")
    
    def create_actions_widget(self, donation_id):
        """Create actions widget for edit/delete buttons."""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(5)
        
        # Edit button
        edit_button = QPushButton("ترمیم")
        edit_button.setFont(get_urdu_font(10))
        edit_button.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        edit_button.clicked.connect(lambda: self.on_edit_donation(donation_id))
        
        # Delete button
        delete_button = QPushButton("حذف")
        delete_button.setFont(get_urdu_font(10))
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #DC3545;
                color: white;
                border: none;
                padding: 4px 8px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        delete_button.clicked.connect(lambda: self.on_delete_donation(donation_id))
        
        layout.addWidget(edit_button)
        layout.addWidget(delete_button)
        
        return widget
    
    def apply_filters(self):
        """Apply filters to donations list."""
        try:
            filters = {}
            
            # Donor name filter
            donor_name = self.donor_filter.text().strip()
            if donor_name:
                filters['donor_name'] = donor_name
            
            # Type filter
            donation_type = self.type_filter.currentText()
            if donation_type != "All":
                filters['donation_type'] = donation_type
            
            # Method filter
            payment_method = self.method_filter.currentText()
            if payment_method != "All":
                filters['payment_method'] = payment_method
            
            # Date range filter
            start_date = self.from_date.date().toString("yyyy-MM-dd")
            end_date = self.to_date.date().toString("yyyy-MM-dd")
            filters['date_range'] = (start_date, end_date)
            
            self.current_donations = self.model.get_all_donations(filters)
            self.refresh_table()
            self.update_summary_cards()
            
        except Exception as e:
            show_error(self, f"فلٹر لگانے میں خرابی: {str(e)}")
    
    def on_add_donation(self):
        """Open donation form for new donation."""
        try:
            form = DonationForm(parent=self)
            form.donation_saved.connect(self.on_donation_saved)
            form.exec_()
        except Exception as e:
            show_error(self, f"عطیہ فارم کھولنے میں خرابی: {str(e)}")
    
    def on_edit_donation(self, donation_id):
        """Open donation form for editing."""
        try:
            form = DonationForm(donation_id=donation_id, parent=self)
            form.donation_saved.connect(self.on_donation_saved)
            form.exec_()
        except Exception as e:
            show_error(self, f"عطیہ فارم کھولنے میں خرابی: {str(e)}")
    
    def on_delete_donation(self, donation_id):
        """Delete donation after confirmation."""
        try:
            if show_confirm(self, "کیا آپ واقعی اس عطیے کو حذف کرنا چاہتے ہیں؟"):
                success = self.model.delete_donation(donation_id)
                if success:
                    show_success(self, "عطیہ کامیابی سے حذف ہوگیا")
                    self.load_donations()
                    self.update_summary_cards()
                else:
                    show_error(self, "عطیہ حذف کرنے میں ناکام")
        except Exception as e:
            show_error(self, f"عطیہ حذف کرنے میں خرابی: {str(e)}")
    
    def on_donation_saved(self, donation_id):
        """Handle donation saved event."""
        self.load_donations()
        self.update_summary_cards()
    
    def update_summary_cards(self):
        """Update summary cards with current statistics."""
        try:
            stats = self.model.get_summary_statistics()
            
            # Update total count
            count_label = self.total_count_card.findChild(QLabel)
            if count_label:
                count_label.setText(to_urdu_numerals(stats['total_count']))
            
            # Update total amount
            amount_label = self.total_amount_card.findChild(QLabel)
            if amount_label:
                amount_label.setText(f"{to_urdu_numerals(stats['total_amount'])} روپے")
            
            # Update today's donations
            today_label = self.today_card.findChild(QLabel)
            if today_label:
                today_text = f"{to_urdu_numerals(stats['today_count'])} عطیات\n{to_urdu_numerals(stats['today_amount'])} روپے"
                today_label.setText(today_text)
            
            # Update this month
            month_label = self.month_card.findChild(QLabel)
            if month_label:
                month_text = f"{to_urdu_numerals(stats['month_count'])} عطیات\n{to_urdu_numerals(stats['month_amount'])} روپے"
                month_label.setText(month_text)
                
        except Exception as e:
            print(f"Error updating summary cards: {e}")
    
    def closeEvent(self, event):
        """Handle close event."""
        self.model.close_connection()
        super().closeEvent(event)
