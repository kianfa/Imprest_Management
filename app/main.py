import sys
from PyQt6.QtWidgets import QApplication
from app.ui.main_window import MainWindow
from app.data.data_base import create_tables

#pyqt6-tools designer
#.\.venv2\Scripts\activate
#python -m app.main

def main():
    create_tables()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
