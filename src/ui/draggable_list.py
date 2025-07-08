from PyQt5.QtWidgets import QListWidget
from PyQt5.QtCore import Qt, QPoint, QMimeData
from PyQt5.QtGui import QDrag, QFont, QFontMetrics, QPainter, QPixmap

class DraggableListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)
        self.setAcceptDrops(False)
        self.setDefaultDropAction(Qt.CopyAction)
        self.setSelectionMode(QListWidget.SingleSelection)
        self.setDragDropMode(QListWidget.DragOnly)

    def startDrag(self, supportedActions):
        item = self.currentItem()
        if item:
            mimeData = QMimeData()
            mimeData.setText(item.text())
            
            drag = QDrag(self)
            drag.setMimeData(mimeData)
            
            # Create a pixmap for drag feedback
            font = self.font()
            metrics = QFontMetrics(font)
            text_width = metrics.width(item.text())
            text_height = metrics.height()
            
            pixmap = QPixmap(text_width + 8, text_height + 8)
            pixmap.fill(Qt.transparent)
            
            painter = QPainter(pixmap)
            painter.setFont(font)
            painter.setPen(Qt.white)
            painter.drawText(4, text_height, item.text())
            painter.end()
            
            drag.setPixmap(pixmap)
            drag.setHotSpot(QPoint(4, text_height))
            
            drag.exec_(Qt.CopyAction)
