import sys
from PySide6.QtWidgets import QApplication
from ui.main_window_ui import MainWindow
from PySide6.QtCore import QFile
from PySide6.QtGui import QIcon

if __name__ == "__main__":
    app = QApplication(sys.argv)
    style_file = QFile("streamraptor/ui/styles.qss")
    if style_file.open(QFile.ReadOnly | QFile.Text):
        app.setStyleSheet(style_file.readAll().data().decode())
    window = MainWindow()
    window.setWindowIcon(QIcon("streamraptor/assets/icons/video.png"))
    window.show()
    sys.exit(app.exec())
