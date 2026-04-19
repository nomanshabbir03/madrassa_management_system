from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QPushButton, QLabel, QStackedWidget, QFrame, 
                             QSizePolicy, QApplication)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QScreen

from ui.styles import get_main_stylesheet, COLOR_SIDEBAR, COLOR_ACCENT, FONT_FAMILY
from ui.utils import get_urdu_font
import database
from modules.dashboard.dashboard_widget import DashboardWidget
from modules.students.student_list import StudentList
from modules.employees.employee_list import EmployeeList
from modules.attendance.attendance_form import AttendanceWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize database on startup
        database.initialize_database()
        
        # Initialize navigation buttons list
        self.nav_buttons = []
        
        # Window setup
        self.setWindowTitle("مدارسہ مینجمنٹ سسٹم")
        self.setMinimumSize(1200, 700)
        self.setLayoutDirection(Qt.RightToLeft)
        
        # Setup UI
        self.setup_ui()
        self.apply_styles()
        
        # Set default active page
        self.navigate_to(0)
        
        # Center window on screen
        self.center_window()
    
    def center_window(self):
        """Center the window on the screen."""
        screen = QApplication.primaryScreen()
        if screen:
            screen_geometry = screen.availableGeometry()
            window_geometry = self.frameGeometry()
            center_point = screen_geometry.center()
            window_geometry.moveCenter(center_point)
            self.move(window_geometry.topLeft())
    
    def setup_ui(self):
        """Setup the main UI layout."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create horizontal layout with no margins and spacing
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        sidebar = self.create_sidebar()
        sidebar.setFixedWidth(250)
        
        # Create content area
        content_area = self.create_content_area()
        content_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Add widgets to layout
        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_area)
    
    def create_sidebar(self):
        """Create the sidebar navigation panel."""
        sidebar = QFrame()
        sidebar.setObjectName("sidebar")
        sidebar.setFixedWidth(250)
        sidebar.setLayoutDirection(Qt.RightToLeft)
        
        # Create vertical layout for sidebar
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Logo label at top
        logo_label = QLabel("مدارسہ مینجمنٹ\nسسٹم")
        logo_label.setObjectName("logo_label")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setFont(get_urdu_font(16, bold=True))
        logo_label.setMinimumHeight(80)
        logo_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                background-color: {COLOR_SIDEBAR};
                padding: 20px;
                font-size: 16px;
                font-weight: bold;
            }}
        """)
        sidebar_layout.addWidget(logo_label)
        
        # Add horizontal line separator
        line_separator = QFrame()
        line_separator.setFrameShape(QFrame.HLine)
        line_separator.setStyleSheet(f"background-color: #2D6A4F; height: 1px;")
        sidebar_layout.addWidget(line_separator)
        
        # Add navigation buttons
        self.add_nav_button(sidebar_layout, "🏠 مرکزی صفحہ", 0)
        self.add_nav_button(sidebar_layout, "👨‍🎓 طلباء", 1)
        self.add_nav_button(sidebar_layout, "👥 ملازمین", 2)
        self.add_nav_button(sidebar_layout, "📋 حاضری", 3)
        self.add_nav_button(sidebar_layout, "💰 فیس", 4)
        self.add_nav_button(sidebar_layout, "🤲 عطیات", 5)
        self.add_nav_button(sidebar_layout, "📝 امتحانات", 6)
        self.add_nav_button(sidebar_layout, "📊 رپورٹس", 7)
        
        # Add stretch spacer
        sidebar_layout.addStretch()
        
        # Version label at bottom
        version_label = QLabel("ورژن ۱.۰")
        version_label.setAlignment(Qt.AlignCenter)
        version_label.setFont(get_urdu_font(10))
        version_label.setStyleSheet(f"""
            QLabel {{
                color: white;
                padding: 10px;
                font-size: 10px;
            }}
        """)
        sidebar_layout.addWidget(version_label)
        
        return sidebar
    
    def add_nav_button(self, sidebar_layout, label, index):
        """Add a navigation button to the sidebar."""
        button = QPushButton(label)
        button.setObjectName("nav_btn")
        button.setFont(get_urdu_font(14))
        button.setLayoutDirection(Qt.RightToLeft)
        button.setFixedHeight(50)
        button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Connect clicked signal
        button.clicked.connect(lambda: self.navigate_to(index))
        
        # Add to buttons list and layout
        self.nav_buttons.append(button)
        sidebar_layout.addWidget(button)
    
    def create_content_area(self):
        """Create the main content area with stacked widget."""
        self.content_stack = QStackedWidget()
        
        # Add Dashboard Widget at index 0
        self.dashboard_widget = DashboardWidget()
        self.content_stack.addWidget(self.dashboard_widget)
        
        # Add Students List Widget at index 1
        self.students_widget = StudentList()
        self.content_stack.addWidget(self.students_widget)
        
        # Add Employees List Widget at index 2
        self.employees_widget = EmployeeList()
        self.content_stack.addWidget(self.employees_widget)
        
        # Add Attendance Widget at index 3
        self.attendance_widget = AttendanceWidget()
        self.content_stack.addWidget(self.attendance_widget)
        
        # Create placeholder pages for remaining modules
        page_labels = [
            "Fees - jald aa raha hai",
            "Atiyat - jald aa raha hai",
            "Imtihaanat - jald aa raha hai",
            "Reports - jald aa raha hai"
        ]
        
        for label in page_labels:
            page = QWidget()
            page_layout = QVBoxLayout(page)
            page_layout.setAlignment(Qt.AlignCenter)
            
            page_label = QLabel(label)
            page_label.setAlignment(Qt.AlignCenter)
            page_label.setFont(get_urdu_font(18, bold=True))
            page_label.setStyleSheet(f"color: {COLOR_SIDEBAR};")
            
            page_layout.addWidget(page_label)
            self.content_stack.addWidget(page)
        
        return self.content_stack
    
    def navigate_to(self, index):
        """Navigate to the specified page index."""
        # Refresh dashboard if navigating to index 0
        if index == 0:
            self.dashboard_widget.refresh()
        
        # Set current page
        self.content_stack.setCurrentIndex(index)
        
        # Update button styles
        for i, button in enumerate(self.nav_buttons):
            if i == index:
                button.setProperty("active", "true")
            else:
                button.setProperty("active", "false")
            
            # Refresh button styling
            self.style().unpolish(button)
            self.style().polish(button)
    
    def apply_styles(self):
        """Apply the main stylesheet to the window."""
        self.setStyleSheet(get_main_stylesheet())