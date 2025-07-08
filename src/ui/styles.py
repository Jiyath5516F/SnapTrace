"""
Application styles and themes for SnapTrace
"""

DARK_THEME_STYLESHEET = '''
    /* Main Window */
    QMainWindow {
        background-color: #1a1a1a;
    }
    
    /* General Widget Styling */
    QWidget {
        background-color: #1a1a1a;
        color: #e0e0e0;
        font-family: 'Segoe UI', 'SF Pro Display', 'Roboto', Arial, sans-serif;
        font-size: 13px;
    }
    
    /* Section Separator */
    .section-separator {
        background-color: #333333;
        min-height: 1px;
        margin: 8px 0;
    }
    
    /* Section Labels */
    .section-label {
        color: #0066cc;
        font-size: 15px;
        font-weight: bold;
        font-family: 'Segoe UI Semibold', 'SF Pro Display', 'Roboto Medium', Arial, sans-serif;
        padding: 0 0 8px 0;
    }
    
    /* Tool Size Spinbox */
    #toolSizeSpinner {
        background-color: #2d2d2d;
        border: 1px solid #3d3d3d;
        padding: 4px 8px;
        border-radius: 6px;
        min-width: 80px;
        max-width: 80px;
    }
    #toolSizeSpinner:hover {
        background-color: #3d3d3d;
        border-color: #4d4d4d;
    }
    #toolSizeSpinner:focus {
        border-color: #0066cc;
    }
    
    /* Tool Buttons */
    QPushButton {
        background-color: #2d2d2d;
        border: none;
        padding: 12px;
        border-radius: 8px;
        font-size: 14px;
        color: #e0e0e0;
        min-width: 44px;
        min-height: 44px;
    }
    QPushButton:hover {
        background-color: #3d3d3d;
    }
    QPushButton:pressed {
        background-color: #4d4d4d;
    }
    QPushButton:checked {
        background-color: #0066cc;
        color: white;
    }
    
    /* Reset Button Special Styling */
    #resetButton {
        background-color: #2d2d2d;
        border: 1px solid #3d3d3d;
        color: #e0e0e0;
        transition: all 0.3s;
    }
    #resetButton:hover {
        background-color: #3d3d3d;
        border-color: #4d4d4d;
    }
    #resetButton:pressed {
        background-color: #0066cc;
        border-color: #0077ee;
        color: white;
    }
    
    /* Tool Buttons */
    #toolButton {
        background-color: #2d2d2d;
        border: 1px solid #3d3d3d;
        margin: 3px;
        padding: 10px;
        border-radius: 10px;
        min-width: 48px;
        min-height: 48px;
    }
    #toolButton:hover {
        background-color: #3d3d3d;
        border: 1px solid #4d4d4d;
    }
    #toolButton:checked {
        background-color: #0066cc;
        border: 1px solid #0077ee;
    }
    
    /* Groups */
    #toolGroup {
        background-color: #2d2d2d;
        border-radius: 10px;
        padding: 16px;
        margin: 8px 0;
    }
    
    /* Input Fields */
    QLineEdit {
        background-color: #2d2d2d;
        border: 1px solid #3d3d3d;
        padding: 12px 16px;
        border-radius: 8px;
        color: #e0e0e0;
        font-size: 14px;
        min-height: 42px;
    }
    QLineEdit:focus {
        border: 1px solid #0066cc;
        background-color: #333333;
    }
    
    /* Spinbox */
    QSpinBox {
        background-color: #2d2d2d;
        border: 1px solid #3d3d3d;
        padding: 8px 12px;
        border-radius: 8px;
        color: #e0e0e0;
        font-size: 14px;
        min-width: 120px;
        min-height: 42px;
    }
    QSpinBox:focus {
        border: 1px solid #0066cc;
        background-color: #333333;
    }
    QSpinBox::up-button, QSpinBox::down-button {
        border: none;
        background: #3d3d3d;
        border-radius: 4px;
        margin: 4px;
        width: 24px;
    }
    QSpinBox::up-button:hover, QSpinBox::down-button:hover {
        background: #4d4d4d;
    }
    
    /* Labels */
    QLabel {
        color: #e0e0e0;
        font-size: 13px;
    }
    
    /* List Widget */
    QListWidget {
        background-color: #2d2d2d;
        border: 1px solid #3d3d3d;
        border-radius: 8px;
        padding: 8px;
        min-height: 300px;
    }
    QListWidget::item {
        background-color: #333333;
        padding: 10px 14px;
        border-radius: 6px;
        margin: 3px 4px;
        font-size: 13px;
    }
    QListWidget::item:hover {
        background-color: #3d3d3d;
    }
    QListWidget::item:selected {
        background-color: #0066cc;
        color: white;
    }
    
    /* Scroll Area */
    QScrollArea {
        border: none;
        background-color: #1a1a1a;
    }
    QScrollBar:vertical, QScrollBar:horizontal {
        background-color: #1a1a1a;
        width: 8px;
        height: 8px;
    }
    QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
        background-color: #3d3d3d;
        border-radius: 4px;
        min-height: 30px;
    }
    QScrollBar::handle:hover {
        background-color: #4d4d4d;
    }
    QScrollBar::add-line, QScrollBar::sub-line {
        border: none;
        background: none;
    }
    QScrollBar::add-page, QScrollBar::sub-page {
        background: none;
    }
    
    /* Color Indicator */
    #colorIndicator {
        border: 1px solid #3d3d3d;
        border-radius: 6px;
        min-height: 24px;
    }
    
    /* Author Credit */
    #authorLabel {
        color: #666666;
        font-size: 12px;
        padding: 10px 0;
        qproperty-alignment: 'AlignRight';
    }
    
    /* Save Button */
    #saveButton {
        background-color: #0066cc;
        color: white;
        font-weight: bold;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 14px;
        min-width: 120px;
        min-height: 42px;
        border: 2px solid #0077ee;
    }
    #saveButton:hover {
        background-color: #0077ee;
        border: 2px solid #0088ff;
    }
    #saveButton:pressed {
        background-color: #0055bb;
        border: 2px solid #0066cc;
    }
    
    /* Undo/Redo Buttons */
    #historyButton {
        background-color: #2d2d2d;
        border: 1px solid #3d3d3d;
        padding: 8px;
        border-radius: 8px;
        min-width: 42px;
        min-height: 42px;
    }
    #historyButton:hover {
        background-color: #3d3d3d;
        border: 1px solid #4d4d4d;
    }
    #historyButton:disabled {
        background-color: #252525;
        border: 1px solid #303030;
        opacity: 0.5;
    }
    
    /* Folder Selection */
    #folderGroup {
        background-color: #2d2d2d;
        border-radius: 10px;
        padding: 16px;
        margin: 8px 0;
    }
    
    #folderPath {
        background-color: #333333;
        border: 1px solid #3d3d3d;
        padding: 12px 16px;
        border-radius: 8px;
        color: #888888;
        font-size: 13px;
        min-height: 42px;
    }
    
    #browseButton {
        background-color: #2d2d2d;
        border: 1px solid #3d3d3d;
        padding: 12px;
        border-radius: 8px;
        min-width: 100px;
        min-height: 42px;
    }
    
    #browseButton:hover {
        background-color: #3d3d3d;
        border: 1px solid #4d4d4d;
    }
'''
