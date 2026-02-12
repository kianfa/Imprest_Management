from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QDate
from PyQt6.uic import loadUi
from pathlib import Path
from app.data.user_repository import load_data
from app.controller.logic import calling_page_logic
from PyQt6.QtGui import QStandardItemModel, QStandardItem

class Calling_Page(QWidget):
    def __init__(self):
        super().__init__()
        ui_path = Path(__file__).parent / "Calling_Page.ui"
        loadUi(ui_path, self)
        self.headers = ["title", "explanation", "record_date", "amount",
                        "expense_center", "expense_type", "company_name"]

        self.model = QStandardItemModel(self)
        self.model.setColumnCount(len(self.headers))
        self.model.setHorizontalHeaderLabels([""] * len(self.headers))  # keep header blank

        self.model.appendRow([QStandardItem(h) for h in self.headers])  # static first row
        self.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setVisible(False)
        self.tableView.verticalHeader().setVisible(False)  # removes row numbers + corner block
        self.tableView.setCornerButtonEnabled(False)  # extra safety
        self.stackedWidget.setCurrentIndex(3)
        self.setWindowTitle("Calling_Page")

        self.logic = calling_page_logic()

        self.logic.repo = load_data()
        self.logic.model = self.model
        self.logic.headers = self.headers

        # Radio buttons
        self.radioButton1.setChecked(True)
        self.radioButton1.toggled.connect(lambda: self.change_page(3))
        self.radioButton2.toggled.connect(lambda: self.change_page(2))
        self.radioButton3.toggled.connect(lambda: self.change_page(1))
        self.radioButton4.toggled.connect(lambda: self.change_page(0))

        # DateEdit 2 (Start)
        self.deLoginEnd.setMinimumDate(QDate(2000, 1, 1))
        self.deLoginEnd.setSpecialValueText("End")
        self.deLoginEnd.setDisplayFormat("yyyy-MM-dd")
        self.deLoginEnd.setDate(self.deLoginEnd.minimumDate())

        # DateEdit 3 (End)
        self.deLoginStart.setMinimumDate(QDate(2000, 1, 1))
        self.deLoginStart.setSpecialValueText("Start")
        self.deLoginStart.setDisplayFormat("yyyy-MM-dd")
        self.deLoginStart.setDate(self.deLoginStart.minimumDate())

        #loading data
        self.logic.tableView = self.tableView

        self.logic.radioButton1 = self.radioButton1
        self.logic.radioButton2 = self.radioButton2
        self.logic.radioButton3 = self.radioButton3
        self.logic.radioButton4 = self.radioButton4

        self.logic.leInvoiceNo = self.leInvoiceNo
        self.logic.leExplanation = self.leExplanation
        self.logic.deRegstrationDate = self.deRegstrationDate
        self.logic.deLoginStart = self.deLoginStart

        self.btnSearch.clicked.connect(self.logic.load_invoices)

    def change_page(self, index):
        if self.sender().isChecked():
            self.stackedWidget.setCurrentIndex(index)
