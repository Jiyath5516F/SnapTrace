from PyQt5.QtWidgets import QWidget, QLabel, QRubberBand, QApplication
from PyQt5.QtCore import Qt, QPoint, QRect, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QPainter, QPixmap, QPen

class ScreenshotSelector(QWidget):
    finished = pyqtSignal()  # Signal when screenshot is taken
    cancelled = pyqtSignal()  # Signal when selection is cancelled

    def __init__(self, parent_window=None):
        super().__init__(None)  # Set no parent to avoid inheritance issues
        self.parent_window = parent_window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setStyleSheet('''
            QWidget {
                background-color: transparent;
            }
            QLabel {
                color: white;
                font-size: 16px;
                background-color: transparent;
            }
        ''')
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_DeleteOnClose)
        self.screen = QApplication.primaryScreen()
        self.screen_geometry = self.screen.geometry()
        self.setGeometry(self.screen_geometry)
        self.begin = QPoint()
        self.end = QPoint()
        self.is_selecting = False
        self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
        self.selected_geometry = None
        self.screenshot = None
        self.full_screenshot = None
        self.setCursor(Qt.CrossCursor)
        
        # Hide parent window first
        if self.parent_window:
            self.parent_window.hide()
        
        # Use timer to ensure window is hidden before capture
        QTimer.singleShot(100, self.capture_screen)  # Reduced delay

    def capture_screen(self):
        """Capture the screen and show selector"""
        self.full_screenshot = self.screen.grabWindow(0)
        self.show()
        self.raise_()  # Bring window to front
        self.activateWindow()
        self.setFocus()  # Ensure the window has focus
        
        # Force the window to be on top and active
        self.setWindowState(self.windowState() & ~Qt.WindowMinimized | Qt.WindowActive)
        
        # Add instruction label after showing
        self.label = QLabel("Click and drag to select area (Esc to cancel)", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet('''
            QLabel {
                color: white;
                font-size: 16px;
                background-color: rgba(0, 0, 0, 150);
                border-radius: 5px;
                padding: 5px;
            }
        ''')
        # Position label at the top center
        label_width = 400
        self.label.setFixedWidth(label_width)
        self.label.move((self.width() - label_width) // 2, 50)
        self.label.show()
        
        # Force a repaint to ensure the overlay is visible
        self.repaint()

    def paintEvent(self, event):
        if not self.full_screenshot:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw semi-transparent overlay
        overlay = QColor(0, 0, 0, 100)
        painter.fillRect(self.rect(), overlay)
        
        # Draw the selection area without overlay
        if self.is_selecting and self.rubber_band.isVisible():
            selection = QRect(self.begin, self.end).normalized()
            painter.drawPixmap(selection, self.full_screenshot, selection)
            
            # Draw selection border
            pen = QPen(QColor(0, 120, 212), 2)  # Blue border
            painter.setPen(pen)
            painter.drawRect(selection)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.cancelled.emit()
            self.close()

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.is_selecting = True
        self.rubber_band.setGeometry(QRect(self.begin, self.end))
        self.rubber_band.show()
        self.update()

    def mouseMoveEvent(self, event):
        if self.is_selecting:
            self.end = event.pos()
            self.rubber_band.setGeometry(QRect(self.begin, self.end).normalized())
            self.update()

    def mouseReleaseEvent(self, event):
        self.is_selecting = False
        if self.begin and self.end:
            self.selected_geometry = QRect(self.begin, self.end).normalized()
            if self.selected_geometry.width() > 0 and self.selected_geometry.height() > 0:
                # Take a new screenshot of the selected area
                self.screenshot = self.full_screenshot.copy(self.selected_geometry)
                # Use a timer to emit the signal after a brief delay
                QTimer.singleShot(50, self._emit_finished)
            else:
                self.rubber_band.hide()
                self.update()
    
    def _emit_finished(self):
        """Emit the finished signal and close"""
        self.finished.emit()
        if self.parent_window:
            self.parent_window.show()
        # Close with a slight delay to ensure signal is processed
        QTimer.singleShot(100, self.close)
