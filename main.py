from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt
from melodious.ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Melodious")
    app.setOrganizationName("Melodious")

    icon = QIcon()
    for size in (16, 32, 48, 64, 128, 256, 512):


    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
