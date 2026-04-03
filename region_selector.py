"""Mail Sense - Region Selector (screen area selection overlay)"""
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal
from PyQt6.QtGui import QPainter, QColor, QPen, QFont, QGuiApplication


class RegionSelector(QWidget):
    """Full-screen overlay for selecting a rectangular screen region."""

    region_selected = pyqtSignal(int, int, int, int)
    selection_cancelled = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setCursor(Qt.CursorShape.CrossCursor)
        self._setup_geometry()
        self._origin = QPoint()
        self._current = QPoint()
        self._is_selecting = False

    def _setup_geometry(self):
        screens = QGuiApplication.screens()
        if not screens:
            return
        total = screens[0].geometry()
        for s in screens[1:]:
            total = total.united(s.geometry())
        self.setGeometry(total)
        self._offset = total.topLeft()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.fillRect(self.rect(), QColor(0, 0, 0, 120))

        if self._is_selecting:
            sel = QRect(self._origin, self._current).normalized()
            if sel.width() > 2 and sel.height() > 2:
                p.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
                p.fillRect(sel, Qt.GlobalColor.transparent)
                p.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
                p.setPen(QPen(QColor(10, 132, 255, 80), 6))
                p.drawRect(sel.adjusted(-2, -2, 2, 2))
                p.setPen(QPen(QColor(10, 132, 255), 2))
                p.drawRect(sel)
                p.setPen(QColor(255, 255, 255, 200))
                f = p.font()
                f.setPointSize(11)
                p.setFont(f)
                p.drawText(sel.x(), sel.y() - 8, f"{sel.width()} × {sel.height()}")

        p.setPen(QColor(255, 255, 255, 180))
        f = QFont('Segoe UI', 14)
        p.setFont(f)
        p.drawText(self.rect().adjusted(0, 40, 0, 0),
                   Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop,
                   "드래그하여 영역을 선택하세요  |  ESC: 취소")

    def mousePressEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton:
            self._origin = e.pos()
            self._current = e.pos()
            self._is_selecting = True
            self.update()

    def mouseMoveEvent(self, e):
        if self._is_selecting:
            self._current = e.pos()
            self.update()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.MouseButton.LeftButton and self._is_selecting:
            self._is_selecting = False
            self._current = e.pos()
            sel = QRect(self._origin, self._current).normalized()
            if sel.width() > 10 and sel.height() > 10:
                ratio = self.window().devicePixelRatioF()
                gx = int((sel.x() + self._offset.x()) * ratio) - 16
                gy = int((sel.y() + self._offset.y()) * ratio) - 16
                gw = int(sel.width() * ratio) + 32
                gh = int(sel.height() * ratio) + 32
                self.region_selected.emit(gx, gy, gw, gh)
            else:
                self.selection_cancelled.emit()
            self.close()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key.Key_Escape:
            self.selection_cancelled.emit()
            self.close()
