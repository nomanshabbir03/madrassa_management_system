from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, 
                             QLabel, QLineEdit, QPushButton, QComboBox,
                             QDateEdit, QSpinBox, QShortcut)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QKeySequence
from ui.utils import (get_urdu_font, show_error, show_success, 
                     validate_required, set_field_error)
from .exam_model import ExamModel


class ExamForm(QWidget):
    exam_saved = pyqtSignal(int)  # Emitted with exam_id when saved
    cancelled = pyqtSignal()
    
    def __init__(self, exam_id=None, parent=None):
        super().__init__(parent)
        self.exam_id = exam_id
        self.model = ExamModel()
        self.is_edit_mode = exam_id is not None
        
        self.setup_ui()
        self.setup_shortcuts()
        self.load_initial_data()
        
        if self.is_edit_mode:
            self.load_exam_data()
            
    def setup_ui(self):
        """Setup the exam registration form UI."""
        self.setLayoutDirection(Qt.RightToLeft)
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Title
        title_text = "امتحان کی ترمیم" if self.is_edit_mode else "امتحان رجسٹریشن"
        title_label = QLabel(title_text)
        title_label.setFont(get_urdu_font(18, bold=True))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #D4A017; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Form grid
        form_layout = QGridLayout()
        form_layout.setSpacing(15)
        
        # Row 0: Exam Name
        self.exam_name_label = QLabel("امتحان کا نام:")
        self.exam_name_label.setFont(get_urdu_font(14))
        self.exam_name_input = QLineEdit()
        self.exam_name_input.setFont(get_urdu_font(14))
        self.exam_name_input.setPlaceholderText("مثلاً: سالانہ امتحان 2024")
        form_layout.addWidget(self.exam_name_label, 0, 0)
        form_layout.addWidget(self.exam_name_input, 0, 1)
        
        # Row 1: Class
        self.class_label = QLabel("کلاس:")
        self.class_label.setFont(get_urdu_font(14))
        self.class_combo = QComboBox()
        self.class_combo.setFont(get_urdu_font(14))
        self.class_combo.currentIndexChanged.connect(self.on_class_changed)
        form_layout.addWidget(self.class_label, 1, 0)
        form_layout.addWidget(self.class_combo, 1, 1)
        
        # Row 2: Subject
        self.subject_label = QLabel("مضمون:")
        self.subject_label.setFont(get_urdu_font(14))
        self.subject_combo = QComboBox()
        self.subject_combo.setFont(get_urdu_font(14))
        form_layout.addWidget(self.subject_label, 2, 0)
        form_layout.addWidget(self.subject_combo, 2, 1)
        
        # Row 3: Exam Date
        self.date_label = QLabel("امتحان کی تاریخ:")
        self.date_label.setFont(get_urdu_font(14))
        self.date_input = QDateEdit()
        self.date_input.setFont(get_urdu_font(14))
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setDisplayFormat("dd-MM-yyyy")
        form_layout.addWidget(self.date_label, 3, 0)
        form_layout.addWidget(self.date_input, 3, 1)
        
        # Row 4: Total Marks
        self.total_marks_label = QLabel("کل نمبر:")
        self.total_marks_label.setFont(get_urdu_font(14))
        self.total_marks_input = QSpinBox()
        self.total_marks_input.setFont(get_urdu_font(14))
        self.total_marks_input.setRange(10, 500)
        self.total_marks_input.setValue(100)
        form_layout.addWidget(self.total_marks_label, 4, 0)
        form_layout.addWidget(self.total_marks_input, 4, 1)
        
        # Row 5: Passing Marks
        self.passing_marks_label = QLabel("پاسنگ نمبر:")
        self.passing_marks_label.setFont(get_urdu_font(14))
        self.passing_marks_input = QSpinBox()
        self.passing_marks_input.setFont(get_urdu_font(14))
        self.passing_marks_input.setRange(5, 250)
        self.passing_marks_input.setValue(40)
        form_layout.addWidget(self.passing_marks_label, 5, 0)
        form_layout.addWidget(self.passing_marks_input, 5, 1)
        
        # Row 6: Exam Type
        self.type_label = QLabel("امتحان کی قسم:")
        self.type_label.setFont(get_urdu_font(14))
        self.type_combo = QComboBox()
        self.type_combo.setFont(get_urdu_font(14))
        self.type_combo.addItems(['ماہانہ', 'سہ ماہی', 'ششماہی', 'سالانہ'])
        form_layout.addWidget(self.type_label, 6, 0)
        form_layout.addWidget(self.type_combo, 6, 1)
        
        main_layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.save_btn = QPushButton("محفوظ کریں")
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
        self.save_btn.clicked.connect(self.save_exam)
        
        self.clear_btn = QPushButton("صاف کریں")
        self.clear_btn.setFont(get_urdu_font(14))
        self.clear_btn.setStyleSheet("""
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
        self.clear_btn.clicked.connect(self.clear_form)
        
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
        button_layout.addWidget(self.clear_btn)
        button_layout.addWidget(self.close_btn)
        
        main_layout.addLayout(button_layout)
        main_layout.addStretch()

    def setup_shortcuts(self):
        """Setup shortcuts for the form."""
        self.shortcut_save = QShortcut(QKeySequence("Ctrl+S"), self)
        self.shortcut_save.activated.connect(self.save_exam)
        
        self.shortcut_cancel = QShortcut(QKeySequence("Esc"), self)
        self.shortcut_cancel.activated.connect(self.close_form)

    def load_initial_data(self):
        """Populate class dropdown."""
        try:
            # Clear combos first
            self.class_combo.clear()
            self.class_combo.addItem("کلاس منتخب کریں", None)
            
            classes = self.model.get_classes()
            for class_id, class_name in classes:
                self.class_combo.addItem(class_name, class_id)
        except Exception as e:
            print(f"Error loading initial data: {e}")

    def on_class_changed(self):
        """Update subjects when class changes."""
        class_id = self.class_combo.currentData()
        self.subject_combo.clear()
        
        if class_id is None:
            return
            
        try:
            subjects = self.model.get_subjects_by_class(class_id)
            for subject_id, subject_name in subjects:
                self.subject_combo.addItem(subject_name, subject_id)
        except Exception as e:
            print(f"Error loading subjects: {e}")

    def load_exam_data(self):
        """Load exam data for editing."""
        try:
            exam = self.model.get_exam_by_id(self.exam_id)
            if exam:
                self.exam_name_input.setText(exam['exam_name'])
                
                # Select class
                class_index = self.class_combo.findData(exam['class_id'])
                if class_index >= 0:
                    self.class_combo.setCurrentIndex(class_index)
                    # Note: on_class_changed is triggered automatically
                
                # Select subject
                # We need a small delay or manual call since index change might be async or trigger after this
                subjects = self.model.get_subjects_by_class(exam['class_id'])
                self.subject_combo.clear()
                for subject_id, subject_name in subjects:
                    self.subject_combo.addItem(subject_name, subject_id)
                
                subject_index = self.subject_combo.findData(exam['subject_id'])
                if subject_index >= 0:
                    self.subject_combo.setCurrentIndex(subject_index)
                
                # Set date
                if exam['exam_date']:
                    self.date_input.setDate(QDate.fromString(exam['exam_date'], "yyyy-MM-dd"))
                
                self.total_marks_input.setValue(exam['total_marks'])
                self.passing_marks_input.setValue(exam['passing_marks'])
                
                type_index = self.type_combo.findText(exam['exam_type'])
                if type_index >= 0:
                    self.type_combo.setCurrentIndex(type_index)
                    
        except Exception as e:
            show_error(self, f"ڈیٹا لوڈ کرنے میں خطا: {str(e)}")

    def validate_form(self):
        """Validate form fields."""
        # Reset errors
        set_field_error(self.exam_name_input, False)
        set_field_error(self.class_combo, False)
        set_field_error(self.subject_combo, False)
        
        if not validate_required(self.exam_name_input.text()):
            set_field_error(self.exam_name_input, True)
            show_error(self, "امتحان کا نام ضروری ہے")
            return False
            
        if self.class_combo.currentData() is None:
            set_field_error(self.class_combo, True)
            show_error(self, "کلاس کا انتخاب ضروری ہے")
            return False
            
        if self.subject_combo.currentData() is None:
            set_field_error(self.subject_combo, True)
            show_error(self, "مضمون کا انتخاب ضروری ہے")
            return False
            
        if self.total_marks_input.value() <= 0:
            show_error(self, "کل نمبر صفر سے زیادہ ہونے چاہئیں")
            return False
            
        if self.passing_marks_input.value() > self.total_marks_input.value():
            show_error(self, "پاسنگ نمبر کل نمبروں سے زیادہ نہیں ہو سکتے")
            return False
            
        return True

    def save_exam(self):
        """Save exam to database."""
        if not self.validate_form():
            return
            
        try:
            exam_name = self.exam_name_input.text().strip()
            class_id = self.class_combo.currentData()
            subject_id = self.subject_combo.currentData()
            exam_date = self.date_input.date().toString("yyyy-MM-dd")
            total_marks = self.total_marks_input.value()
            passing_marks = self.passing_marks_input.value()
            exam_type = self.type_combo.currentText()
            
            if self.is_edit_mode:
                success = self.model.update_exam(
                    self.exam_id,
                    exam_name=exam_name,
                    class_id=class_id,
                    subject_id=subject_id,
                    exam_date=exam_date,
                    total_marks=total_marks,
                    passing_marks=passing_marks,
                    exam_type=exam_type
                )
                if success:
                    show_success(self, "معلومات کامیابی سے تبدیل ہوگئیں")
                    self.exam_saved.emit(self.exam_id)
                else:
                    show_error(self, "معلومات محفوظ کرنے میں ناکامی")
            else:
                exam_id = self.model.add_exam(
                    exam_name, class_id, subject_id, exam_date,
                    total_marks, passing_marks, exam_type
                )
                if exam_id:
                    show_success(self, "امتحان کامیابی سے رجسٹر ہو گیا")
                    self.exam_saved.emit(exam_id)
                    self.clear_form()
                else:
                    show_error(self, "امتحان رجسٹر کرنے میں ناکامی")
                    
        except Exception as e:
            show_error(self, f"خرابی: {str(e)}")

    def clear_form(self):
        """Reset the form."""
        self.exam_name_input.clear()
        self.class_combo.setCurrentIndex(0)
        self.date_input.setDate(QDate.currentDate())
        self.total_marks_input.setValue(100)
        self.passing_marks_input.setValue(40)
        self.type_combo.setCurrentIndex(0)
        self.exam_name_input.setFocus()

    def close_form(self):
        """Emit cancelled signal."""
        self.cancelled.emit()
