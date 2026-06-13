from PyQt6.QtWidgets import QDialog, QMessageBox
from PyQt6.uic import loadUi
from pathlib import Path
from app.controller.logic import main_window_logic
from app.controller.navigator import Navigator
import sys

class MainWindow(QDialog):
    def __init__(self) -> None:

        super().__init__()

        if getattr(sys, 'frozen', False):
            ui_path = Path(sys._MEIPASS) / "app" / "ui" / "main_window.ui"
        else:
            ui_path = Path(__file__).parent / "main_window.ui"

        self.UI = loadUi(str(ui_path), self)
        self.setWindowTitle("Login")
        self.success = False
        self.role = ""
        self.username = ""

        self.setWindowTitle("Imprest_Management Version 1.0")
        self.logic = main_window_logic()
        self.nav=Navigator()
        self.UI.btnLogin.clicked.connect(self.on_login_clicked)

        self.UI.lblFooterLeft.setText("""
        <div align="left">
        <a href="about" style="
            color: #939495;
            text-decoration: none;
            font-family: 'Segoe UI';
            font-size: 10px;
        ">
        Nozhan Ghayati Design &amp; Developer <br>
        Kian Farooghi Project Management &amp; QA <br><br>
        © 2026
        </a>
        </div>
        """)
        self.UI.lblFooterLeft.linkActivated.connect(self.open_about_page)

    def on_login_clicked(self) -> None:
        username = self.UI.leUsername.text().strip()
        password = self.UI.lePassword.text()

        result = main_window_logic.login(username, password)  # call class method
        if result.ok:
            self.success = True
            self.accept()
            self.nav.main_window_navigator(self)
        else:
            QMessageBox.critical(None, "Warning", result.error_message)

    def open_about_page(self, link):
        try:
            self.nav.main_window_navigator_about_us(self)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"CRASH: {e}")