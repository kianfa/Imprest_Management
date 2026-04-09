from PyQt6.QtWidgets import QMainWindow
from PyQt6.uic import loadUi
from pathlib import Path

class Dashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        from app.controller.navigator import Navigator

        ui_path = Path(__file__).parent / "Dashboard.ui"
        self.UI = loadUi(ui_path, self)

        self.setWindowTitle("Dashboard")
        self.nav=Navigator()
        self.UI.btndashboard_input.clicked.connect(self.Input_Clicked)
        self.UI.btndashboard_save.clicked.connect(self.Save_Clicked)



    def Input_Clicked(self):
        self.nav.dashboard_page_navigator_expense_entry(self)
    def Save_Clicked(self):
        self.nav.dashboard_page_navigator_calling_page(self)