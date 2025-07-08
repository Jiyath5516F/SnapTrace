#!/usr/bin/env python3
"""
SnapTrace - QA Screenshot Tool
Main entry point for the application with system tray support
"""

import sys
import os

# Add the current directory to Python path for imports
if getattr(sys, 'frozen', False):
    # Running as compiled executable
    current_dir = os.path.dirname(sys.executable)
else:
    # Running as script
    current_dir = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(0, current_dir)

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from src.system_tray import SystemTrayManager

def main():
    """Main application entry point with system tray support"""
    # Create QApplication with proper attributes for system tray
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)  # Keep running when windows are closed
    
    # Set application properties
    app.setApplicationName("SnapTrace")
    app.setApplicationVersion("2.0")
    app.setOrganizationName("SnapTrace")
    
    # Set application icon
    icon_path = "assets/logo.ico"
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    
    # Check if system tray is available
    try:
        from PyQt5.QtWidgets import QSystemTrayIcon
        if not QSystemTrayIcon.isSystemTrayAvailable():
            QMessageBox.critical(None, "System Tray", 
                               "System tray is not available on this system.\n"
                               "SnapTrace requires system tray support to run in the background.")
            return 1
    except Exception as e:
        print(f"Error checking system tray availability: {e}")
        return 1
    
    # Initialize system tray manager
    try:
        tray_manager = SystemTrayManager(app)
        print("SnapTrace started successfully!")
        print("The application is now running in the system tray.")
        print("Press Ctrl+Alt+S to take a screenshot from anywhere!")
        
        # Run the application
        return app.exec_()
        
    except Exception as e:
        QMessageBox.critical(None, "Startup Error", 
                           f"Failed to initialize SnapTrace:\n{str(e)}")
        print(f"Error starting SnapTrace: {e}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
