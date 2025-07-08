import os
import csv
from datetime import datetime
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QPushButton, QLabel, QLineEdit, QSpinBox, QScrollArea,
                           QListWidgetItem, QButtonGroup, QGridLayout, QFileDialog,
                           QMessageBox, QFrame, QColorDialog, QApplication)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QFont, QColor, QPen

from ..core.constants import APP_NAME, APP_ICON, DEFECT_CSV, ICONS_DIR, DEFAULT_PEN_SIZE
from .styles import DARK_THEME_STYLESHEET
from .drawing_area import DrawingArea
from .draggable_list import DraggableListWidget
from .screenshot_selector import ScreenshotSelector

class ScreenshotTool(QMainWindow):
    def __init__(self, screenshot=None, geometry=None):
        super().__init__()
        self.screenshot = screenshot
        self.geometry = geometry
        self.current_tool_button = None
        self.save_directory = os.path.expanduser("~")
        
        # Initialize defect_data first - using simple list instead of pandas
        self.defect_data = []
        if os.path.exists(DEFECT_CSV):
            try:
                with open(DEFECT_CSV, 'r', newline='', encoding='utf-8') as csvfile:
                    reader = csv.DictReader(csvfile)
                    self.defect_data = list(reader)
                    # Ensure all entries have both Category and Feedback keys
                    for entry in self.defect_data:
                        if 'Category' not in entry:
                            entry['Category'] = ''
                        if 'Feedback' not in entry:
                            entry['Feedback'] = ''
            except Exception as e:
                QMessageBox.warning(self, "CSV Load Error", f"Error loading defect feedbacks: {str(e)}")
                self.defect_data = []
        
        self.init_icons()
        self.initUI()
        
        # Set window title and icon
        self.setWindowTitle(APP_NAME)
        if os.path.exists(APP_ICON):
            self.setWindowIcon(QIcon(APP_ICON))

    def init_icons(self):
        # Load icons from the icons folder
        self.icons = {
            'rectangle': QIcon(os.path.join(ICONS_DIR, "rectangle.png")),
            'circle': QIcon(os.path.join(ICONS_DIR, "circle.png")),
            'line': QIcon(os.path.join(ICONS_DIR, "line.png")),
            'arrow': QIcon(os.path.join(ICONS_DIR, "arrow.png")),
            'pencil': QIcon(os.path.join(ICONS_DIR, "pencil.png")),
            'text': QIcon(os.path.join(ICONS_DIR, "text.png")),
            'eraser': QIcon(os.path.join(ICONS_DIR, "eraser.png")),
            'image': QIcon(os.path.join(ICONS_DIR, "image.png")),
            'color': QIcon(os.path.join(ICONS_DIR, "color-picker.png")),
            'count': QIcon(os.path.join(ICONS_DIR, "counter.png")),
            'reset': QIcon(os.path.join(ICONS_DIR, "reset.png")),
            'undo': QIcon(os.path.join(ICONS_DIR, "undo.png")),
            'redo': QIcon(os.path.join(ICONS_DIR, "redo.png")),
            'save': QIcon(os.path.join(ICONS_DIR, "save.png")),
            'new': QIcon(os.path.join(ICONS_DIR, "new.png")),
            'paste': QIcon(os.path.join(ICONS_DIR, "paste.png")),
            'folder': QIcon(os.path.join(ICONS_DIR, "folder.png"))
        }
        
        # Create fallback counter icon
        counter_icon = QIcon(os.path.join(ICONS_DIR, "counter.png"))
        if counter_icon.isNull():
            # Create a simple number icon if the image file doesn't exist
            pixmap = QPixmap(64, 64)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw circle
            painter.setPen(QPen(Qt.black, 2))
            painter.setBrush(Qt.white)
            painter.drawEllipse(4, 4, 56, 56)
            
            # Draw number
            font = QFont("Arial", 24, QFont.Bold)
            painter.setFont(font)
            painter.drawText(pixmap.rect(), Qt.AlignCenter, "#")
            painter.end()
            
            counter_icon = QIcon(pixmap)
        
        self.icons['count'] = counter_icon

    def initUI(self):
        # Apply stylesheet
        self.setStyleSheet(DARK_THEME_STYLESHEET)

        # Create main widget and layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)
        
        # Create drawing area with dark background and padding
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        container = QWidget()
        container.setStyleSheet("background-color: #1a1a1a; padding: 24px;")
        container_layout = QVBoxLayout(container)
        container_layout.setAlignment(Qt.AlignCenter)
        
        self.drawing_area = DrawingArea(self.screenshot)
        container_layout.addWidget(self.drawing_area)
        scroll_area.setWidget(container)
        self.layout.addWidget(scroll_area, stretch=4)
        
        # Right sidebar with tools
        self.create_right_panel()
        
        # Window setup
        self.setWindowTitle('SnapTrace')
        self.setGeometry(100, 100, 1400, 900)
        self.setMinimumSize(1000, 700)

    def create_right_panel(self):
        """Create the right panel with all controls"""
        right_panel = QWidget()
        right_panel.setFixedWidth(360)
        right_panel.setStyleSheet("background-color: #262626; padding: 0px;")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setSpacing(4)
        right_layout.setContentsMargins(24, 20, 24, 20)
        
        # Header with save button
        self.create_header(right_layout)
        
        # Add folder selection group
        self.create_folder_selection(right_layout)
        
        # Add separator
        self.add_separator(right_layout)
        
        # File name group
        self.create_filename_input(right_layout)
        
        # Add separator
        self.add_separator(right_layout)
        
        # Drawing tools group
        self.create_drawing_tools(right_layout)
        
        # Counter settings group
        self.create_counter_settings(right_layout)
        
        # Add separator
        self.add_separator(right_layout)
        
        # Quick commands group
        self.create_quick_commands(right_layout)
        
        # Add stretch to push everything up
        right_layout.addStretch()
        
        # Add author credit at the bottom
        author_label = QLabel("by 0x4a4b")
        author_label.setObjectName("authorLabel")
        right_layout.addWidget(author_label)
        
        # Add the right panel to the main layout
        self.layout.addWidget(right_panel)

    def create_header(self, layout):
        """Create header with app name and save button"""
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)
        
        header_label = QLabel("SnapTrace")
        header_label.setStyleSheet("""
            font-size: 22px;
            font-weight: bold;
            color: white;
            padding-bottom: 8px;
        """)
        
        save_btn = QPushButton()
        save_btn.setObjectName("saveButton")
        save_btn.setIcon(self.icons['save'])
        save_btn.setIconSize(QSize(20, 20))
        save_btn.setToolTip("Save Screenshot (Ctrl+S)")
        save_btn.setFixedSize(42, 42)
        save_btn.clicked.connect(self.save_screenshot)
        
        header_layout.addWidget(header_label)
        header_layout.addWidget(save_btn)
        header_layout.addStretch()
        layout.addLayout(header_layout)

    def create_folder_selection(self, layout):
        """Create folder selection group"""
        folder_group = QWidget()
        folder_group.setObjectName("toolGroup")
        folder_layout = QVBoxLayout(folder_group)
        folder_layout.setSpacing(8)
        
        folder_header = QLabel("Save Location")
        folder_header.setProperty("class", "section-label")
        folder_layout.addWidget(folder_header)
        
        folder_input_layout = QHBoxLayout()
        folder_input_layout.setSpacing(10)
        
        self.folder_path_label = QLabel(self.save_directory)
        self.folder_path_label.setObjectName("folderPath")
        self.folder_path_label.setWordWrap(True)
        self.folder_path_label.setMinimumWidth(180)
        
        browse_btn = QPushButton("Browse")
        browse_btn.setObjectName("browseButton")
        browse_btn.setIcon(self.icons['folder'])
        browse_btn.setIconSize(QSize(20, 20))
        browse_btn.clicked.connect(self.browse_save_location)
        
        folder_input_layout.addWidget(self.folder_path_label)
        folder_input_layout.addWidget(browse_btn)
        folder_layout.addLayout(folder_input_layout)
        layout.addWidget(folder_group)

    def create_filename_input(self, layout):
        """Create filename input group"""
        name_group = QWidget()
        name_group.setObjectName("toolGroup")
        name_layout = QVBoxLayout(name_group)
        name_layout.setSpacing(8)
        
        name_header = QLabel("File Name")
        name_header.setProperty("class", "section-label")
        name_layout.addWidget(name_header)
        
        input_layout = QHBoxLayout()
        input_layout.setSpacing(10)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Enter file name")
        
        paste_btn = QPushButton()
        paste_btn.setIcon(self.icons['paste'])
        paste_btn.setIconSize(QSize(20, 20))
        paste_btn.setToolTip("Paste from clipboard")
        paste_btn.setFixedSize(42, 42)
        paste_btn.clicked.connect(self.paste_filename)
        
        input_layout.addWidget(self.name_input)
        input_layout.addWidget(paste_btn)
        
        name_layout.addLayout(input_layout)
        layout.addWidget(name_group)

    def create_drawing_tools(self, layout):
        """Create drawing tools group"""
        tools_group = QWidget()
        tools_group.setObjectName("toolGroup")
        tools_layout = QVBoxLayout(tools_group)
        tools_layout.setSpacing(12)
        
        # Header with tool size
        tools_header_layout = QHBoxLayout()
        tools_header_layout.setSpacing(12)
        
        tools_header = QLabel("Drawing Tools")
        tools_header.setProperty("class", "section-label")
        tools_header_layout.addWidget(tools_header)
        
        size_layout = QHBoxLayout()
        size_label = QLabel("Size:")
        self.size_spinner = QSpinBox()
        self.size_spinner.setObjectName("toolSizeSpinner")
        self.size_spinner.setRange(1, 50)
        self.size_spinner.setValue(DEFAULT_PEN_SIZE)
        self.size_spinner.valueChanged.connect(self.change_pen_size)
        
        size_layout.addWidget(size_label)
        size_layout.addWidget(self.size_spinner)
        tools_header_layout.addLayout(size_layout)
        tools_header_layout.addStretch()
        
        tools_layout.addLayout(tools_header_layout)
        
        tool_grid = QGridLayout()
        tool_grid.setSpacing(8)
        tool_grid.setHorizontalSpacing(10)
        tool_grid.setVerticalSpacing(10)
        self.add_drawing_tools(tool_grid)
        tools_layout.addLayout(tool_grid)
        layout.addWidget(tools_group)

    def create_counter_settings(self, layout):
        """Create counter settings group"""
        self.counter_group = QWidget()  # Store as instance variable
        self.counter_group.setObjectName("toolGroup")
        counter_layout = QHBoxLayout(self.counter_group)
        counter_layout.setSpacing(8)
        
        counter_left_layout = QVBoxLayout()
        counter_left_layout.setSpacing(8)
        
        counter_header = QLabel("Counter Settings")
        counter_header.setProperty("class", "section-label")
        counter_left_layout.addWidget(counter_header)
        
        # Create a horizontal layout for input and reset button
        input_reset_layout = QHBoxLayout()
        input_reset_layout.setSpacing(8)
        
        start_from_label = QLabel("Start From:")
        self.start_from_input = QSpinBox()
        self.start_from_input.setRange(1, 999)
        self.start_from_input.setValue(1)
        self.start_from_input.setObjectName("toolSizeSpinner")
        self.start_from_input.valueChanged.connect(self.update_counter_start)
        
        # Reset counter button with custom icon
        reset_btn = QPushButton()
        reset_btn.setObjectName("resetButton")
        reset_btn.setIcon(self.icons['reset'])
        reset_btn.setIconSize(QSize(24, 24))
        reset_btn.setToolTip("Reset Counter")
        reset_btn.setFixedSize(42, 42)
        reset_btn.clicked.connect(self.reset_counter)
        
        input_reset_layout.addWidget(start_from_label)
        input_reset_layout.addWidget(self.start_from_input)
        input_reset_layout.addWidget(reset_btn)
        input_reset_layout.addStretch()
        
        counter_left_layout.addLayout(input_reset_layout)
        counter_layout.addLayout(counter_left_layout)
        layout.addWidget(self.counter_group)
        
        # Initially hide the counter settings - only show when counter tool is selected
        self.counter_group.hide()

    def create_quick_commands(self, layout):
        """Create quick commands group"""
        commands_group = QWidget()
        commands_group.setObjectName("toolGroup")
        commands_layout = QVBoxLayout(commands_group)
        commands_layout.setSpacing(10)
        
        commands_header = QLabel("Quick Commands")
        commands_header.setProperty("class", "section-label")
        commands_layout.addWidget(commands_header)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to search commands...")
        self.search_input.textChanged.connect(self.filter_commands)
        commands_layout.addWidget(self.search_input)
        
        self.feedback_list = DraggableListWidget()
        self.feedback_list.setMinimumHeight(200)
        self.populate_defect_list()
        commands_layout.addWidget(self.feedback_list)
        layout.addWidget(commands_group)

    def add_separator(self, layout):
        """Add a visual separator"""
        separator = QFrame()
        separator.setProperty("class", "section-separator")
        separator.setFrameShape(QFrame.HLine)
        separator.setContentsMargins(0, 4, 0, 4)
        layout.addWidget(separator)

    def filter_commands(self, text):
        """Filter the commands list based on search text"""
        search_terms = text.lower().split()
        for i in range(self.feedback_list.count()):
            item = self.feedback_list.item(i)
            item_text = item.text().lower()
            # Show item if all search terms are found in the item text
            should_show = all(term in item_text for term in search_terms)
            item.setHidden(not should_show)

    def add_drawing_tools(self, grid_layout):
        tools = [
            ("new", "New Screenshot (Ctrl+N)"),
            ("rectangle", "Rectangle (R)"),
            ("circle", "Circle (C)"),
            ("line", "Line (L)"),
            ("arrow", "Arrow (A)"),
            ("pencil", "Pencil (P)"),
            ("text", "Text (T)"),
            ("eraser", "Eraser (E)"),
            ("image", "Add Image (I)"),
            ("color", "Color Picker (K)"),
            ("count", "Counter (#)"),
            ("undo", "Undo (Ctrl+Z)"),
            ("redo", "Redo (Ctrl+Y)")
        ]
        
        tool_group = QButtonGroup(self)
        row = 0
        col = 0
        for tool_id, tooltip in tools:
            btn = QPushButton()
            btn.setObjectName("toolButton")
            btn.setIcon(self.icons[tool_id])
            btn.setIconSize(QSize(24, 24))
            btn.setToolTip(tooltip)
            btn.setFixedSize(48, 48)
            
            # Set button behavior based on tool type
            if tool_id == "new":
                btn.clicked.connect(self.take_new_screenshot)
            elif tool_id == "image":
                btn.clicked.connect(self.import_image)
            elif tool_id == "color":
                btn.clicked.connect(self.choose_color)
                btn.setCheckable(False)
            elif tool_id == "undo":
                btn.clicked.connect(self.drawing_area.undo)
                btn.setCheckable(False)
            elif tool_id == "redo":
                btn.clicked.connect(self.drawing_area.redo)
                btn.setCheckable(False)
            else:
                btn.clicked.connect(lambda checked, t=tool_id, b=btn: self.set_tool(t, b))
                btn.setProperty("tool", tool_id)
                btn.setCheckable(True)
                tool_group.addButton(btn)
            
            grid_layout.addWidget(btn, row, col, Qt.AlignCenter)
            col += 1
            if col > 3:  # 4 buttons per row
                col = 0
                row += 1

    def import_image(self):
        """Open file dialog to import an image"""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Import Image", "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*)"
        )
        if file_name:
            self.drawing_area.add_image(file_name)

    def update_color_indicator(self):
        self.drawing_area.current_color = self.drawing_area.current_color

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.drawing_area.current_color = color
            self.update_color_indicator()

    def set_tool(self, tool, button):
        # Auto-save any current text before switching tools
        if hasattr(self.drawing_area, 'is_typing') and self.drawing_area.is_typing:
            self.drawing_area.stop_text_editing()
            
        if self.current_tool_button and self.current_tool_button != button:
            self.current_tool_button.setChecked(False)
        self.current_tool_button = button
        self.drawing_area.current_tool = tool
        
        # Reset text tool ready state when switching tools
        if hasattr(self.drawing_area, 'text_tool_ready'):
            self.drawing_area.text_tool_ready = True
            
        # Show/hide counter settings based on selected tool
        if hasattr(self, 'counter_group'):
            if tool == 'count':
                self.counter_group.show()
            else:
                self.counter_group.hide()
        
    def change_pen_size(self, size):
        """Update pen size and font size for text tool"""
        self.drawing_area.pen_size = size
        # Update font size for text tool
        self.drawing_area.current_text_font = QFont("Arial", size + 10)  # Base font size + pen size

    def save_screenshot(self):
        if not self.screenshot:
            return
            
        base_name = self.name_input.text()
        if not base_name:
            base_name = "screenshot"
            
        # Handle file naming with incrementing numbers
        index = 0
        while True:
            suffix = f"_{index}" if index > 0 else ""
            filename = os.path.join(self.save_directory, f"{base_name}{suffix}.png")
            if not os.path.exists(filename):
                break
            index += 1
            
        # Create a new pixmap with the drawings
        final_image = QPixmap(self.drawing_area.size())
        final_image.fill(Qt.transparent)
        painter = QPainter(final_image)
        self.drawing_area.render(painter)
        painter.end()
        
        try:
            if final_image.save(filename):
                # Show success message
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Information)
                msg.setWindowTitle("Success")
                msg.setText(f"Screenshot saved successfully as:\n{filename}")
                msg.setStandardButtons(QMessageBox.Ok)
                msg.exec_()
            else:
                raise Exception("Failed to save image")
        except Exception as e:
            # Show error message
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText(f"Failed to save screenshot:\n{str(e)}")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

    def take_new_screenshot(self):
        """Show screen selection overlay"""
        # Create and show the screenshot selector with reference to this window
        self.hide()  # Hide main window first
        QTimer.singleShot(100, self.start_new_screenshot)

    def start_new_screenshot(self):
        """Start the new screenshot process after window is hidden"""
        self.selector = ScreenshotSelector(parent_window=self)
        self.selector.finished.connect(self.handle_new_selection)
        self.selector.cancelled.connect(self.handle_selection_cancelled)
        self.selector.showFullScreen()

    def handle_new_selection(self):
        """Handle new area selection"""
        if self.selector.screenshot is not None:
            self.screenshot = self.selector.screenshot
            self.geometry = self.selector.selected_geometry
            self.drawing_area.screenshot = self.selector.screenshot
            self.drawing_area.setMinimumSize(self.selector.screenshot.size())
            
            # Clear any existing drawings
            self.drawing_area.drawings = []
            self.drawing_area.text_items = []
            self.drawing_area.undo_stack = []
            self.drawing_area.redo_stack = []
            
            # Reset and suggest filename
            self.name_input.clear()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.name_input.setText(f"screenshot_{timestamp}")
            
            # Fit to viewport and update
            self.drawing_area.fit_to_viewport()
            self.drawing_area.update()
        
        self.show()
        self.activateWindow()

    def handle_selection_cancelled(self):
        """Handle when selection is cancelled"""
        self.show()
        self.activateWindow()

    def paste_filename(self):
        """Paste clipboard text into filename input"""
        clipboard = QApplication.clipboard()
        self.name_input.setText(clipboard.text())

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts"""
        if event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_N:
                self.take_new_screenshot()
            elif event.key() == Qt.Key_S:
                self.save_screenshot()
        else:
            # Tool shortcuts
            key_tool_map = {
                Qt.Key_R: "rectangle",
                Qt.Key_C: "circle",
                Qt.Key_L: "line",
                Qt.Key_A: "arrow",
                Qt.Key_P: "pencil",
                Qt.Key_T: "text",
                Qt.Key_E: "eraser",
                Qt.Key_I: "image",
                Qt.Key_K: "color",
                Qt.Key_NumberSign: "count"  # Add shortcut for counter tool
            }
            if event.key() in key_tool_map:
                tool = key_tool_map[event.key()]
                if tool == "color":
                    self.choose_color()
                elif tool == "image":
                    self.import_image()
                else:
                    # Find and click the corresponding tool button
                    for btn in self.findChildren(QPushButton):
                        if btn.property("tool") == tool:
                            btn.click()
                            break

    def browse_save_location(self):
        """Open folder dialog to select save location"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Save Location",
            self.save_directory,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )
        if folder:
            self.save_directory = folder
            # Update display path - show only last 40 chars with ellipsis if too long
            display_path = self.save_directory
            if len(display_path) > 40:
                display_path = "..." + display_path[-37:]
            self.folder_path_label.setText(display_path)
            self.folder_path_label.setToolTip(self.save_directory)

    def update_counter_start(self, value):
        """Update the counter start value"""
        self.drawing_area.set_counter_start(value)

    def reset_counter(self):
        """Reset the counter to the start value"""
        self.drawing_area.reset_counter()

    def populate_defect_list(self):
        """Populate the defect list from the defect_data list"""
        self.feedback_list.clear()  # Clear existing items first
        for row in self.defect_data:
            feedback_text = row.get('Feedback', '')
            if row.get('Category'):
                feedback_text = f"{row['Category']}: {feedback_text}"
            item = QListWidgetItem(feedback_text)
            item.setFlags(item.flags() | Qt.ItemIsDragEnabled)
            self.feedback_list.addItem(item)

