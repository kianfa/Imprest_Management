import sys
from PyQt6.QtWidgets import QApplication
from app.ui.main_window_UI import MainWindow
from app.data.data_base import DataBase
from app.controller.license import LicenseManager

#pyqt6-tools designer
#.\.venv2\Scripts\activate
#python -m app.main

def main() -> None:
    DataBase.create_tables()
    DataBase.create_default_users()
    app = QApplication(sys.argv)
    lm = LicenseManager()
    lm.check_or_initialize()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
