from math import cos, sin, atan2, pi
from PyQt5.QtWidgets import QWidget, QScrollArea
from PyQt5.QtCore import Qt, QPoint, QRect, QTimer
from PyQt5.QtGui import (QColor, QPainter, QPixmap, QPen, QPainterPath,
                        QFont, QFontMetrics, QBrush)
from ..core.constants import DEFAULT_PEN_SIZE, MAX_UNDO_STATES, DEFAULT_FONT_SIZE

class DrawingArea(QWidget):
    def __init__(self, screenshot, parent=None):
        super().__init__(parent)
        self.screenshot = screenshot
        self.setMinimumSize(screenshot.size())
        self.setAcceptDrops(True)
        self.begin = QPoint()
        self.end = QPoint()
        self.is_drawing = False
        self.current_tool = "rectangle"
        self.current_color = QColor(Qt.red)
        self.pen_size = DEFAULT_PEN_SIZE
        self.current_text_font = QFont("Arial", DEFAULT_FONT_SIZE)  # Base font size
        self.drawings = []
        self.selected_shape_index = None
        self.selected_text_index = None
        self.selected_counter_index = None
        self.resize_handle = None
        self.is_resizing = False
        self.is_moving = False
        self.is_right_dragging = False
        self.right_drag_start = None
        self.last_drag_pos = None  # Track last position for incremental movement
        self.move_start = None
        self.move_offset = None
        self.viewport_offset = QPoint(0, 0)
        self.is_panning = False
        self.pan_start = None
        self.zoom_level = 1.0
        self.min_pen_width = 1
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo_states = MAX_UNDO_STATES
        self.text_items = []
        self.current_text = ""
        self.text_position = None
        self.is_typing = False
        self.editing_text_index = None
        self.text_cursor_pos = 0
        self.counter_value = 1
        self.counter_start = 1
        self.counter_items = []
        self.pencil_points = []  # Initialize pencil points
        self.setFocusPolicy(Qt.StrongFocus)
        self.setMouseTracking(True)
        
        # Text editing improvements
        self.cursor_blink_timer = QTimer()
        self.cursor_blink_timer.timeout.connect(self.toggle_cursor_visibility)
        self.cursor_visible = True
        self.text_editing_background = True  # Show background when editing text
        self.text_tool_ready = True  # Track if text tool is ready for new text creation
        
        self.add_to_undo_stack()

        # Add viewport fitting
        self.fit_to_viewport()

    def fit_to_viewport(self):
        """Fit the image to the viewport while maintaining aspect ratio"""
        if not self.screenshot:
            return

        # Get the viewport size (parent widget size)
        if self.parent() and isinstance(self.parent(), QScrollArea):
            viewport_size = self.parent().viewport().size()
            if viewport_size.isEmpty():
                return

            # Calculate scaling factors
            scale_w = viewport_size.width() / self.screenshot.width()
            scale_h = viewport_size.height() / self.screenshot.height()
            
            # Use the smaller scaling factor to fit within viewport
            self.zoom_level = min(scale_w, scale_h, 1.0)  # Don't zoom in past 100%
            
            # Center the image in viewport
            self.viewport_offset = QPoint(
                max(0, (viewport_size.width() - self.screenshot.width() * self.zoom_level) // 2),
                max(0, (viewport_size.height() - self.screenshot.height() * self.zoom_level) // 2)
            )
            
            self.update()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.fit_to_viewport()

    def get_scaled_pen_width(self, original_width):
        # Ensure pen width is never less than 1 pixel and is always an integer
        scaled_width = max(self.min_pen_width, int(round(original_width / self.zoom_level)))
        return scaled_width

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Apply viewport transformation
        painter.translate(self.viewport_offset)
        painter.scale(self.zoom_level, self.zoom_level)
        
        # Draw screenshot
        painter.drawPixmap(0, 0, self.screenshot)
        
        # Draw all saved drawings
        for i, drawing in enumerate(self.drawings):
            if len(drawing) == 5:  # Image drawing
                tool, _, points, _, image = drawing
                if tool == "image":
                    rect = QRect(points[0], points[1]).normalized()
                    painter.drawPixmap(rect, image)
            else:  # Regular drawing
                tool, color, points, size = drawing
                pen = QPen(color)
                pen.setWidth(self.get_scaled_pen_width(size))
                painter.setPen(pen)
                
                if tool == "rectangle":
                    painter.drawRect(QRect(points[0], points[1]).normalized())
                elif tool == "circle":
                    painter.drawEllipse(QRect(points[0], points[1]).normalized())
                elif tool == "arrow":
                    self.draw_arrow(painter, points[0], points[1])
                elif tool == "line":
                    painter.drawLine(points[0], points[1])
                elif tool == "pencil":
                    if len(points) > 1:
                        path = QPainterPath()
                        path.moveTo(points[0])
                        for point in points[1:]:
                            path.lineTo(point)
                        painter.drawPath(path)
        
        # Draw counter items with highlight
        for i, counter_item in enumerate(self.counter_items):
            if len(counter_item) == 4:  # New format with size
                number, pos, color, size = counter_item
            else:  # Old format without size (backward compatibility)
                number, pos, color = counter_item
                size = 2  # Default size for old counters
            
            # Draw highlight circle with stored size
            highlight_color = QColor(color)
            highlight_color.setAlpha(50)
            painter.setBrush(highlight_color)
            painter.setPen(Qt.NoPen)
            highlight_radius = 10 + size  # Use stored size
            painter.drawEllipse(pos, highlight_radius, highlight_radius)
            
            # Draw number with stored font size
            painter.setPen(QPen(color))
            font = QFont("Arial", size + 10, QFont.Bold)  # Use stored size
            painter.setFont(font)
            painter.drawText(QRect(pos.x() - highlight_radius, pos.y() - highlight_radius,
                                 highlight_radius * 2, highlight_radius * 2),
                           Qt.AlignCenter, str(number))
            
            # Draw selection feedback for selected counter
            if self.selected_counter_index == i:
                self.draw_counter_selection(painter, pos, highlight_radius)
        
        # Draw text items
        for i, text_item in enumerate(self.text_items):
            if isinstance(text_item, dict):
                painter.setPen(QPen(text_item['color']))
                painter.setFont(text_item['font'])
                
                # Handle multi-line text
                text = text_item['text']
                pos = text_item['pos']
                
                if '\n' in text:
                    lines = text.split('\n')
                    metrics = QFontMetrics(text_item['font'])
                    line_height = metrics.height()
                    
                    for i_line, line in enumerate(lines):
                        line_pos = QPoint(pos.x(), pos.y() + (i_line * line_height))
                        painter.drawText(line_pos, line)
                else:
                    painter.drawText(pos, text)
                    
                # Draw selection feedback for selected text
                if self.selected_text_index == i:
                    self.draw_text_selection(painter, text_item)
                    
            else:  # Backward compatibility for old format
                painter.setPen(QPen(text_item[2]))
                # Use a default font size for old text items instead of current pen_size
                painter.setFont(QFont("Arial", 12))  # Fixed default font size
                painter.drawText(text_item[1], text_item[0])
        
        # Draw current text if typing
        if self.is_typing and self.text_position:
            painter.setPen(QPen(self.current_color))
            painter.setFont(self.current_text_font)
            
            # Calculate text metrics for better positioning
            metrics = QFontMetrics(self.current_text_font)
            text_height = metrics.height()
            
            # Draw background box for better readability
            if self.text_editing_background:
                text_width = metrics.width(self.current_text) if self.current_text else 100
                padding = 4
                bg_rect = QRect(
                    self.text_position.x() - padding,
                    self.text_position.y() - text_height - padding,
                    text_width + padding * 2,
                    text_height + padding * 2
                )
                
                # Semi-transparent background
                painter.fillRect(bg_rect, QColor(0, 0, 0, 100))
                painter.setPen(QPen(QColor(255, 255, 255, 100)))
                painter.drawRect(bg_rect)
            
            # Draw the text
            painter.setPen(QPen(self.current_color))
            if self.current_text:
                painter.drawText(self.text_position, self.current_text)
            
            # Draw blinking cursor
            if self.cursor_visible:
                cursor_x = self.text_position.x()
                if self.current_text:
                    text_before_cursor = self.current_text[:self.text_cursor_pos]
                    cursor_x += metrics.width(text_before_cursor)
                
                # Draw cursor line
                cursor_pen = QPen(self.current_color)
                cursor_pen.setWidth(2)
                painter.setPen(cursor_pen)
                painter.drawLine(
                    cursor_x, self.text_position.y() - text_height + 2,
                    cursor_x, self.text_position.y() + 2
                )
        
        # Draw current drawing
        if self.is_drawing:
            pen = QPen(self.current_color)
            pen.setWidth(self.get_scaled_pen_width(self.pen_size))
            painter.setPen(pen)
            
            if self.current_tool == "rectangle":
                painter.drawRect(QRect(self.begin, self.end).normalized())
            elif self.current_tool == "circle":
                painter.drawEllipse(QRect(self.begin, self.end).normalized())
            elif self.current_tool == "arrow":
                self.draw_arrow(painter, self.begin, self.end)
            elif self.current_tool == "line":
                painter.drawLine(self.begin, self.end)
            elif self.current_tool == "pencil":
                if len(self.pencil_points) > 1:
                    path = QPainterPath()
                    path.moveTo(self.pencil_points[0])
                    for point in self.pencil_points[1:]:
                        path.lineTo(point)
                    painter.drawPath(path)

        # Draw selection handles for selected shape
        if self.selected_shape_index is not None and self.selected_shape_index < len(self.drawings):
            self.draw_selection_handles(painter, self.drawings[self.selected_shape_index])

    def draw_selection_handles(self, painter, drawing):
        """Draw selection feedback with dashed outline and resize handles"""
        # Save current pen and brush
        old_pen = painter.pen()
        old_brush = painter.brush()
        
        # Create dashed pen for selection outline
        selection_pen = QPen(QColor(0, 150, 255), 2)  # Brighter blue
        selection_pen.setStyle(Qt.DashLine)
        selection_pen.setCosmetic(True)  # Don't scale with zoom
        selection_pen.setDashPattern([5, 3])  # Custom dash pattern for better visibility
        painter.setPen(selection_pen)
        painter.setBrush(Qt.NoBrush)
        
        # Get the shape bounds
        if len(drawing) == 5:  # Image
            tool, _, points, _, _ = drawing
            rect = QRect(points[0], points[1]).normalized()
        else:
            tool, _, points, _ = drawing
            if tool in ["rectangle", "circle", "arrow", "line"]:
                rect = QRect(points[0], points[1]).normalized()
            elif tool == "pencil":
                # For pencil, create bounding rectangle
                if points:
                    min_x = min(p.x() for p in points)
                    max_x = max(p.x() for p in points)
                    min_y = min(p.y() for p in points)
                    max_y = max(p.y() for p in points)
                    padding = 5
                    rect = QRect(min_x - padding, min_y - padding, 
                               max_x - min_x + 2*padding, max_y - min_y + 2*padding)
                else:
                    return  # No points to draw
            else:
                return  # Unknown tool
        
        # Draw selection outline
        painter.drawRect(rect)
        
        # Draw resize handles (corner squares)
        handle_size = max(6, int(8 / self.zoom_level))  # Adjust size with zoom
        half_size = handle_size // 2
        
        # Handle positions
        handles = [
            rect.topLeft(),     # Top-left
            rect.topRight(),    # Top-right
            rect.bottomLeft(),  # Bottom-left
            rect.bottomRight()  # Bottom-right
        ]
        
        # Draw handles
        handle_pen = QPen(QColor(0, 150, 255), 1)
        handle_pen.setCosmetic(True)
        handle_brush = QBrush(QColor(255, 255, 255))
        painter.setPen(handle_pen)
        painter.setBrush(handle_brush)
        
        for handle_pos in handles:
            handle_rect = QRect(
                handle_pos.x() - half_size,
                handle_pos.y() - half_size,
                handle_size,
                handle_size
            )
            painter.drawRect(handle_rect)
        
        # Restore original pen and brush
        painter.setPen(old_pen)
        painter.setBrush(old_brush)

    def draw_arrow(self, painter, start, end):
        if start == end:
            return
            
        # Draw the main line
        painter.drawLine(start, end)
        
        # Calculate the arrow head
        angle = atan2(end.y() - start.y(), end.x() - start.x())
        # Scale arrow size with pen width and zoom
        arrow_size = max(8, int((self.pen_size * 3 + 12) / self.zoom_level))
        arrow_angle = pi/6  # 30 degrees
        
        # Calculate arrow head points
        p1 = QPoint(
            int(end.x() - arrow_size * cos(angle - arrow_angle)),
            int(end.y() - arrow_size * sin(angle - arrow_angle))
        )
        p2 = QPoint(
            int(end.x() - arrow_size * cos(angle + arrow_angle)),
            int(end.y() - arrow_size * sin(angle + arrow_angle))
        )
        
        # Draw arrow head lines
        painter.drawLine(end, p1)
        painter.drawLine(end, p2)

    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            # Zoom
            zoom_factor = 1.1 if event.angleDelta().y() > 0 else 0.9
            old_zoom = self.zoom_level
            self.zoom_level *= zoom_factor
            self.zoom_level = max(0.1, min(5.0, self.zoom_level))
            
            # Adjust viewport to keep the mouse position fixed
            mouse_pos = event.pos()
            rel_x = (mouse_pos.x() - self.viewport_offset.x()) / old_zoom
            rel_y = (mouse_pos.y() - self.viewport_offset.y()) / old_zoom
            new_x = mouse_pos.x() - rel_x * self.zoom_level
            new_y = mouse_pos.y() - rel_y * self.zoom_level
            self.viewport_offset = QPoint(int(new_x), int(new_y))
            
            self.update()
        else:
            # Scroll
            self.viewport_offset += QPoint(
                -event.angleDelta().x() // 8,
                -event.angleDelta().y() // 8
            )
            self.update()

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        pos = self.transform_point(event.pos())
        text = event.mimeData().text()
        text_item = {
            'text': text,
            'pos': pos,
            'color': self.current_color,
            'font': QFont("Arial", 12)
        }
        self.text_items.append(text_item)
        self.add_to_undo_stack()
        self.update()
        event.acceptProposedAction()

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.is_panning = True
            self.pan_start = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            return
            
        transformed_pos = self.transform_point(event.pos())
        
        if event.button() == Qt.RightButton:
            self.handle_right_click(transformed_pos)
        elif event.button() == Qt.LeftButton:
            if self.current_tool == "count":
                self.add_counter(transformed_pos)
            elif self.current_tool == "eraser":
                if self.handle_eraser(transformed_pos):
                    self.update()
            else:
                self.handle_left_click(transformed_pos)

    def handle_right_click(self, pos):
        # Store right click position for potential dragging
        self.right_drag_start = pos
        
        # For text tool: right-click selects for moving, but don't enter edit mode yet
        # Edit mode will be handled in mouseReleaseEvent if no drag occurred
        if self.current_tool == "text":
            # Check if clicking on existing text
            for i, text_item in enumerate(self.text_items):
                text_rect = self.get_text_rect(text_item)
                if text_rect.contains(pos):
                    # Select the text for potential moving or editing
                    self.clear_all_selections()
                    self.selected_text_index = i
                    self.update()
                    return
            
            # If not clicking on text, clear selections
            self.clear_all_selections()
            self.update()
            return
        
        # For all other tools: right-click shows selection
        # Don't clear selections immediately - first check if we're clicking on something
        
        # Check for counter selection first (they're usually smaller)
        for i, counter_item in enumerate(self.counter_items):
            if len(counter_item) >= 2:
                counter_pos = counter_item[1]
                size = counter_item[3] if len(counter_item) == 4 else 2
                radius = 10 + size
                if (pos - counter_pos).manhattanLength() <= radius:
                    self.clear_selections_only()  # Only clear selections, keep drag state
                    self.selected_counter_index = i
                    # If we were editing text, exit without saving to prevent duplication
                    self.exit_text_editing_for_movement()
                    self.update()
                    return
        
        # Check for text selection
        for i, text_item in enumerate(self.text_items):
            text_rect = self.get_text_rect(text_item)
            if text_rect.contains(pos):
                self.clear_selections_only()  # Only clear selections, keep drag state
                self.selected_text_index = i
                # If we were editing a different text, exit without saving to prevent duplication
                if self.is_typing and self.editing_text_index != i:
                    self.exit_text_editing_for_movement()
                self.update()
                return
        
        # Check for shape selection
        for i, drawing in enumerate(self.drawings):
            if self.is_point_in_shape(pos, drawing):
                self.clear_selections_only()  # Only clear selections, keep drag state
                self.selected_shape_index = i
                # If we were editing text, exit without saving to prevent duplication
                self.exit_text_editing_for_movement()
                self.update()
                return
        
        # If nothing was clicked, clear all selections
        self.clear_all_selections()

    def handle_left_click(self, pos):
        if self.current_tool == "text":
            # For text tool, handle the two-click behavior
            if self.is_typing:
                # If currently typing, save and exit text mode
                if self.current_text:
                    self.save_current_text()
                self.stop_text_editing()
                self.text_tool_ready = False  # Not ready for immediate new text
                return
            elif not self.text_tool_ready:
                # First click after exiting text mode - just prepare for next click
                self.text_tool_ready = True
                return
            else:
                # Ready to create new text
                self.start_text_editing(pos)
                return
        else:
            # Exit text mode when using other tools
            if self.is_typing:
                if self.current_text:
                    self.save_current_text()
                self.stop_text_editing()
            
            # Reset text tool ready state when switching tools
            self.text_tool_ready = True
            
            # For other tools, check if we're clicking on a selected element for resize/move
            if self.selected_shape_index is not None:
                drawing = self.drawings[self.selected_shape_index]
                # Check if clicking on resize handle first
                self.check_resize_handle(pos, drawing)
                if self.is_resizing or self.is_moving:
                    return  # Don't start drawing if we're about to resize/move
            
            # Start drawing for drawing tools only if not interacting with selected elements
            if self.current_tool in ["rectangle", "circle", "arrow", "line", "pencil"]:
                self.is_drawing = True
                self.begin = pos
                self.end = pos
                if self.current_tool in ["pencil"]:
                    self.pencil_points = [pos]
        
        self.update()

    def mouseMoveEvent(self, event):
        transformed_pos = self.transform_point(event.pos())
        
        if self.is_panning:
            delta = event.pos() - self.pan_start
            self.viewport_offset += delta
            self.pan_start = event.pos()
            self.update()
            return
            
        # Handle right-click dragging for moving elements
        if event.buttons() & Qt.RightButton and self.right_drag_start:
            if not self.is_right_dragging:
                # Check if we've moved enough to start dragging
                drag_distance = (transformed_pos - self.right_drag_start).manhattanLength()
                if drag_distance > 5:  # 5 pixel threshold
                    self.is_right_dragging = True
                    # Exit text editing without saving when starting to move any element
                    # This prevents text duplication during movement
                    self.exit_text_editing_for_movement()
                    # Determine what to move based on current selection
                    if self.selected_shape_index is not None:
                        self.is_moving = True
                    elif self.selected_text_index is not None:
                        self.is_moving = True
                    elif self.selected_counter_index is not None:
                        self.is_moving = True
            
            if self.is_right_dragging and self.is_moving:
                self.move_selected_element(transformed_pos)
                self.update()
            return
            
        if self.current_tool == "eraser" and event.buttons() & Qt.LeftButton:
            if self.handle_eraser(transformed_pos):
                self.update()
            return
            
        if self.selected_shape_index is not None and self.selected_shape_index < len(self.drawings):
            if self.is_resizing:
                self.resize_selected_shape(transformed_pos)
            elif self.is_moving and not self.is_right_dragging:
                if not self.move_start:
                    self.move_start = transformed_pos
                else:
                    delta = transformed_pos - self.move_start
                    self.move_selected_shape(delta)
                    self.move_start = transformed_pos
            self.update()
            return
        
        if self.is_drawing:
            self.end = transformed_pos
            if self.current_tool in ["pencil"]:
                self.pencil_points.append(transformed_pos)
            self.update()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.is_panning = False
            self.pan_start = None
            self.setCursor(Qt.ArrowCursor)
            return
            
        transformed_pos = self.transform_point(event.pos())
        
        # ALWAYS reset movement states on ANY mouse button release (left or right)
        movement_was_active = self.is_right_dragging or self.is_moving
        
        # Reset ALL movement and drag states regardless of which button was released
        self.is_right_dragging = False
        self.right_drag_start = None
        self.last_drag_pos = None
        self.is_moving = False
        self.move_start = None
        self.is_resizing = False
        self.resize_handle = None
        
        # Clear original position storage
        if hasattr(self, '_original_shape_points'):
            delattr(self, '_original_shape_points')
        if hasattr(self, '_original_text_pos'):
            delattr(self, '_original_text_pos')
        if hasattr(self, '_original_counter_pos'):
            delattr(self, '_original_counter_pos')
        
        # Force cursor back to normal
        self.setCursor(Qt.ArrowCursor)
        
        # If we just finished moving something, ensure text editing is completely reset
        if movement_was_active:
            # Exit any lingering text editing state without saving to prevent duplication
            self.exit_text_editing_for_movement()
        
        if event.button() == Qt.RightButton:
            # Handle end of right-click drag
            if movement_was_active:
                # Add to undo stack if we moved something
                if (self.selected_shape_index is not None or 
                    self.selected_text_index is not None or 
                    self.selected_counter_index is not None):
                    self.add_to_undo_stack()
            else:
                # No drag occurred - handle single right-click actions
                if self.current_tool == "text" and self.selected_text_index is not None:
                    # Enter text editing mode for selected text
                    text_item = self.text_items[self.selected_text_index]
                    self.editing_text_index = self.selected_text_index
                    if isinstance(text_item, dict):
                        self.current_text = text_item['text']
                        self.text_position = text_item['pos']
                    else:
                        self.current_text = text_item[0]
                        self.text_position = text_item[1]
                    self.is_typing = True
                    self.text_cursor_pos = len(self.current_text)
                    self.setFocus()
            
            self.update()
            return
        
        elif event.button() == Qt.LeftButton:
            # Handle left-click release
            if movement_was_active:
                # Add to undo stack if we moved something
                if (self.selected_shape_index is not None or 
                    self.selected_text_index is not None or 
                    self.selected_counter_index is not None):
                    self.add_to_undo_stack()
            
            if self.is_drawing:
                self.is_drawing = False
                if not self.is_typing:
                    if self.current_tool == "pencil":
                        if len(self.pencil_points) > 1:
                            self.drawings.append((
                                self.current_tool,
                                self.current_color,
                                self.pencil_points.copy(),
                                self.pen_size
                            ))
                            self.add_to_undo_stack()
                        self.pencil_points = []
                    elif self.current_tool in ["rectangle", "circle", "arrow", "line"]:
                        if self.begin != self.end:
                            self.drawings.append((
                                self.current_tool,
                                self.current_color,
                                [self.begin, self.end],
                                self.pen_size
                            ))
                            self.add_to_undo_stack()
            # Note: Don't clear selections here as user might be interacting with selected items
            self.update()

    def transform_point(self, point):
        # Transform from screen coordinates to drawing coordinates
        x = (point.x() - self.viewport_offset.x()) / self.zoom_level
        y = (point.y() - self.viewport_offset.y()) / self.zoom_level
        return QPoint(int(x), int(y))

    def inverse_transform_point(self, point):
        # Transform from drawing coordinates to screen coordinates
        x = point.x() * self.zoom_level + self.viewport_offset.x()
        y = point.y() * self.zoom_level + self.viewport_offset.y()
        return QPoint(int(x), int(y))

    def get_text_rect(self, text_item):
        # Handle both dict and tuple formats
        if isinstance(text_item, dict):
            font = text_item.get('font', QFont("Arial", 12))
            text = text_item['text']
            pos = text_item['pos']
        else:  # tuple format
            font = QFont("Arial", 12)
            text = text_item[0]
            pos = text_item[1]
        
        metrics = QFontMetrics(font)
        
        # Handle multi-line text
        lines = text.split('\n')
        max_width = 0
        for line in lines:
            line_width = metrics.width(line)
            max_width = max(max_width, line_width)
        
        text_height = metrics.height() * len(lines)
        
        return QRect(pos.x() - 2, pos.y() - text_height,
                    max_width + 4, text_height + 4)

    def save_current_text(self):
        if self.current_text and self.current_text.strip():  # Only save non-empty text
            # Additional safety check: don't save if we're in the middle of movement operations
            if self.is_right_dragging or self.is_moving:
                print(f"WARNING: Attempted to save text during movement - skipping to prevent duplication")
                return
                
            # Calculate proper font size based on pen size
            font_size = max(8, self.pen_size + 8)  # Minimum 8px, scales with pen size
            text_font = QFont("Arial", font_size)
            
            text_item = {
                'text': self.current_text,
                'pos': self.text_position,
                'color': self.current_color,
                'font': text_font
            }
            
            if self.editing_text_index is not None and self.editing_text_index < len(self.text_items):
                print(f"Updating existing text at index {self.editing_text_index}: '{self.current_text}'")
                self.text_items[self.editing_text_index] = text_item
            else:
                print(f"Adding new text: '{self.current_text}'")
                self.text_items.append(text_item)
            
            self.add_to_undo_stack()

    def keyPressEvent(self, event):
        if self.is_typing:
            if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                # Support multi-line text with Shift+Enter, finish with Enter
                if event.modifiers() & Qt.ShiftModifier:
                    # Add newline for multi-line text
                    self.current_text = (self.current_text[:self.text_cursor_pos] + 
                                       "\n" + 
                                       self.current_text[self.text_cursor_pos:])
                    self.text_cursor_pos += 1
                else:
                    # Finish text editing - stop_text_editing will save if text exists
                    self.stop_text_editing()
                    # Clear selection after finishing text
                    self.selected_shape_index = None
            elif event.key() == Qt.Key_Backspace:
                if self.text_cursor_pos > 0:
                    self.current_text = (self.current_text[:self.text_cursor_pos - 1] + 
                                       self.current_text[self.text_cursor_pos:])
                    self.text_cursor_pos -= 1
                    self.cursor_visible = True  # Show cursor immediately on edit
            elif event.key() == Qt.Key_Delete:
                if self.text_cursor_pos < len(self.current_text):
                    self.current_text = (self.current_text[:self.text_cursor_pos] + 
                                       self.current_text[self.text_cursor_pos + 1:])
                    self.cursor_visible = True  # Show cursor immediately on edit
            elif event.key() == Qt.Key_Left:
                self.text_cursor_pos = max(0, self.text_cursor_pos - 1)
                self.cursor_visible = True  # Show cursor on navigation
            elif event.key() == Qt.Key_Right:
                self.text_cursor_pos = min(len(self.current_text), self.text_cursor_pos + 1)
                self.cursor_visible = True  # Show cursor on navigation
            elif event.key() == Qt.Key_Home:
                self.text_cursor_pos = 0
                self.cursor_visible = True
            elif event.key() == Qt.Key_End:
                self.text_cursor_pos = len(self.current_text)
                self.cursor_visible = True
            elif event.key() == Qt.Key_Escape:
                # Cancel text editing without saving
                # Reset state without calling save_current_text()
                self.cursor_blink_timer.stop()
                self.is_typing = False
                self.cursor_visible = False
                self.current_text = ""
                self.text_position = None
                self.text_cursor_pos = 0
                self.editing_text_index = None
                self.selected_shape_index = None  # Clear selection
            else:
                # Insert text at cursor position
                if len(event.text()) > 0 and event.text().isprintable():
                    self.current_text = (self.current_text[:self.text_cursor_pos] + 
                                       event.text() + 
                                       self.current_text[self.text_cursor_pos:])
                    self.text_cursor_pos += len(event.text())
                    self.cursor_visible = True  # Show cursor immediately on typing
            self.update()
        elif event.modifiers() & Qt.ControlModifier:
            if event.key() == Qt.Key_Z:
                self.undo()
            elif event.key() == Qt.Key_Y:
                self.redo()
        elif event.key() == Qt.Key_Escape:
            self.clear_all_selections()  # Clear all selections on Escape
            self.update()
        elif event.key() == Qt.Key_Delete:
            self.delete_selected_item()
            self.update()
        else:
            # Handle tool shortcuts when not typing
            main_window = self.get_main_window()
            if main_window:
                if event.key() == Qt.Key_R:
                    main_window.set_tool("rectangle", None)
                elif event.key() == Qt.Key_C:
                    main_window.set_tool("circle", None)
                elif event.key() == Qt.Key_A:
                    main_window.set_tool("arrow", None)
                elif event.key() == Qt.Key_L:
                    main_window.set_tool("line", None)
                elif event.key() == Qt.Key_P:
                    main_window.set_tool("pencil", None)
                elif event.key() == Qt.Key_T:
                    main_window.set_tool("text", None)
                elif event.key() == Qt.Key_E:
                    main_window.set_tool("eraser", None)
                elif event.key() == Qt.Key_N:
                    main_window.set_tool("count", None)

    def get_main_window(self):
        """Find the main window in the widget hierarchy"""
        widget = self
        while widget:
            if hasattr(widget, 'set_tool'):
                return widget
            widget = widget.parent()
        return None

    def add_to_undo_stack(self):
        state = {
            'drawings': self.drawings.copy(),
            'text_items': self.text_items.copy(),
            'counter_items': self.counter_items.copy(),
            'counter_value': self.counter_value
        }
        self.undo_stack.append(state)
        self.redo_stack.clear()  # Clear redo stack when new action is performed
        
        # Limit undo stack size
        if len(self.undo_stack) > self.max_undo_states:
            self.undo_stack.pop(0)

    def undo(self):
        if len(self.undo_stack) > 1:  # Keep at least one state
            current_state = self.undo_stack.pop()
            self.redo_stack.append(current_state)
            previous_state = self.undo_stack[-1]
            self.drawings = previous_state.get('drawings', []).copy()
            self.text_items = previous_state.get('text_items', []).copy()
            self.counter_items = previous_state.get('counter_items', []).copy()
            self.counter_value = previous_state.get('counter_value', self.counter_start)
            self.update()

    def redo(self):
        if self.redo_stack:
            next_state = self.redo_stack.pop()
            self.undo_stack.append(next_state)
            self.drawings = next_state.get('drawings', []).copy()
            self.text_items = next_state.get('text_items', []).copy()
            self.counter_items = next_state.get('counter_items', []).copy()
            self.counter_value = next_state.get('counter_value', self.counter_start)
            self.update()

    def is_point_in_shape(self, point, drawing):
        if len(drawing) == 5:  # Image
            tool, _, points, _, _ = drawing
            rect = QRect(points[0], points[1]).normalized()
            return rect.contains(point)
            
        tool, _, points, _ = drawing
        if tool in ["rectangle", "circle", "line", "arrow"]:
            rect = QRect(points[0], points[1]).normalized()
            return rect.contains(point)
        elif tool == "pencil":
            # Check if point is near any point in the pencil path
            for p in points:
                if (point - p).manhattanLength() < 5:
                    return True
        return False

    def check_resize_handle(self, pos, drawing):
        if len(drawing) == 5:  # Image
            tool, _, points, _, _ = drawing
        else:
            tool, _, points, _ = drawing
            
        if tool in ["rectangle", "circle", "arrow", "line", "image"]:
            rect = QRect(points[0], points[1]).normalized()
            handles = self.get_resize_handles(rect)
            
            for handle, handle_rect in handles.items():
                if handle_rect.contains(pos):
                    self.resize_handle = handle
                    self.is_resizing = True
                    return
            
            # If clicked inside shape but not on handle, enable moving
            if rect.contains(pos):
                self.is_moving = True
                return

    def get_resize_handles(self, rect):
        handle_size = 8
        half_size = handle_size // 2
        handles = {}
        
        # Corner handles
        handles['top_left'] = QRect(rect.topLeft().x() - half_size,
                                  rect.topLeft().y() - half_size,
                                  handle_size, handle_size)
        handles['top_right'] = QRect(rect.topRight().x() - half_size,
                                   rect.topRight().y() - half_size,
                                   handle_size, handle_size)
        handles['bottom_left'] = QRect(rect.bottomLeft().x() - half_size,
                                     rect.bottomLeft().y() - half_size,
                                     handle_size, handle_size)
        handles['bottom_right'] = QRect(rect.bottomRight().x() - half_size,
                                      rect.bottomRight().y() - half_size,
                                      handle_size, handle_size)
        
        return handles

    def resize_selected_shape(self, pos):
        if self.selected_shape_index is None:
            return
            
        drawing = self.drawings[self.selected_shape_index]
        if len(drawing) == 5:  # Image
            tool, color, points, size, image = drawing
        else:
            tool, color, points, size = drawing
        
        if tool in ["rectangle", "circle", "arrow", "line", "image"]:
            rect = QRect(points[0], points[1]).normalized()
            new_rect = QRect(rect)
            
            if self.resize_handle == 'top_left':
                new_rect.setTopLeft(pos)
            elif self.resize_handle == 'top_right':
                new_rect.setTopRight(pos)
            elif self.resize_handle == 'bottom_left':
                new_rect.setBottomLeft(pos)
            elif self.resize_handle == 'bottom_right':
                new_rect.setBottomRight(pos)
            
            if len(drawing) == 5:  # Image
                self.drawings[self.selected_shape_index] = (tool, color,
                                                          [new_rect.topLeft(), new_rect.bottomRight()],
                                                          size, image)
            else:
                self.drawings[self.selected_shape_index] = (tool, color,
                                                          [new_rect.topLeft(), new_rect.bottomRight()],
                                                          size)

    def move_selected_shape(self, delta):
        if self.selected_shape_index is None or not self.is_moving:
            return
            
        drawing = self.drawings[self.selected_shape_index]
        if len(drawing) == 5:  # Image
            tool, color, points, size, image = drawing
            new_points = [p + delta for p in points]
            self.drawings[self.selected_shape_index] = (tool, color, new_points, size, image)
        else:
            tool, color, points, size = drawing
            new_points = [p + delta for p in points]
            self.drawings[self.selected_shape_index] = (tool, color, new_points, size)

    def move_selected_element(self, current_pos):
        """Move the currently selected element to a new position"""
        if not self.right_drag_start:
            return
            
        # Calculate movement delta from the start position
        delta = current_pos - self.right_drag_start
        
        moved = False
        
        if self.selected_shape_index is not None and self.selected_shape_index < len(self.drawings):
            # Move shape
            drawing = self.drawings[self.selected_shape_index]
            if len(drawing) == 5:  # Image
                tool, color, points, size, image = drawing
                # Store original positions if not stored yet
                if not hasattr(self, '_original_shape_points'):
                    self._original_shape_points = [points[0], points[1]]
                new_points = [self._original_shape_points[0] + delta, self._original_shape_points[1] + delta]
                self.drawings[self.selected_shape_index] = (tool, color, new_points, size, image)
            else:  # Regular drawing
                tool, color, points, size = drawing
                # Store original positions if not stored yet
                if not hasattr(self, '_original_shape_points'):
                    if tool == "pencil":
                        self._original_shape_points = points.copy()
                    else:
                        self._original_shape_points = [points[0], points[1]]
                        
                if tool == "pencil":
                    # Move all points in pencil path
                    new_points = [self._original_shape_points[i] + delta for i in range(len(points))]
                else:
                    # Move start and end points
                    new_points = [self._original_shape_points[0] + delta, self._original_shape_points[1] + delta]
                self.drawings[self.selected_shape_index] = (tool, color, new_points, size)
            moved = True
                
        elif self.selected_text_index is not None and self.selected_text_index < len(self.text_items):
            # Move text
            text_item = self.text_items[self.selected_text_index]
            if isinstance(text_item, dict):
                # Store original position if not stored yet
                if not hasattr(self, '_original_text_pos'):
                    self._original_text_pos = text_item['pos']
                text_item['pos'] = self._original_text_pos + delta
            else:  # Old format
                # Store original position if not stored yet
                if not hasattr(self, '_original_text_pos'):
                    self._original_text_pos = text_item[1]
                text, pos, color = text_item
                self.text_items[self.selected_text_index] = (text, self._original_text_pos + delta, color)
            moved = True
                
        elif self.selected_counter_index is not None and self.selected_counter_index < len(self.counter_items):
            # Move counter
            counter_item = self.counter_items[self.selected_counter_index]
            if len(counter_item) == 4:  # New format with size
                # Store original position if not stored yet
                if not hasattr(self, '_original_counter_pos'):
                    self._original_counter_pos = counter_item[1]
                number, pos, color, size = counter_item
                self.counter_items[self.selected_counter_index] = (number, self._original_counter_pos + delta, color, size)
            else:  # Old format without size
                # Store original position if not stored yet
                if not hasattr(self, '_original_counter_pos'):
                    self._original_counter_pos = counter_item[1]
                number, pos, color = counter_item
                self.counter_items[self.selected_counter_index] = (number, self._original_counter_pos + delta, color)
            moved = True

    def handle_eraser(self, pos):
        """Handle eraser tool at the given position"""
        erase_radius = self.pen_size * 2
        items_to_remove = []
        
        # Check drawings
        for i, drawing in enumerate(self.drawings):
            if len(drawing) == 5:  # Image
                tool, _, points, _, _ = drawing
                rect = QRect(points[0], points[1]).normalized()
                if rect.contains(pos):
                    items_to_remove.append(("drawing", i))
            else:  # Regular drawings
                tool, _, points, _ = drawing
                if tool in ["rectangle", "circle", "arrow", "line"]:
                    rect = QRect(points[0], points[1]).normalized()
                    if rect.contains(pos):
                        items_to_remove.append(("drawing", i))
                elif tool == "pencil":
                    for point in points:
                        if (pos - point).manhattanLength() < erase_radius:
                            items_to_remove.append(("drawing", i))
                            break
        
        # Check text items
        for i, text_item in enumerate(self.text_items):
            text_rect = self.get_text_rect(text_item)
            if text_rect.contains(pos):
                items_to_remove.append(("text", i))
        
        # Check counter items
        for i, counter_item in enumerate(self.counter_items):
            if len(counter_item) == 4:  # New format with size
                _, counter_pos, _, _ = counter_item
            else:  # Old format without size
                _, counter_pos, _ = counter_item
            if (pos - counter_pos).manhattanLength() < erase_radius:
                items_to_remove.append(("counter", i))
        
        # Remove items in reverse order to maintain correct indices
        if items_to_remove:
            items_to_remove.sort(key=lambda x: (-x[1], x[0]))  # Sort by index descending
            for item_type, index in items_to_remove:
                if item_type == "drawing":
                    self.drawings.pop(index)
                elif item_type == "text":
                    self.text_items.pop(index)
                elif item_type == "counter":
                    self.counter_items.pop(index)
            
            self.add_to_undo_stack()
            return True
        
        return False

    def add_image(self, image_path):
        """Add an image to the drawing area"""
        image = QPixmap(image_path)
        if not image.isNull():
            # Scale image to reasonable size if too large
            max_size = min(self.width(), self.height()) // 2
            if image.width() > max_size or image.height() > max_size:
                image = image.scaled(max_size, max_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Place image in center of viewport
            center = self.transform_point(QPoint(self.width()//2, self.height()//2))
            top_left = center - QPoint(image.width()//2, image.height()//2)
            bottom_right = top_left + QPoint(image.width(), image.height())
            
            self.drawings.append(("image", None, [top_left, bottom_right], None, image))
            self.add_to_undo_stack()
            self.update()

    def add_counter(self, pos):
        # Store the counter with its size at the time of creation
        self.counter_items.append((self.counter_value, pos, self.current_color, self.pen_size))
        self.counter_value += 1
        self.add_to_undo_stack()
        self.update()

    def set_counter_start(self, value):
        self.counter_start = value
        self.counter_value = value

    def reset_counter(self):
        # Keep existing counter items but reset the counter value to start value
        self.counter_value = self.counter_start
        self.add_to_undo_stack()

    def toggle_cursor_visibility(self):
        """Toggle cursor visibility for blinking effect"""
        self.cursor_visible = not self.cursor_visible
        if self.is_typing:
            self.update()
    
    def start_text_editing(self, pos):
        """Start text editing mode with improved UX"""
        self.is_typing = True
        self.text_position = pos
        self.current_text = ""
        self.editing_text_index = None
        self.text_cursor_pos = 0
        self.cursor_visible = True
        
        # Start cursor blinking
        self.cursor_blink_timer.start(500)  # Blink every 500ms
        
        self.setFocus()
        self.update()
    
    def stop_text_editing(self):
        """Stop text editing mode and save any current text"""
        # Save current text if it exists and is not empty
        if self.is_typing and self.current_text and self.current_text.strip():
            print(f"Auto-saving text: '{self.current_text}'")  # Debug output
            self.save_current_text()
        
        # Reset text editing state
        self.cursor_blink_timer.stop()
        self.is_typing = False
        self.cursor_visible = False
        self.current_text = ""
        self.text_position = None
        self.text_cursor_pos = 0
        self.editing_text_index = None
        self.text_tool_ready = False  # Require two clicks after exiting text mode
        self.update()

    def exit_text_editing_for_movement(self):
        """Exit text editing mode without saving - used during movement to prevent duplication"""
        if self.is_typing:
            # Don't save, just reset state
            self.cursor_blink_timer.stop()
            self.is_typing = False
            self.cursor_visible = False
            self.current_text = ""
            self.text_position = None
            self.text_cursor_pos = 0
            self.editing_text_index = None
            self.text_tool_ready = False
            print("Exited text editing for movement without saving")  # Debug output

    def focusOutEvent(self, event):
        """Auto-save text when drawing area loses focus"""
        if self.is_typing and self.current_text and self.current_text.strip():
            self.stop_text_editing()
        super().focusOutEvent(event)

    def draw_text_selection(self, painter, text_item):
        """Draw selection feedback for text items"""
        # Save current pen and brush
        old_pen = painter.pen()
        old_brush = painter.brush()
        
        # Get text bounds
        text_rect = self.get_text_rect(text_item)
        
        # Create dashed pen for selection outline
        selection_pen = QPen(QColor(0, 150, 255), 2)
        selection_pen.setStyle(Qt.DashLine)
        selection_pen.setCosmetic(True)
        selection_pen.setDashPattern([5, 3])
        painter.setPen(selection_pen)
        painter.setBrush(Qt.NoBrush)
        
        # Draw selection outline
        painter.drawRect(text_rect)
        
        # No resize handles for text as requested
        # Text can only be moved with right-click drag
        
        # Restore original pen and brush
        painter.setPen(old_pen)
        painter.setBrush(old_brush)

    def draw_counter_selection(self, painter, center_pos, radius):
        """Draw selection feedback for counter items"""
        # Save current pen and brush
        old_pen = painter.pen()
        old_brush = painter.brush()
        
        # Create dashed pen for selection outline
        selection_pen = QPen(QColor(0, 150, 255), 2)
        selection_pen.setStyle(Qt.DashLine)
        selection_pen.setCosmetic(True)
        selection_pen.setDashPattern([5, 3])
        painter.setPen(selection_pen)
        painter.setBrush(Qt.NoBrush)
        
        # Draw selection circle outline
        selection_radius = radius + 4  # Slightly larger than the counter
        painter.drawEllipse(center_pos, selection_radius, selection_radius)
        
        # Draw resize handles around the circle
        handle_size = max(6, int(8 / self.zoom_level))
        half_size = handle_size // 2
        
        # Handle positions for counter (4 cardinal directions)
        handles = [
            QPoint(center_pos.x(), center_pos.y() - selection_radius),  # Top
            QPoint(center_pos.x() + selection_radius, center_pos.y()),  # Right
            QPoint(center_pos.x(), center_pos.y() + selection_radius),  # Bottom
            QPoint(center_pos.x() - selection_radius, center_pos.y())   # Left
        ]
        
        # Draw handles
        handle_pen = QPen(QColor(0, 150, 255), 1)
        handle_pen.setCosmetic(True)
        handle_brush = QBrush(QColor(255, 255, 255))
        painter.setPen(handle_pen)
        painter.setBrush(handle_brush)
        
        for handle_pos in handles:
            handle_rect = QRect(
                handle_pos.x() - half_size,
                handle_pos.y() - half_size,
                handle_size,
                handle_size
            )
            painter.drawRect(handle_rect)
        
        # Restore original pen and brush
        painter.setPen(old_pen)
        painter.setBrush(old_brush)

    def clear_all_selections(self):
        """Clear all element selections and drag states"""
        # If we're editing text when clearing selections during movement operations,
        # exit text editing without saving to prevent duplication
        if self.is_typing and (self.is_right_dragging or self.is_moving):
            self.exit_text_editing_for_movement()
        
        self.selected_shape_index = None
        self.selected_text_index = None
        self.selected_counter_index = None
        self.is_right_dragging = False
        self.right_drag_start = None
        self.last_drag_pos = None
        self.is_moving = False
        self.is_resizing = False
        self.move_start = None
        self.resize_handle = None
        
        # Clear original position storage
        if hasattr(self, '_original_shape_points'):
            delattr(self, '_original_shape_points')
        if hasattr(self, '_original_text_pos'):
            delattr(self, '_original_text_pos')
        if hasattr(self, '_original_counter_pos'):
            delattr(self, '_original_counter_pos')
        
        # Reset cursor
        self.setCursor(Qt.ArrowCursor)

    def clear_selections_only(self):
        """Clear only the selection indices without affecting drag state"""
        self.selected_shape_index = None
        self.selected_text_index = None
        self.selected_counter_index = None

    def delete_selected_item(self):
        """Delete the currently selected item"""
        deleted_something = False
        
        if self.selected_shape_index is not None and self.selected_shape_index < len(self.drawings):
            del self.drawings[self.selected_shape_index]
            self.selected_shape_index = None
            deleted_something = True
            
        elif self.selected_text_index is not None and self.selected_text_index < len(self.text_items):
            del self.text_items[self.selected_text_index]
            self.selected_text_index = None
            deleted_something = True
            
        elif self.selected_counter_index is not None and self.selected_counter_index < len(self.counter_items):
            del self.counter_items[self.selected_counter_index]
            self.selected_counter_index = None
            deleted_something = True
            
        if deleted_something:
            self.add_to_undo_stack()
