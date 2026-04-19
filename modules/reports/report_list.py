import os
import subprocess
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QComboBox, QPushButton, QTabWidget, QDateEdit, 
                             QSpinBox, QLineEdit, QFileDialog, QFrame, QShortcut)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QKeySequence

from ui.utils import (get_urdu_font, show_error, show_success, to_urdu_numerals,
                     validate_required)
from ui.styles import COLOR_ACCENT, COLOR_SIDEBAR, COLOR_TEXT_LIGHT
from database import get_connection
from .report_generator import ReportGenerator

class ReportList(QWidget):
    def __init__(self):
        super().__init__()
        self.generator = ReportGenerator()
        self.setLayoutDirection(Qt.RightToLeft)
        self.setup_ui()
        self.setup_shortcuts()
        self.load_initial_data()

    def setup_ui(self):
        """Setup the UI for reports selection and generation."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Heading
        heading_label = QLabel("رپورٹس کا حصہ")
        heading_label.setFont(get_urdu_font(20, bold=True))
        heading_label.setStyleSheet(f"color: {COLOR_ACCENT}; margin-bottom: 20px;")
        heading_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(heading_label)
        
        # Output Directory Configuration
        dir_frame = QFrame()
        dir_frame.setStyleSheet("background-color: #f8f9fa; border-radius: 8px; padding: 10px;")
        dir_layout = QHBoxLayout(dir_frame)
        
        dir_label = QLabel("رپورٹ محفوظ کرنے کا فولڈر:")
        dir_label.setFont(get_urdu_font(12))
        
        self.output_dir_input = QLineEdit(self.generator.output_dir)
        self.output_dir_input.setFont(get_urdu_font(12))
        self.output_dir_input.setReadOnly(True)
        
        open_dir_btn = QPushButton("فولڈر کھولیں")
        open_dir_btn.setFont(get_urdu_font(12))
        open_dir_btn.setStyleSheet(f"background-color: {COLOR_SIDEBAR}; color: {COLOR_TEXT_LIGHT};")
        open_dir_btn.clicked.connect(self.open_output_folder)
        
        browse_btn = QPushButton("براؤز کریں")
        browse_btn.setFont(get_urdu_font(12))
        browse_btn.setStyleSheet(f"background-color: {COLOR_SIDEBAR}; color: {COLOR_TEXT_LIGHT};")
        browse_btn.clicked.connect(self.browse_output_directory)
        
        dir_layout.addWidget(dir_label)
        dir_layout.addWidget(self.output_dir_input)
        dir_layout.addWidget(browse_btn)
        dir_layout.addWidget(open_dir_btn)
        main_layout.addWidget(dir_frame)

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.setFont(get_urdu_font(14))
        self.tabs.setLayoutDirection(Qt.RightToLeft)
        
        # Create tabs
        self._setup_student_tab()
        self._setup_financial_tab()
        self._setup_exam_tab()
        self._setup_attendance_tab()
        self._setup_receipt_tab()
        
        main_layout.addWidget(self.tabs)
        
        # Status Label
        self.status_label = QLabel("")
        self.status_label.setFont(get_urdu_font(12))
        self.status_label.setStyleSheet("color: #2D6A4F; font-weight: bold;")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

    def setup_shortcuts(self):
        """Setup shortcuts for reports."""
        self.shortcut_focus = QShortcut(QKeySequence("Ctrl+F"), self)
        self.shortcut_focus.activated.connect(lambda: self.tabs.setFocus())

    def _setup_student_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(20)
        
        label = QLabel("طالب علم منتخب کریں:")
        label.setFont(get_urdu_font(14))
        self.student_combo = QComboBox()
        self.student_combo.setFont(get_urdu_font(14))
        self.student_combo.setMinimumWidth(300)
        
        btn_layout = QHBoxLayout()
        detailed_btn = QPushButton("تفصیلی رپورٹ")
        detailed_btn.setFont(get_urdu_font(12))
        detailed_btn.clicked.connect(lambda: self.on_generate_student_report('detailed'))
        
        btn_layout.addWidget(detailed_btn)
        btn_layout.addStretch()
        
        layout.addWidget(label)
        layout.addWidget(self.student_combo)
        layout.addLayout(btn_layout)
        layout.addStretch()
        self.tabs.addTab(tab, "طلباء کی رپورٹس")

    def _setup_financial_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setSpacing(15)
        
        type_label = QLabel("رپورٹ کی قسم:")
        self.fin_type_combo = QComboBox()
        self.fin_type_combo.addItems(['ماہانہ فیس', 'عطیات', 'ملازمین کی تنخواہ'])
        self.fin_type_combo.setFont(get_urdu_font(13))
        
        # Container for dynamic fields
        self.fin_container = QWidget()
        fin_vbox = QVBoxLayout(self.fin_container)
        
        # Month/Year Layout
        self.month_year_layout = QHBoxLayout()
        self.month_combo = QComboBox()
        self.month_combo.addItems([self.generator.months_urdu[i] for i in range(1, 13)])
        self.year_spin = QSpinBox()
        self.year_spin.setRange(2020, 2030)
        self.year_spin.setValue(datetime.now().year)
        self.month_year_layout.addWidget(QLabel("مہینہ:"))
        self.month_year_layout.addWidget(self.month_combo)
        self.month_year_layout.addWidget(QLabel("سال:"))
        self.month_year_layout.addWidget(self.year_spin)
        
        # Date Range Layout
        self.date_range_layout = QHBoxLayout()
        self.from_date = QDateEdit(QDate.currentDate().addMonths(-1))
        self.to_date = QDateEdit(QDate.currentDate())
        self.date_range_layout.addWidget(QLabel("تاریخ سے:"))
        self.date_range_layout.addWidget(self.from_date)
        self.date_range_layout.addWidget(QLabel("تک:"))
        self.date_range_layout.addWidget(self.to_date)
        
        fin_vbox.addLayout(self.month_year_layout)
        fin_vbox.addLayout(self.date_range_layout)
        
        generate_btn = QPushButton("رپورٹ بنائیں")
        generate_btn.setFont(get_urdu_font(13))
        generate_btn.clicked.connect(self.on_generate_financial_report)
        
        layout.addWidget(type_label)
        layout.addWidget(self.fin_type_combo)
        layout.addWidget(self.fin_container)
        layout.addWidget(generate_btn)
        layout.addStretch()
        self.tabs.addTab(tab, "مالی رپورٹس")

    def _setup_exam_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        label = QLabel("امتحان منتخب کریں:")
        self.exam_combo = QComboBox()
        self.exam_combo.setFont(get_urdu_font(13))
        
        btn = QPushButton("نتائج کی رپورٹ بنائیں")
        btn.setFont(get_urdu_font(13))
        btn.clicked.connect(self.on_generate_exam_report)
        
        layout.addWidget(label)
        layout.addWidget(self.exam_combo)
        layout.addWidget(btn)
        layout.addStretch()
        self.tabs.addTab(tab, "امتحانی رپورٹس")

    def _setup_attendance_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        class_label = QLabel("کلاس:")
        self.class_combo = QComboBox()
        
        month_label = QLabel("مہینہ:")
        self.att_month_combo = QComboBox()
        self.att_month_combo.addItems([self.generator.months_urdu[i] for i in range(1, 13)])
        
        year_label = QLabel("سال:")
        self.att_year_spin = QSpinBox()
        self.att_year_spin.setRange(2020, 2030)
        self.att_year_spin.setValue(datetime.now().year)
        
        btn = QPushButton("حاضری رپورٹ بنائیں")
        btn.clicked.connect(self.on_generate_attendance_report)
        
        layout.addWidget(class_label)
        layout.addWidget(self.class_combo)
        layout.addWidget(month_label)
        layout.addWidget(self.att_month_combo)
        layout.addWidget(year_label)
        layout.addWidget(self.att_year_spin)
        layout.addWidget(btn)
        layout.addStretch()
        self.tabs.addTab(tab, "حاضری کی رپورٹس")

    def _setup_receipt_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        type_label = QLabel("قسم:")
        self.receipt_type_combo = QComboBox()
        self.receipt_type_combo.addItems(['فیس کی رسید', 'عطیہ کی رسید'])
        
        id_label = QLabel("رسید نمبر / آئی ڈی درج کریں:")
        self.receipt_id_input = QLineEdit()
        self.receipt_id_input.setPlaceholderText("مثلاً: 123")
        
        btn = QPushButton("رسید تلاش کریں اور بنائیں")
        btn.clicked.connect(self.on_generate_receipt)
        
        layout.addWidget(type_label)
        layout.addWidget(self.receipt_type_combo)
        layout.addWidget(id_label)
        layout.addWidget(self.receipt_id_input)
        layout.addWidget(btn)
        layout.addStretch()
        self.tabs.addTab(tab, "رسیدیں")

    def load_initial_data(self):
        """Populate dropdowns from database."""
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Students
            cursor.execute("SELECT id, full_name FROM students WHERE status='active' ORDER BY full_name")
            for sid, name in cursor.fetchall():
                self.student_combo.addItem(name, sid)
                
            # Classes
            cursor.execute("SELECT id, class_name FROM classes ORDER BY class_name")
            for cid, name in cursor.fetchall():
                self.class_combo.addItem(name, cid)
                
            # Exams
            cursor.execute("SELECT id, exam_name FROM exams ORDER BY exam_date DESC")
            for eid, name in cursor.fetchall():
                self.exam_combo.addItem(name, eid)
                
        except Exception as e:
            print(f"Error loading initial data: {e}")
        finally:
            if 'conn' in locals(): conn.close()

    def on_generate_student_report(self, r_type):
        student_id = self.student_combo.currentData()
        if not student_id:
            show_error(self, "پہلے طالب علم منتخب کریں")
            return
            
        self.status_label.setText("رپورٹ تیار ہو رہی ہے...")
        path = self.generator.generate_student_report(student_id)
        if path:
            self.status_label.setText(f"رپورٹ بن گئی: {os.path.basename(path)}")
            show_success(self, "رپورٹ کامیابی سے بنائی گئی")
        else:
            self.status_label.setText("رپورٹ بنانے میں ناکامی")

    def on_generate_financial_report(self):
        r_type = self.fin_type_combo.currentText()
        self.status_label.setText("رپورٹ تیار ہو رہی ہے...")
        
        path = None
        if r_type == 'ماہانہ فیس':
            month = self.month_combo.currentIndex() + 1
            year = self.year_spin.value()
            path = self.generator.generate_fee_summary_report(month, year)
        elif r_type == 'عطیات':
            start = self.from_date.date().toString("yyyy-MM-dd")
            end = self.to_date.date().toString("yyyy-MM-dd")
            path = self.generator.generate_donation_report(start, end)
        else: # Employees
            path = self.generator.generate_employee_report()
            
        if path:
            self.status_label.setText(f"رپورٹ بن گئی: {os.path.basename(path)}")
            show_success(self, "رپورٹ کامیابی سے بنائی گئی")

    def on_generate_exam_report(self):
        exam_id = self.exam_combo.currentData()
        if not exam_id: return
        
        path = self.generator.generate_exam_result_report(exam_id)
        if path:
            show_success(self, "رپورٹ کامیابی سے بنائی گئی")

    def on_generate_attendance_report(self):
        class_id = self.class_combo.currentData()
        month = self.att_month_combo.currentIndex() + 1
        year = self.att_year_spin.value()
        
        path = self.generator.generate_attendance_report(class_id, month, year)
        if path:
            show_success(self, "رپورٹ کامیابی سے بنائی گئی")

    def on_generate_receipt(self):
        r_type_text = self.receipt_type_combo.currentText()
        r_type = 'fee' if 'فیس' in r_type_text else 'donation'
        r_id = self.receipt_id_input.text().strip()
        
        if not validate_required(r_id):
            show_error(self, "آئی ڈی نمبر درج کریں")
            return
            
        path = self.generator.generate_general_receipt(r_type, r_id)
        if path:
            show_success(self, "رسید کامیابی سے بنائی گئی")
            self.open_pdf(path)

    def open_pdf(self, path):
        """Open generated PDF in default viewer."""
        try:
            if os.name == 'nt':
                os.startfile(path)
            else:
                subprocess.run(['xdg-open', path])
        except Exception as e:
            print(f"Error opening PDF: {e}")

    def browse_output_directory(self):
        """Allow user to choose output directory for reports."""
        directory = QFileDialog.getExistingDirectory(self, "فولڈر منتخب کریں", self.generator.output_dir)
        if directory:
            self.generator.output_dir = directory + "/"
            self.output_dir_input.setText(directory)

    def open_output_folder(self):
        """Open reports directory in explorer."""
        try:
            os.startfile(self.generator.output_dir)
        except Exception as e:
            print(f"Error opening folder: {e}")
