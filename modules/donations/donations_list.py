from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QLineEdit, QPushButton, QComboBox, QTableWidget,
                             QTableWidgetItem, QDateEdit, QHeaderView, QFrame,
                             QSizePolicy, QAbstractItemView, QShortcut)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QKeySequence

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
        self.setup_shortcuts()
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
        
        # ٹیبل (Initialize early to avoid NoneType errors)
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
        main_layout.addWidget(self.table)
        
        # Footer with total
        footer_layout = QHBoxLayout()
        self.total_label = QLabel("کل رقم: 0 روپے")
        self.total_label.setFont(get_urdu_font(14, bold=True))
        self.total_label.setStyleSheet("color: #28A745;")
        footer_layout.addWidget(self.total_label)
        footer_layout.addStretch()
        
        main_layout.addLayout(footer_layout)

    def setup_shortcuts(self):
        """Setup shortcuts for donation list."""
        self.shortcut_new = QShortcut(QKeySequence("Ctrl+N"), self)
        self.shortcut_new.activated.connect(self.on_add_donation)
        
        self.shortcut_search = QShortcut(QKeySequence("Ctrl+F"), self)
        self.shortcut_search.activated.connect(lambda: self.donor_filter.setFocus())
    
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
        if self.table is None:
            return
            
        clear_table(self.table)
        self.table.setRowCount(len(self.current_donations))
        
        total_amount = 0
        
        for row, donation in enumerate(self.current_donations):
            # Receipt number
            set_table_item_urdu(self.table, row, 0, str(donation['id']))
            
            # Donor name
            set_table_item_urdu(self.table, row, 1, donation['donor_name'])
            
            # Amount
            amount_text = f"{to_urdu_numerals(donation['amount'])} روپے"
            set_table_item_urdu(self.table, row, 2, amount_text)
            total_amount += donation['amount']
            
            # Type
            set_table_item_urdu(self.table, row, 3, donation['donation_type'])
            
            # Payment method
            set_table_item_urdu(self.table, row, 4, donation['payment_method'])
            
            # Date
            date_str = format_date_urdu(donation['donation_date'])
            set_table_item_urdu(self.table, row, 5, date_str)
            
            # Contact
            set_table_item_urdu(self.table, row, 6, donation['donor_contact'] or "")
            
            # Actions
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)
            
            view_btn = QPushButton("دیکھیں")
            view_btn.setFont(get_urdu_font(10))
            view_btn.setStyleSheet("background-color: #17A2B8; color: white; border: none; padding: 3px; border-radius: 3px;")
            view_btn.clicked.connect(lambda checked, did=donation['id']: self.view_donation(did))
            
            edit_btn = QPushButton("ترمیم")
            edit_btn.setFont(get_urdu_font(10))
            edit_btn.setStyleSheet("background-color: #FFC107; color: black; border: none; padding: 3px; border-radius: 3px;")
            edit_btn.clicked.connect(lambda checked, did=donation['id']: self.edit_donation(did))
            
            delete_btn = QPushButton("حذف")
            delete_btn.setFont(get_urdu_font(10))
            delete_btn.setStyleSheet("background-color: #DC3545; color: white; border: none; padding: 3px; border-radius: 3px;")
            delete_btn.clicked.connect(lambda checked, did=donation['id']: self.delete_donation(did))
            
            actions_layout.addWidget(view_btn)
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_widget.setLayout(actions_layout)
            
            self.table.setCellWidget(row, 7, actions_widget)
        
        # Update total
        self.total_label.setText(f"کل رقم: {to_urdu_numerals(total_amount)} روپے")
        self.total_label.setStyleSheet("color: #28A745; font-weight: bold;")
    
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
    
    def apply_filters(self):
        """Apply filters to donations list."""
        try:
            # Get filter values
            donor_filter = self.donor_filter.text().strip()
            type_filter = self.type_filter.currentText()
            method_filter = self.method_filter.currentText()
            from_date = self.from_date.date().toString("yyyy-MM-dd")
            to_date = self.to_date.date().toString("yyyy-MM-dd")
            
            # Build filters dictionary
            filters = {}
            if donor_filter:
                filters['donor_name'] = donor_filter
            if type_filter != "تمام":
                filters['donation_type'] = type_filter
            if method_filter != "تمام":
                filters['payment_method'] = method_filter
            if from_date:
                filters['date_from'] = from_date
            if to_date:
                filters['date_to'] = to_date
            
            # Load filtered donations
            self.current_donations = self.model.get_all_donations(filters)
            self.refresh_table()
            self.update_summary_cards()
            
        except Exception as e:
            show_error(self, f"فلٹرز لگانے میں خرابی: {str(e)}")
    
    def on_add_donation(self):
        """Open DonationForm as dialog."""
        dialog = DonationForm(self)
        if dialog.exec_() == DonationForm.Accepted:
            self.load_donations()
            self.update_summary_cards()
    
    def view_donation(self, donation_id):
        """View donation details."""
        try:
            donation = self.model.get_donation_by_id(donation_id)
            if donation:
                details = f"""
                <b>رسید نمبر:</b> {donation['id']}<br>
                <b>عطیہ دہندہ:</b> {donation['donor_name']}<br>
                <b>رقم:</b> {to_urdu_numerals(donation['amount'])} روپے<br>
                <b>قسم:</b> {donation['donation_type']}<br>
                <b>طریقہ:</b> {donation['payment_method']}<br>
                <b>تاریخ:</b> {format_date_urdu(donation['donation_date'])}<br>
                <b>رابطہ:</b> {donation['donor_contact'] or 'نہیں'}<br>
                <b>نوٹس:</b> {donation['notes'] or 'نہیں'}
                """
                
                msg = QMessageBox(self)
                msg.setWindowTitle("عطیہ تفصیل")
                msg.setTextFormat(Qt.RichText)
                msg.setText(details)
                msg.setStandardButtons(QMessageBox.Ok)
                msg.setFont(get_urdu_font(12))
                msg.exec_()
            else:
                show_error(self, "عطیہ نہیں ملا")
        except Exception as e:
            show_error(self, f"عطیہ دیکھنے میں خرابی: {str(e)}")
    
    def edit_donation(self, donation_id):
        """Edit donation."""
        try:
            donation = self.model.get_donation_by_id(donation_id)
            if donation:
                dialog = DonationForm(self, donation)
                if dialog.exec_() == DonationForm.Accepted:
                    self.load_donations()
                    self.update_summary_cards()
            else:
                show_error(self, "عطیہ نہیں ملا")
        except Exception as e:
            show_error(self, f"عطیہ میں ترمیم کرنے میں خرابی: {str(e)}")
    
    def delete_donation(self, donation_id):
        """Delete donation with confirmation."""
        try:
            if show_confirm(self, "کیا آپ واقعی یہ عطیہ حذف کرنا چاہتے ہیں؟"):
                if self.model.delete_donation(donation_id):
                    self.load_donations()
                    self.update_summary_cards()
                    show_success(self, "عطیہ کامیابی سے حذف کر دیا گیا")
                else:
                    show_error(self, "عطیہ حذف کرنے میں ناکامی")
        except Exception as e:
            show_error(self, f"عطیہ حذف کرنے میں خرابی: {str(e)}")
    
    def on_donation_saved(self, donation_id):
        """Handle donation saved event."""
        self.load_donations()
        self.update_summary_cards()
    
    def closeEvent(self, event):
        """Handle close event."""
        self.model.close_connection()
        super().closeEvent(event)
