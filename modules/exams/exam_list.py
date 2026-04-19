from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QComboBox, QDateEdit, QFrame, 
                             QGridLayout, QAbstractItemView, QMessageBox, QShortcut)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QKeySequence

from ui.utils import (get_urdu_font, show_error, show_success, to_urdu_numerals, 
                     format_date_urdu, clear_table)
from ui.styles import apply_table_style, COLOR_ACCENT, COLOR_SIDEBAR
from .exam_model import ExamModel
from .exam_form import ExamForm
from .result_form import ResultForm


class ExamList(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = ExamModel()
        self.setup_ui()
        self.setup_shortcuts()
        self.load_classes()
        self.refresh_table()
        
    def setup_ui(self):
        """Setup the exam list UI."""
        self.setLayoutDirection(Qt.RightToLeft)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header
        header_label = QLabel("امتحانات کی فہرست")
        header_label.setFont(get_urdu_font(20, bold=True))
        header_label.setStyleSheet(f"color: {COLOR_ACCENT}; margin-bottom: 10px;")
        main_layout.addWidget(header_label)
        
        # Summary Cards
        self.summary_layout = QGridLayout()
        self.summary_layout.setSpacing(15)
        main_layout.addLayout(self.summary_layout)
        self.update_summary_cards()
        
        # Filter Bar
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
        
        # Class Filter
        class_label = QLabel("کلاس:")
        class_label.setFont(get_urdu_font(12))
        self.class_filter = QComboBox()
        self.class_filter.setFont(get_urdu_font(12))
        self.class_filter.setFixedWidth(150)
        
        # Type Filter
        type_label = QLabel("قسم:")
        type_label.setFont(get_urdu_font(12))
        self.type_filter = QComboBox()
        self.type_filter.setFont(get_urdu_font(12))
        self.type_filter.addItems(['تمام', 'ماہانہ', 'سہ ماہی', 'ششماہی', 'سالانہ'])
        self.type_filter.setFixedWidth(120)
        
        # Date Filters
        from_label = QLabel("تاریخ سے:")
        from_label.setFont(get_urdu_font(12))
        self.from_date = QDateEdit()
        self.from_date.setFont(get_urdu_font(12))
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addMonths(-3))
        
        to_label = QLabel("تاریخ تک:")
        to_label.setFont(get_urdu_font(12))
        self.to_date = QDateEdit()
        self.to_date.setFont(get_urdu_font(12))
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate().addMonths(1))
        
        # Search Button
        search_btn = QPushButton("تلاش کریں")
        search_btn.setFont(get_urdu_font(12))
        search_btn.setStyleSheet("""
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
        search_btn.clicked.connect(self.refresh_table)
        
        # Action Buttons
        new_exam_btn = QPushButton("نیا امتحان")
        new_exam_btn.setFont(get_urdu_font(12))
        new_exam_btn.setStyleSheet(f"background-color: {COLOR_SIDEBAR}; color: white; padding: 8px 16px; border-radius: 4px;")
        new_exam_btn.clicked.connect(self.on_add_exam)
        
        results_btn = QPushButton("نتائج درج کریں")
        results_btn.setFont(get_urdu_font(12))
        results_btn.setStyleSheet(f"background-color: {COLOR_ACCENT}; color: white; padding: 8px 16px; border-radius: 4px;")
        results_btn.clicked.connect(self.on_enter_results)
        
        filter_layout.addWidget(class_label)
        filter_layout.addWidget(self.class_filter)
        filter_layout.addWidget(type_label)
        filter_layout.addWidget(self.type_filter)
        filter_layout.addWidget(from_label)
        filter_layout.addWidget(self.from_date)
        filter_layout.addWidget(to_label)
        filter_layout.addWidget(self.to_date)
        filter_layout.addWidget(search_btn)
        filter_layout.addStretch()
        filter_layout.addWidget(new_exam_btn)
        filter_layout.addWidget(results_btn)
        
        main_layout.addWidget(filter_frame)
        
        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "امتحان", "کلاس", "مضمون", "تاریخ", "کل نمبر", "پاسنگ نمبر", "قسم", "عمل"
        ])
        apply_table_style(self.table)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        for i in range(1, 7):
            header.setSectionResizeMode(i, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(7, QHeaderView.Fixed)
        self.table.setColumnWidth(7, 200)
        
        main_layout.addWidget(self.table)
        
        # Status Label for empty state
        self.status_label = QLabel("")
        self.status_label.setFont(get_urdu_font(12))
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

    def setup_shortcuts(self):
        """Setup shortcuts for exam list."""
        self.shortcut_new = QShortcut(QKeySequence("Ctrl+N"), self)
        self.shortcut_new.activated.connect(self.on_add_exam)
        
        self.shortcut_search = QShortcut(QKeySequence("Ctrl+F"), self)
        self.shortcut_search.activated.connect(lambda: self.class_filter.setFocus())

    def create_summary_card(self, title, value, color):
        """Create a stylized summary card."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 10px;
                border-left: 5px solid {color};
                padding: 15px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        
        val_label = QLabel(to_urdu_numerals(value))
        val_label.setFont(get_urdu_font(20, bold=True))
        val_label.setStyleSheet(f"color: {color};")
        
        title_label = QLabel(title)
        title_label.setFont(get_urdu_font(12))
        title_label.setStyleSheet("color: #7F8C8D;")
        
        card_layout.addWidget(val_label)
        card_layout.addWidget(title_label)
        return card

    def update_summary_cards(self):
        """Update the statistical summary cards."""
        # Clear existing cards
        for i in reversed(range(self.summary_layout.count())): 
            self.summary_layout.itemAt(i).widget().setParent(None)
            
        try:
            total_exams = len(self.model.get_all_exams())
            upcoming = len(self.model.get_upcoming_exams(7))
            this_month = self.model.get_this_month_exams_count()
            types = self.model.get_exam_types_summary()
            
            # Create cards
            self.summary_layout.addWidget(self.create_summary_card("کل امتحانات", total_exams, "#27AE60"), 0, 0)
            self.summary_layout.addWidget(self.create_summary_card("آنے والے امتحانات (7 دن)", upcoming, "#E67E22"), 0, 1)
            self.summary_layout.addWidget(self.create_summary_card("اس ماہ", this_month, "#2980B9"), 0, 2)
            
            types_str = f"ماہانہ: {to_urdu_numerals(types.get('ماہانہ', 0))} | سالانہ: {to_urdu_numerals(types.get('سالانہ', 0))}"
            self.summary_layout.addWidget(self.create_summary_card("اقسام", types_str, "#8E44AD"), 0, 3)
        except Exception as e:
            print(f"Error updating summary cards: {e}")

    def load_classes(self):
        """Populate class filter."""
        try:
            self.class_filter.clear()
            self.class_filter.addItem("تمام", None)
            classes = self.model.get_classes()
            for cid, name in classes:
                self.class_filter.addItem(name, cid)
        except Exception as e:
            print(f"Error loading classes: {e}")

    def refresh_table(self):
        """Fetch data and populate table."""
        filters = {
            'class_id': self.class_filter.currentData(),
            'exam_type': None if self.type_filter.currentText() == 'تمام' else self.type_filter.currentText(),
            'date_from': self.from_date.date().toString("yyyy-MM-dd"),
            'date_to': self.to_date.date().toString("yyyy-MM-dd")
        }
        
        try:
            exams = self.model.get_all_exams(filters)
            clear_table(self.table)
            self.table.setRowCount(len(exams))
            
            for row, exam in enumerate(exams):
                self.table.setItem(row, 0, QTableWidgetItem(exam['exam_name']))
                self.table.setItem(row, 1, QTableWidgetItem(exam['class_name']))
                self.table.setItem(row, 2, QTableWidgetItem(exam['subject_name']))
                
                # Format Date DD-MM-YYYY Urdu
                dt = QDate.fromString(exam['exam_date'], "yyyy-MM-dd")
                date_str = to_urdu_numerals(dt.toString("dd-MM-yyyy"))
                self.table.setItem(row, 3, QTableWidgetItem(date_str))
                
                self.table.setItem(row, 4, QTableWidgetItem(to_urdu_numerals(exam['total_marks'])))
                self.table.setItem(row, 5, QTableWidgetItem(to_urdu_numerals(exam['passing_marks'])))
                self.table.setItem(row, 6, QTableWidgetItem(exam['exam_type']))
                
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(5, 2, 5, 2)
                
                edit_btn = QPushButton("ترمیم")
                edit_btn.setStyleSheet("background-color: #F39C12; color: white; border-radius: 3px; padding: 3px;")
                edit_btn.clicked.connect(lambda _, eid=exam['id']: self.on_edit_exam(eid))
                
                delete_btn = QPushButton("حذف")
                delete_btn.setStyleSheet("background-color: #E74C3C; color: white; border-radius: 3px; padding: 3px;")
                delete_btn.clicked.connect(lambda _, eid=exam['id']: self.on_delete_exam(eid))
                
                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)
                self.table.setCellWidget(row, 7, actions_widget)
                
            if len(exams) == 0:
                self.status_label.setText("کوئی ریکارڈ نہیں ملا")
                self.status_label.setStyleSheet("color: #DC3545; font-weight: bold;")
            else:
                self.status_label.setText("")
                
            self.update_summary_cards()
        except Exception as e:
            show_error(self, f"ٹیبل ریفریش کرنے میں خطا: {str(e)}")

    def on_add_exam(self):
        """Open ExamForm as dialog."""
        self.form_window = QWidget()
        self.form_window.setWindowFlags(Qt.Dialog | Qt.Window)
        self.form_window.setWindowTitle("نیا امتحان")
        self.form_window.setMinimumSize(500, 600)
        
        layout = QVBoxLayout(self.form_window)
        form = ExamForm()
        form.exam_saved.connect(lambda: (self.refresh_table(), self.form_window.close()))
        form.cancelled.connect(self.form_window.close)
        layout.addWidget(form)
        
        self.form_window.show()

    def on_edit_exam(self, exam_id):
        """Open ExamForm pre-filled."""
        self.form_window = QWidget()
        self.form_window.setWindowFlags(Qt.Dialog | Qt.Window)
        self.form_window.setWindowTitle("امتحان میں ترمیم")
        self.form_window.setMinimumSize(500, 600)
        
        layout = QVBoxLayout(self.form_window)
        form = ExamForm(exam_id=exam_id)
        form.exam_saved.connect(lambda: (self.refresh_table(), self.form_window.close()))
        form.cancelled.connect(self.form_window.close)
        layout.addWidget(form)
        
        self.form_window.show()

    def on_delete_exam(self, exam_id):
        """Confirm and delete exam."""
        reply = QMessageBox.question(self, "تصدیق", "کیا آپ واقعی یہ امتحان حذف کرنا چاہتے ہیں؟ تمام نتائج بھی حذف ہو جائیں گے۔",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.model.delete_exam(exam_id):
                show_success(self, "امتحان کامیابی سے حذف کر دیا گیا")
                self.refresh_table()
            else:
                show_error(self, "حذف کرنے میں ناکامی")

    def on_enter_results(self):
        """Open ResultForm."""
        self.res_window = QWidget()
        self.res_window.setWindowFlags(Qt.Dialog | Qt.Window)
        self.res_window.setWindowTitle("نتائج کا اندراج")
        self.res_window.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self.res_window)
        form = ResultForm()
        form.results_saved.connect(lambda: (self.refresh_table(), self.res_window.close()))
        form.cancelled.connect(self.res_window.close)
        layout.addWidget(form)
        
        self.res_window.show()
