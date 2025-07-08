"""
System Tray Manager for SnapTrace
Handles system tray functionality, global hotkeys, and application lifecycle
"""

import sys
import os
import threading
from PyQt5.QtWidgets import (QSystemTrayIcon, QMenu, QAction, QActionGroup,
                            QApplication, QMessageBox, QDialog, QVBoxLayout, 
                            QLabel, QPushButton, QHBoxLayout, QTextEdit, QWidget)
from PyQt5.QtGui import QIcon, QPixmap, QCursor
from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QThread, Qt
from .ui.screenshot_selector import ScreenshotSelector
from .ui.main_window import ScreenshotTool

try:
    import keyboard
    KEYBOARD_AVAILABLE = True
except ImportError:
    KEYBOARD_AVAILABLE = False
    print("Warning: keyboard library not available. Global hotkey will not work.")

class HotkeyThread(QThread):
    """Thread for handling global hotkey detection"""
    screenshot_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.hotkey = 'ctrl+alt+s'  # Changed to Ctrl+Alt+S
        self.running = False
    
    def run(self):
        """Run the hotkey listener in a separate thread"""
        if not KEYBOARD_AVAILABLE:
            print("Keyboard library not available, hotkey thread not started")
            return
            
        self.running = True
        try:
            # Register the hotkey
            keyboard.add_hotkey(self.hotkey, self._on_hotkey_pressed)
            print(f"Global hotkey registered: {self.hotkey}")
            
            # Keep the thread alive
            while self.running:
                keyboard.wait()
                
        except Exception as e:
            print(f"Error in hotkey thread: {e}")
    
    def _on_hotkey_pressed(self):
        """Called when the global hotkey is pressed"""
        if self.running:
            self.screenshot_requested.emit()
    
    def stop(self):
        """Stop the hotkey listener"""
        self.running = False
        if KEYBOARD_AVAILABLE:
            try:
                keyboard.unhook_all()
            except:
                pass
        self.quit()
        self.wait()

class SystemTrayManager(QWidget):
    """Manages system tray functionality and global shortcuts"""
    
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.hide()  # Keep the widget hidden - it's just for menu parenting
        self.tray_icon = None
        self.screenshot_selector = None
        self.main_window = None
        self.hotkey_thread = None
        self.context_menu = None
        
        # Color options for quick access
        self.colors = [
            ('Red', '#FF0000'),
            ('Green', '#00FF00'),
            ('Blue', '#0000FF'),
            ('Yellow', '#FFFF00'),
            ('Orange', '#FF7F00'),
            ('Purple', '#8000FF'),
            ('Pink', '#FF007F'),
            ('Cyan', '#00FFFF'),
            ('White', '#FFFFFF'),
            ('Black', '#000000')
        ]
        self.current_color = '#FF0000'  # Default red
        
        self.setup_tray_icon()
        self.setup_hotkey()
    
    def setup_tray_icon(self):
        """Setup the system tray icon and menu"""
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "System Tray", 
                               "System tray is not available on this system.")
            sys.exit(1)
        
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self)  # Set parent to self
        
        # Set icon (use the logo.ico if available)
        icon_path = "assets/logo.ico"
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            # Create a simple icon if logo.ico is not found
            pixmap = QPixmap(16, 16)
            pixmap.fill()
            self.tray_icon.setIcon(QIcon(pixmap))
        
        # Create context menu - use self (QWidget) as parent for proper ownership
        self.context_menu = QMenu(self)
        print("Creating system tray context menu...")
        
        # NEW SCREENSHOT action (make it prominent)
        new_screenshot_action = QAction("📸 New Screenshot", self)
        new_screenshot_action.triggered.connect(self.take_screenshot)
        new_screenshot_action.setToolTip("Take a new screenshot (Ctrl+Alt+S)")
        self.context_menu.addAction(new_screenshot_action)
        print("Added New Screenshot action")
        
        self.context_menu.addSeparator()
        
        # Color submenu - create with proper parent
        color_menu = QMenu("🎨 Drawing Color", self.context_menu)
        color_group = QActionGroup(self)  # Use self as parent for action group
        
        for color_name, color_value in self.colors:
            color_action = QAction(f"● {color_name}", self)
            color_action.setCheckable(True)
            color_action.setData(color_value)
            if color_value == self.current_color:
                color_action.setChecked(True)
            color_action.triggered.connect(lambda checked, c=color_value: self.set_color(c))
            color_group.addAction(color_action)
            color_menu.addAction(color_action)
        
        self.context_menu.addMenu(color_menu)
        print("Added Drawing Color submenu")
        
        self.context_menu.addSeparator()
        
        # Settings action
        settings_action = QAction("⚙️ Settings", self)
        settings_action.triggered.connect(self.show_settings)
        self.context_menu.addAction(settings_action)
        print("Added Settings action")
        
        # Help action
        help_action = QAction("❓ Help", self)
        help_action.triggered.connect(self.show_help)
        self.context_menu.addAction(help_action)
        print("Added Help action")
        
        self.context_menu.addSeparator()
        
        # QUIT action (make it prominent)
        quit_action = QAction("❌ Quit SnapTrace", self)
        quit_action.triggered.connect(self.exit_application)
        quit_action.setToolTip("Exit the application")
        self.context_menu.addAction(quit_action)
        print("Added Quit action")
        
        # Set the menu on the tray icon
        self.tray_icon.setContextMenu(self.context_menu)
        print(f"Context menu set with {len(self.context_menu.actions())} actions")
        
        # Connect activation signal for debugging only - let Qt handle context menu automatically
        self.tray_icon.activated.connect(self.on_tray_activated)
        
        # Set tooltip
        self.tray_icon.setToolTip("SnapTrace - QA Screenshot Tool\nCtrl+Alt+S to take screenshot")
        
        # Show the tray icon
        self.tray_icon.show()
        
        # Show startup message
        if self.tray_icon.supportsMessages():
            self.tray_icon.showMessage(
                "SnapTrace Started",
                "SnapTrace is now running in the system tray.\nPress Ctrl+Alt+S to take a screenshot.",
                QSystemTrayIcon.Information,
                3000
            )
        
        # Windows-specific: Add fallback manual context menu handling
        # Some Windows systems may need manual menu popup
        self.manual_menu_fallback = False
    
    def test_context_menu_support(self):
        """Test if automatic context menu works, enable fallback if needed"""
        # This is called after a delay to test context menu support
        # If users report menu issues, we can enable manual fallback
        print("Context menu support test completed")
    
    def show_context_menu_manually(self):
        """Manually show context menu as fallback"""
        if self.context_menu:
            # Show menu at current cursor position
            self.context_menu.exec_(QCursor.pos())
            print("Context menu shown manually")
    
    def setup_hotkey(self):
        """Setup global hotkey listener"""
        if KEYBOARD_AVAILABLE:
            self.hotkey_thread = HotkeyThread()
            self.hotkey_thread.screenshot_requested.connect(self.take_screenshot)
            self.hotkey_thread.start()
        else:
            print("Global hotkey not available - keyboard library not installed")
    
    def on_tray_activated(self, reason):
        """Handle tray icon activation"""
        print(f"Tray icon activated with reason: {reason}")
        if reason == QSystemTrayIcon.DoubleClick:
            print("Double-click detected - taking screenshot")
            self.take_screenshot()
        elif reason == QSystemTrayIcon.Context:
            print("Right-click detected - Qt will show context menu automatically")
            # Qt should handle context menu automatically via setContextMenu()
            # If users report issues, we can enable manual fallback
            if self.manual_menu_fallback:
                QTimer.singleShot(100, self.show_context_menu_manually)
        elif reason == QSystemTrayIcon.Trigger:
            print("Single click detected")
        elif reason == QSystemTrayIcon.MiddleClick:
            print("Middle click detected")
    
    def take_screenshot(self):
        """Trigger screenshot capture"""
        print("Taking screenshot via system tray...")
        
        # Hide any existing windows first
        if self.main_window:
            self.main_window.hide()
        
        # Create new screenshot selector
        self.screenshot_selector = ScreenshotSelector()
        
        # Connect signals
        self.screenshot_selector.finished.connect(self.on_screenshot_finished)
        self.screenshot_selector.cancelled.connect(self.on_screenshot_cancelled)
        
        # Show the selector
        self.screenshot_selector.showFullScreen()
        self.screenshot_selector.raise_()
        self.screenshot_selector.activateWindow()
        
        # Brief delay to ensure selector is ready
        QTimer.singleShot(100, lambda: self.screenshot_selector.activateWindow())
    
    def on_screenshot_finished(self):
        """Handle when screenshot is taken"""
        if self.screenshot_selector and self.screenshot_selector.screenshot is not None:
            print("Screenshot captured, creating main window...")
            
            # Hide the selector
            self.screenshot_selector.hide()
            
            # Create and show the editing tool
            self.main_window = ScreenshotTool(
                self.screenshot_selector.screenshot, 
                self.screenshot_selector.selected_geometry
            )
            
            # Set the current color in the main window
            if hasattr(self.main_window, 'drawing_area'):
                from PyQt5.QtGui import QColor
                self.main_window.drawing_area.current_color = QColor(self.current_color)
            
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()
            
            print("Main window should be visible now")
        
        # Clean up selector
        if self.screenshot_selector:
            self.screenshot_selector.deleteLater()
            self.screenshot_selector = None
    
    def on_screenshot_cancelled(self):
        """Handle when screenshot is cancelled"""
        print("Screenshot cancelled")
        
        # Clean up selector
        if self.screenshot_selector:
            self.screenshot_selector.deleteLater()
            self.screenshot_selector = None
    
    def set_color(self, color_value):
        """Set the current drawing color"""
        self.current_color = color_value
        print(f"Color changed to: {color_value}")
        
        # Update main window if it exists
        if self.main_window and hasattr(self.main_window, 'drawing_area'):
            from PyQt5.QtGui import QColor
            self.main_window.drawing_area.current_color = QColor(color_value)
        
        # Show notification
        if self.tray_icon.supportsMessages():
            color_name = next((name for name, value in self.colors if value == color_value), "Custom")
            self.tray_icon.showMessage(
                "Color Changed",
                f"Drawing color set to {color_name}",
                QSystemTrayIcon.Information,
                1000
            )
    
    def show_settings(self):
        """Show settings dialog"""
        dialog = QDialog()
        dialog.setWindowTitle("SnapTrace Settings")
        dialog.setFixedSize(300, 200)
        
        layout = QVBoxLayout()
        
        # Hotkey info
        hotkey_label = QLabel(f"Global Hotkey: Ctrl+Alt+S")
        hotkey_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(hotkey_label)
        
        # Status info
        status_text = "Status: Running in system tray"
        if KEYBOARD_AVAILABLE:
            status_text += "\nGlobal hotkey: Active"
        else:
            status_text += "\nGlobal hotkey: Not available"
        
        status_label = QLabel(status_text)
        layout.addWidget(status_label)
        
        # Instructions
        instructions = QLabel(
            "Instructions:\n"
            "• Double-click tray icon to take screenshot\n"
            "• Use Ctrl+Alt+S from anywhere\n"
            "• Right-click tray icon for options"
        )
        layout.addWidget(instructions)
        
        # Close button
        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.close)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def show_help(self):
        """Show help dialog"""
        dialog = QDialog()
        dialog.setWindowTitle("SnapTrace Help")
        dialog.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        help_text = """
<h3>SnapTrace - QA Screenshot Tool</h3>

<b>Taking Screenshots:</b>
• Press Ctrl+Alt+S from anywhere
• Double-click the system tray icon
• Right-click tray icon → New Screenshot

<b>Drawing Tools:</b>
• R - Rectangle
• C - Circle  
• A - Arrow
• L - Line
• P - Pencil
• T - Text
• E - Eraser
• N - Counter

<b>Mouse Controls:</b>
• Left-click: Draw/Create
• Right-click: Select and move elements
• Right-drag: Move selected elements
• Middle-click drag: Pan view
• Ctrl+Wheel: Zoom

<b>Keyboard Shortcuts:</b>
• Ctrl+Z: Undo
• Ctrl+Y: Redo
• Delete: Delete selected item
• Escape: Clear selection/Cancel
• Enter: Finish text editing

<b>System Tray:</b>
• Right-click for color options
• Change drawing colors on-the-fly
• Exit application
        """
        
        help_display = QTextEdit()
        help_display.setHtml(help_text)
        help_display.setReadOnly(True)
        layout.addWidget(help_display)
        
        # Close button
        button_layout = QHBoxLayout()
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.close)
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec_()
    
    def exit_application(self):
        """Exit the application"""
        print("Exiting SnapTrace...")
        
        # Stop hotkey thread first
        if self.hotkey_thread:
            self.hotkey_thread.stop()
        
        # Hide tray icon
        if self.tray_icon:
            self.tray_icon.hide()
        
        # Close any open windows
        if self.main_window:
            self.main_window.close()
        
        if self.screenshot_selector:
            self.screenshot_selector.close()
        
        # Force quit the application
        self.app.quit()
        
        # If quit() doesn't work, force exit
        import sys
        sys.exit(0)
    
    def enable_manual_menu_fallback(self):
        """Enable manual context menu fallback for problematic systems"""
        self.manual_menu_fallback = True
        print("Manual context menu fallback enabled")
        if self.tray_icon.supportsMessages():
            self.tray_icon.showMessage(
                "Menu Fallback",
                "Manual context menu fallback enabled",
                QSystemTrayIcon.Information,
                2000
            )
