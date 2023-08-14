import sys
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class SnippingWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Snipping ")
        self.begin = QPoint()
        self.end = QPoint()

        self.setWindowOpacity(0.3)

        QApplication.setOverrideCursor(QCursor(Qt.CrossCursor))
        self.setWindowFlags(Qt.FramelessWindowHint)
        print("Capture the screen...")

        self.showFullScreen()

    def paintEvent(self, event):
        qp = QPainter(self)
        qp.setPen(QPen(QColor("black"), 3))
        qp.setBrush(QColor(128, 128, 255, 128))
        qp.drawRect(QRect(self.begin, self.end))

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        self.begin = event.globalPosition().toPoint()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)
        self.end = event.globalPosition().toPoint()
        self.update()

    def mouseReleaseEvent(self, event):
        self.close()
        QTimer.singleShot(1000, self.screenshot)

    def screenshot(self):
        print("screenshot")
        screen = QGuiApplication.primaryScreen()
        window = self.windowHandle()
        if window is not None:
            screen = window.screen()
        if screen is None:
            print("failed")
            return

        original_pixmap = screen.grabWindow(0)
        output_pixmap = original_pixmap.copy(
            QRect(self.begin, self.end).normalized()
        )
        output_pixmap.save("capture.png")

        self.label = QLabel(pixmap=output_pixmap)
        self.label.show()
        app.setQuitOnLastWindowClosed(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SnippingWidget()
    window.show()
    app.aboutToQuit.connect(app.deleteLater)
    app.setQuitOnLastWindowClosed(False)
    sys.exit(app.exec())