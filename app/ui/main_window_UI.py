from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.uic import loadUi
from pathlib import Path
from app.controller.logic import main_window_logic
from app.data.data_base import DataBase


class MainWindow(QDialog):
    def __init__(self) -> None:
        super().__init__()
        ui_path = Path(__file__).parent / "main_window.ui"
        self.UI = loadUi(ui_path, self)
        self.setWindowTitle("Login")
        self.success = False
        self.role = ""
        self.username = ""

        from app.controller.navigator import Navigator
        self.setWindowTitle("My App")
        self.logic = main_window_logic()
        self.nav=Navigator()
        self.UI.btnLogin.clicked.connect(self.on_login_clicked)

    def on_login_clicked(self) -> None:
        username = self.UI.leUsername.text().strip()
        password = self.UI.lePassword.text()

        result = main_window_logic.login(username, password)  # call class method
        if result.ok:
            self.success = True
            UserSession.username = username
            UserSession.full_name = str(username)
            UserSession.role = str(result.role)
            self.accept()
            self.nav.main_window_navigator(self)
        else:
            QMessageBox.critical(None, "Warning", result.error_message)


class UserSession:
    username = ""
    full_name = ""
    role = ""