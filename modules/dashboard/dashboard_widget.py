from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QGridLayout, QSizePolicy
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from ui.utils import get_urdu_font, to_urdu_numerals, format_date_urdu, get_today_date, get_current_month_year
from ui.styles import COLOR_SIDEBAR, COLOR_ACCENT, COLOR_SUCCESS, COLOR_ERROR, COLOR_WARNING
from database import get_connection
import datetime


class DashboardWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setLayoutDirection(Qt.RightToLeft)
        self.setup_ui()
        self.load_statistics()

    def setup_ui(self):
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Top heading
        heading_label = QLabel("مرکزی صفحہ — خلاصہ")
        heading_label.setObjectName("heading_label")
        heading_label.setFont(get_urdu_font(18, bold=True))
        heading_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        main_layout.addWidget(heading_label)
        
        # Subtitle with today's date
        today_date = get_today_date()
        formatted_date = format_date_urdu(today_date)
        subtitle_label = QLabel(f"تاریخ: {formatted_date}")
        subtitle_label.setFont(get_urdu_font(13))
        subtitle_label.setStyleSheet("color: gray;")
        subtitle_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        main_layout.addWidget(subtitle_label)
        
        # Horizontal line separator
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("background-color: #E0E0E0; max-height: 1px;")
        main_layout.addWidget(line)
        
        # Grid layout for summary cards
        cards_grid = QGridLayout()
        cards_grid.setSpacing(15)
        
        # Create 4 cards
        card1, self.students_label = self.create_stat_card("کل طلباء", "👨‍🎓", "#1B4332")
        card2, self.employees_label = self.create_stat_card("کل ملازمین", "👥", "#2D6A4F")
        card3, self.attendance_label = self.create_stat_card("آج کی حاضری", "📋", "#D4A017")
        card4, self.fees_label = self.create_stat_card("ماہانہ فیس وصولی", "💰", "#B8860B")
        
        # Place cards in 2x2 grid
        cards_grid.addWidget(card1, 0, 0)
        cards_grid.addWidget(card2, 0, 1)
        cards_grid.addWidget(card3, 1, 0)
        cards_grid.addWidget(card4, 1, 1)
        
        main_layout.addLayout(cards_grid)
        
        # Add stretch spacer
        main_layout.addStretch()
        
        # Bottom label
        bottom_label = QLabel("تازہ کاری کے لیے ماڈیول پر کلک کریں")
        bottom_label.setFont(get_urdu_font(11))
        bottom_label.setStyleSheet("color: gray;")
        bottom_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(bottom_label)
        
        self.setLayout(main_layout)

    def create_stat_card(self, title, icon, color):
        # Card frame
        card_frame = QFrame()
        card_frame.setObjectName("card_frame")
        card_frame.setMinimumHeight(150)
        card_frame.setMinimumWidth(200)
        card_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Card layout
        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(20, 20, 20, 20)
        
        # Top row with icon and title
        top_row = QHBoxLayout()
        
        # Icon label
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 32))
        icon_label.setStyleSheet("color: white;")
        
        # Title label
        title_label = QLabel(title)
        title_label.setFont(get_urdu_font(14))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        
        top_row.addWidget(icon_label)
        top_row.addWidget(title_label)
        top_row.addStretch()
        
        # Value label
        value_label = QLabel("...")
        value_label.setFont(get_urdu_font(36, bold=True))
        value_label.setStyleSheet("color: white;")
        value_label.setAlignment(Qt.AlignCenter)
        
        # Description label
        desc_label = QLabel(title)
        desc_label.setFont(get_urdu_font(12))
        desc_label.setStyleSheet("color: white; opacity: 0.8;")
        desc_label.setAlignment(Qt.AlignCenter)
        
        # Add to layout
        card_layout.addLayout(top_row)
        card_layout.addWidget(value_label)
        card_layout.addWidget(desc_label)
        
        card_frame.setLayout(card_layout)
        
        # Set card style
        card_frame.setStyleSheet(f"""
            QFrame#card_frame {{
                background-color: {color};
                border-radius: 12px;
                color: white;
            }}
        """)
        
        return card_frame, value_label

    def load_statistics(self):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # Query 1: Total active students
            cursor.execute("SELECT COUNT(*) FROM students WHERE status = 'active'")
            students_count = cursor.fetchone()[0]
            self.students_label.setText(to_urdu_numerals(students_count))
            
            # Query 2: Total active employees
            cursor.execute("SELECT COUNT(*) FROM employees WHERE status = 'active'")
            employees_count = cursor.fetchone()[0]
            self.employees_label.setText(to_urdu_numerals(employees_count))
            
            # Query 3: Today's attendance
            today = get_today_date()
            cursor.execute("SELECT COUNT(*) FROM attendance WHERE date = ? AND status = 'present'", (today,))
            attendance_count = cursor.fetchone()[0]
            self.attendance_label.setText(to_urdu_numerals(attendance_count))
            
            # Query 4: Monthly fees collection
            current_month, current_year = get_current_month_year()
            cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM fees WHERE year = ? AND month = ?", 
                         (current_year, current_month))
            fees_total = cursor.fetchone()[0]
            fees_text = f"روپے {to_urdu_numerals(int(fees_total))}"
            self.fees_label.setText(fees_text)
            
        except Exception as e:
            print(f"Error loading statistics: {e}")
            # Set error state
            self.students_label.setText("خطا")
            self.employees_label.setText("خطا")
            self.attendance_label.setText("خطا")
            self.fees_label.setText("خطا")
        finally:
            if 'conn' in locals():
                conn.close()

    def refresh(self):
        """Refresh dashboard statistics"""
        self.load_statistics()
