from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTableWidget, QTableWidgetItem, 
                             QHeaderView, QComboBox, QSpinBox, QLineEdit)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor

from ui.utils import (get_urdu_font, show_error, show_success, 
                     to_urdu_numerals, clear_table)
from .exam_model import ExamModel
from .result_model import ResultModel


class ResultForm(QWidget):
    results_saved = pyqtSignal()
    cancelled = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.exam_model = ExamModel()
        self.result_model = ResultModel()
        self.current_exam_id = None
        self.exam_config = {} # total_marks, passing_marks
        
        self.setup_ui()
        self.load_exams()
        
    def setup_ui(self):
        """Setup the result entry form UI."""
        self.setLayoutDirection(Qt.RightToLeft)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Title
        title_label = QLabel("نتائج کا اندراج")
        title_label.setFont(get_urdu_font(18, bold=True))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #D4A017; margin-bottom: 15px;")
        main_layout.addWidget(title_label)
        
        # Section 1: Exam Selection
        selection_layout = QHBoxLayout()
        selection_label = QLabel("امتحان منتخب کریں:")
        selection_label.setFont(get_urdu_font(14))
        
        self.exam_combo = QComboBox()
        self.exam_combo.setFont(get_urdu_font(14))
        self.exam_combo.setMinimumWidth(400)
        self.exam_combo.currentIndexChanged.connect(self.on_exam_selected)
        
        selection_layout.addWidget(selection_label)
        selection_layout.addWidget(self.exam_combo)
        selection_layout.addStretch()
        main_layout.addLayout(selection_layout)
        
        # Section 2: Results Table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "طالب علم", "رول نمبر", "حاصل کردہ نمبر", "ریمارکس", "نتیجہ"
        ])
        
        header = self.table.horizontalHeader()
        header.setFont(get_urdu_font(12, bold=True))
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        self.table.setAlternatingRowColors(True)
        self.table.setFont(get_urdu_font(12))
        main_layout.addWidget(self.table)
        
        # Section 3: Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.save_btn = QPushButton("تمام نتائج محفوظ کریں")
        self.save_btn.setFont(get_urdu_font(14))
        self.save_btn.setStyleSheet("""
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
        self.save_btn.clicked.connect(self.save_all_results)
        
        self.close_btn = QPushButton("بند کریں")
        self.close_btn.setFont(get_urdu_font(14))
        self.close_btn.setStyleSheet("""
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
        self.close_btn.clicked.connect(self.close_form)
        
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.close_btn)
        button_layout.addStretch()
        main_layout.addLayout(button_layout)

    def load_exams(self):
        """Populate exam dropdown."""
        try:
            self.exam_combo.clear()
            self.exam_combo.addItem("امتحان منتخب کریں...", None)
            
            exams = self.exam_model.get_all_exams()
            for exam in exams:
                display_text = f"{exam['exam_name']} - {exam['class_name']} ({exam['exam_date']})"
                self.exam_combo.addItem(display_text, exam['id'])
        except Exception as e:
            print(f"Error loading exams: {e}")

    def on_exam_selected(self):
        """Load students when exam is selected."""
        exam_id = self.exam_combo.currentData()
        if not exam_id:
            clear_table(self.table)
            return
            
        self.current_exam_id = exam_id
        try:
            # Get exam config
            exam = self.exam_model.get_exam_by_id(exam_id)
            if not exam: return
            
            self.exam_config = {
                'total_marks': exam['total_marks'],
                'passing_marks': exam['passing_marks'],
                'class_id': exam['class_id']
            }
            
            # Load students
            students = self.result_model.get_students_by_class(exam['class_id'])
            # Load existing results
            existing_results = self.result_model.get_all_results(exam_id=exam_id)
            results_map = {res['student_id']: res for res in existing_results}
            
            self.populate_table(students, results_map)
            
        except Exception as e:
            show_error(self, f"طلباء لود کرنے میں خطا: {str(e)}")

    def populate_table(self, students, results_map):
        """Populate table with students and their existing results."""
        self.table.setRowCount(len(students))
        
        for row, student in enumerate(students):
            # Student Name
            name_item = QTableWidgetItem(student['full_name'])
            name_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            self.table.setItem(row, 0, name_item)
            
            # Roll Number (Registration)
            roll_item = QTableWidgetItem(to_urdu_numerals(student['registration_number']))
            roll_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            roll_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, roll_item)
            
            # Obtained Marks (SpinBox)
            marks_spin = QSpinBox()
            marks_spin.setRange(0, self.exam_config['total_marks'])
            marks_spin.setFont(get_urdu_font(12))
            
            # Remarks (LineEdit)
            remarks_input = QLineEdit()
            remarks_input.setFont(get_urdu_font(12))
            
            # Status (Label)
            status_item = QTableWidgetItem()
            status_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            status_item.setTextAlignment(Qt.AlignCenter)
            
            # Apply existing data if available
            res_data = results_map.get(student['id'])
            if res_data:
                marks_spin.setValue(res_data['obtained_marks'])
                remarks_input.setText(res_data['remarks'] or "")
            
            # Connect spinbox to update status
            marks_spin.valueChanged.connect(lambda val, r=row: self.update_row_status(r, val))
            
            # Add to table
            self.table.setCellWidget(row, 2, marks_spin)
            self.table.setCellWidget(row, 3, remarks_input)
            self.table.setItem(row, 4, status_item)
            
            # Initial status update
            self.update_row_status(row, marks_spin.value())
            
            # Store student_id in name_item
            name_item.setData(Qt.UserRole, student['id'])

    def update_row_status(self, row, marks):
        """Update the pass/fail status in the table."""
        status_item = self.table.item(row, 4)
        if marks >= self.exam_config['passing_marks']:
            status_item.setText("پاس")
            status_item.setForeground(QColor("green"))
        else:
            status_item.setText("فیل")
            status_item.setForeground(QColor("red"))

    def save_all_results(self):
        """Collect all data and save to database."""
        if not self.current_exam_id:
            show_error(self, "پہلے امتحان منتخب کریں")
            return
            
        results_list = []
        for row in range(self.table.rowCount()):
            student_id = self.table.item(row, 0).data(Qt.UserRole)
            marks_spin = self.table.cellWidget(row, 2)
            remarks_input = self.table.cellWidget(row, 3)
            
            results_list.append({
                'student_id': student_id,
                'obtained_marks': marks_spin.value(),
                'remarks': remarks_input.text().strip()
            })
            
        try:
            count = self.result_model.bulk_add_results(self.current_exam_id, results_list)
            if count > 0:
                show_success(self, f"{to_urdu_numerals(count)} طلباء کے نتائج محفوظ کر لیے گئے ہیں")
                self.results_saved.emit()
            else:
                show_error(self, "نتائج محفوظ کرنے میں ناکامی")
        except Exception as e:
            show_error(self, f"خرابی: {str(e)}")

    def close_form(self):
        self.cancelled.emit()
