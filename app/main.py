import sys
from PyQt6.QtWidgets import QApplication
from app.ui.main_window_UI import MainWindow
from app.data.data_base import DataBase

#pyqt6-tools designer
#.\.venv2\Scripts\activate
#python -m app.main

def main():
    DataBase.create_tables()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
