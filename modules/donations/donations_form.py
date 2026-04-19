from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QLabel, QLineEdit, QTextEdit, QPushButton, QComboBox,
                             QCompleter, QShortcut)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QIntValidator, QDoubleValidator, QKeySequence

from ui.utils import (get_urdu_font, show_error, show_success, to_urdu_numerals, 
                     validate_required, validate_phone, set_field_error)
from .donations_model import DonationModel


class DonationForm(QWidget):
    donation_saved = pyqtSignal(int)  # Pass donation_id when saved
    cancelled = pyqtSignal()
    
    def __init__(self, donation_id=None, parent=None):
        super().__init__(parent)
        self.donation_id = donation_id
        self.model = DonationModel()
        self.is_edit_mode = donation_id is not None
        
        self.setup_ui()
        self.setup_shortcuts()
        self.setLayoutDirection(Qt.RightToLeft)
        
        if self.is_edit_mode:
            self.load_donation_data()
    
    def setup_ui(self):
        """Setup the donation form UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Title
        title_label = QLabel("عطیہ رجسٹریشن" if self.is_edit_mode else "عطیہ رجسٹریشن")
        title_label.setFont(get_urdu_font(18, bold=True))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #D4A017; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # فارم لی آؤٹ
        form_layout = QGridLayout()
        form_layout.setSpacing(10)
        
        # عطیہ دہندہ کا نام
        self.donor_name_label = QLabel("عطیہ دہندہ کا نام:")
        self.donor_name_label.setFont(get_urdu_font(14))
        self.donor_name_input = QLineEdit()
        self.donor_name_input.setFont(get_urdu_font(14))
        self.donor_name_input.setPlaceholderText("عطیہ دہندہ کا نام درج کریں...")
        self.donor_name_input.textChanged.connect(self.load_donor_suggestions)
        form_layout.addWidget(self.donor_name_label, 0, 0)
        form_layout.addWidget(self.donor_name_input, 0, 1)
        
        # رابطہ نمبر
        self.contact_label = QLabel("رابطہ نمبر:")
        self.contact_label.setFont(get_urdu_font(14))
        self.contact_input = QLineEdit()
        self.contact_input.setFont(get_urdu_font(14))
        self.contact_input.setPlaceholderText("03XX-XXXXXXX")
        form_layout.addWidget(self.contact_label, 1, 0)
        form_layout.addWidget(self.contact_input, 1, 1)
        
        # رقم
        self.amount_label = QLabel("رقم:")
        self.amount_label.setFont(get_urdu_font(14))
        self.amount_input = QLineEdit()
        self.amount_input.setFont(get_urdu_font(14))
        self.amount_input.setPlaceholderText("رقم درج کریں...")
        self.amount_input.setValidator(QDoubleValidator(0, 999999.99, 2))
        form_layout.addWidget(self.amount_label, 2, 0)
        form_layout.addWidget(self.amount_input, 2, 1)
        
        # عطیہ کی قسم
        self.donation_type_label = QLabel("عطیے کی قسم:")
        self.donation_type_label.setFont(get_urdu_font(14))
        self.donation_type_combo = QComboBox()
        self.donation_type_combo.setFont(get_urdu_font(14))
        self.donation_type_combo.addItems(['عام', 'زکوٰۃ', 'صدقہ', 'فترہ', 'تعمیر', 'دیگر'])
        form_layout.addWidget(self.donation_type_label, 3, 0)
        form_layout.addWidget(self.donation_type_combo, 3, 1)
        
        # ادائیگی کا طریقہ
        self.payment_method_label = QLabel("ادائیگی کا طریقہ:")
        self.payment_method_label.setFont(get_urdu_font(14))
        self.payment_method_combo = QComboBox()
        self.payment_method_combo.setFont(get_urdu_font(14))
        self.payment_method_combo.addItems(['نقد', 'بینک ٹرانزفر', 'چیک'])
        form_layout.addWidget(self.payment_method_label, 4, 0)
        form_layout.addWidget(self.payment_method_combo, 4, 1)
        
        # رسید نمبر
        self.receipt_label = QLabel("رسید نمبر:")
        self.receipt_label.setFont(get_urdu_font(14))
        self.receipt_input = QLineEdit()
        self.receipt_input.setFont(get_urdu_font(14))
        self.receipt_input.setReadOnly(True)
        self.receipt_input.setStyleSheet("background-color: #f0f0f0;")
        if not self.is_edit_mode:
            self.receipt_input.setText(self.generate_receipt_number())
        form_layout.addWidget(self.receipt_label, 5, 0)
        form_layout.addWidget(self.receipt_input, 5, 1)
        
        # نوٹس
        self.notes_label = QLabel("نوٹس:")
        self.notes_label.setFont(get_urdu_font(14))
        self.notes_input = QTextEdit()
        self.notes_input.setFont(get_urdu_font(14))
        self.notes_input.setPlaceholderText("اضافی نوٹس...")
        self.notes_input.setMaximumHeight(80)
        form_layout.addWidget(self.notes_label, 6, 0)
        form_layout.addWidget(self.notes_input, 6, 1)
        
        main_layout.addLayout(form_layout)
        
        # بٹن
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.save_button = QPushButton("محفوظ کریں")
        self.save_button.setFont(get_urdu_font(14))
        self.save_button.setStyleSheet("""
            QPushButton {
                background-color: #28A745;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        self.save_button.clicked.connect(self.save_donation)
        
        self.new_button = QPushButton("نیا عطیہ")
        self.new_button.setFont(get_urdu_font(14))
        self.new_button.setStyleSheet("""
            QPushButton {
                background-color: #007BFF;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        self.new_button.clicked.connect(self.clear_form)
        
        self.close_button = QPushButton("بند کریں")
        self.close_button.setFont(get_urdu_font(14))
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #6C757D;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #545b62;
            }
        """)
        self.close_button.clicked.connect(self.close_form)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.new_button)
        button_layout.addWidget(self.close_button)
        
        main_layout.addLayout(button_layout)
        main_layout.addStretch()
        
        # سیٹ اپ کمپلیٹر برائے عطیہ دہندہ کا نام
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.activated.connect(self.auto_fill_contact)
        self.donor_name_input.setCompleter(self.completer)

    def setup_shortcuts(self):
        """Setup shortcuts for the form."""
        self.shortcut_save = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut_save.activated.connect(self.save_donation)
        
        self.shortcut_cancel = QShortcut(QKeySequence("Esc"), self)
        self.shortcut_cancel.activated.connect(self.close_form)
    
    def validate_form(self):
        """Validate form fields."""
        # Reset errors
        set_field_error(self.donor_name_input, False)
        set_field_error(self.amount_input, False)
        set_field_error(self.contact_input, False)
        
        errors = []
        
        # Donor name
        if not validate_required(self.donor_name_input.text()):
            set_field_error(self.donor_name_input, True)
            errors.append("عطیہ دہندہ کا نام ضروری ہے")
        
        # Amount
        amount_text = self.amount_input.text().strip()
        if not validate_required(amount_text):
            set_field_error(self.amount_input, True)
            errors.append("رقم ضروری ہے")
        else:
            try:
                amount = float(amount_text)
                if amount <= 0:
                    set_field_error(self.amount_input, True)
                    errors.append("رقم صفر سے زیادہ ہونی چاہیے")
            except ValueError:
                set_field_error(self.amount_input, True)
                errors.append("غلط رقم کی شکل")
        
        # Contact (optional)
        contact_text = self.contact_input.text().strip()
        if contact_text and not validate_phone(contact_text):
            set_field_error(self.contact_input, True)
            errors.append("غلط رابطہ نمبر کی شکل - 03XX-XXXXXXX فارمیٹ درکار ہے")
        
        if errors:
            show_error(self, "\n".join(errors))
            return False
        
        return True
    
    def save_donation(self):
        """عطیہ ڈیٹا محفوظ کریں"""
        if not self.validate_form():
            return
        
        try:
            donor_name = self.donor_name_input.text().strip()
            donor_contact = self.contact_input.text().strip()
            amount = float(self.amount_input.text().strip())
            donation_type = self.donation_type_combo.currentText()
            payment_method = self.payment_method_combo.currentText()
            notes = self.notes_input.toPlainText().strip()
            
            if self.is_edit_mode:
                # Update existing donation
                success = self.model.update_donation(
                    self.donation_id,
                    donor_name=donor_name,
                    donor_contact=donor_contact,
                    amount=amount,
                    donation_type=donation_type,
                    payment_method=payment_method,
                    notes=notes
                )
                
                if success:
                    show_success(self, "عطیہ کامیابی سے اپ ڈیٹ ہوگیا")
                    self.donation_saved.emit(self.donation_id)
                else:
                    show_error(self, "عطیہ اپ ڈیٹ کرنے میں ناکام")
            else:
                # Add new donation
                donation_id, receipt_number = self.model.add_donation(
                    donor_name, amount, donation_type, payment_method,
                    donor_contact, notes
                )
                
                if donation_id:
                    show_success(self, f"عطیہ کامیابی سے محفوظ ہوگیا\nرسید نمبر: {receipt_number}")
                    self.donation_saved.emit(donation_id)
                    self.clear_form()
                else:
                    show_error(self, "عطیہ محفوظ کرنے میں ناکام")
        
        except Exception as e:
            show_error(self, f"عطیہ محفوظ کرنے میں خرابی: {str(e)}")
    
    def clear_form(self):
        """Clear form fields."""
        self.donor_name_input.clear()
        self.contact_input.clear()
        self.amount_input.clear()
        self.donation_type_combo.setCurrentIndex(0)
        self.payment_method_combo.setCurrentIndex(0)
        self.notes_input.clear()
        
        if not self.is_edit_mode:
            self.receipt_input.setText(self.generate_receipt_number())
        
        self.donor_name_input.setFocus()
    
    def close_form(self):
        """Close the form."""
        self.cancelled.emit()
        self.close()
    
    def load_donor_suggestions(self):
        """Load donor suggestions for autocomplete."""
        text = self.donor_name_input.text().strip()
        if len(text) < 2:
            return
        
        try:
            donors = self.model.search_donors(text)
            donor_names = [donor['donor_name'] for donor in donors]
            
            if donor_names:
                from PyQt5.QtCore import QStringListModel
                model = QStringListModel(donor_names)
                self.completer.setModel(model)
        except Exception as e:
            print(f"Error loading donor suggestions: {e}")
    
    def auto_fill_contact(self, donor_name):
        """Auto-fill contact number when donor is selected."""
        try:
            donors = self.model.search_donors(donor_name)
            for donor in donors:
                if donor['donor_name'] == donor_name and donor['donor_contact']:
                    self.contact_input.setText(donor['donor_contact'])
                    break
        except Exception as e:
            print(f"Error auto-filling contact: {e}")
    
    def generate_receipt_number(self):
        """Generate receipt number."""
        return self.model.generate_receipt_number()
    
    def load_donation_data(self):
        """Load donation data for editing."""
        if not self.is_edit_mode:
            return
        
        try:
            donation = self.model.get_donation_by_id(self.donation_id)
            if donation:
                self.donor_name_input.setText(donation['donor_name'] or '')
                self.contact_input.setText(donation['donor_contact'] or '')
                self.amount_input.setText(str(donation['amount']) if donation['amount'] else '')
                
                # Set donation type
                donation_type = donation['donation_type'] or 'General'
                index = self.donation_type_combo.findText(donation_type)
                if index >= 0:
                    self.donation_type_combo.setCurrentIndex(index)
                
                # Set payment method
                payment_method = donation['payment_method'] or 'Cash'
                index = self.payment_method_combo.findText(payment_method)
                if index >= 0:
                    self.payment_method_combo.setCurrentIndex(index)
                
                self.receipt_input.setText(donation['receipt_number'] or '')
                self.notes_input.setText(donation['notes'] or '')
        
        except Exception as e:
            show_error(self, f"عطیہ ڈیٹا لوڈ کرنے میں خرابی: {str(e)}")
    
    def closeEvent(self, event):
        """Handle close event."""
        self.model.close_connection()
        super().closeEvent(event)
