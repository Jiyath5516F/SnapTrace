import sys
import os

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for portable exe"""
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    elif hasattr(sys, 'frozen') and sys.frozen:
        # Nuitka, cx_Freeze and other freezers
        base_path = os.path.dirname(sys.executable)
    elif "__compiled__" in globals():
        # Nuitka compiled mode
        base_path = os.path.dirname(os.path.abspath(__file__))
    else:
        # Get the directory where the executable or script is located
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(base_path, relative_path)

def external_data_path(filename):
    """Get absolute path to external data files that should be next to the executable"""
    if hasattr(sys, 'frozen') and sys.frozen:
        # For compiled executable, look next to the .exe file
        base_path = os.path.dirname(sys.executable)
    else:
        # For development, look in the project root
        base_path = os.path.dirname(os.path.abspath(sys.argv[0]))
    return os.path.join(base_path, filename)
