from PyQt6.QtWidgets import QWidget,QTableView
from PyQt6.QtCore import QDate
from PyQt6.uic import loadUi
from pathlib import Path
from app.controller.logic import calling_page_logic
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from app.data.data_base import Load_Save_Data


class Calling_Page(QWidget):
    def __init__(self):
        super().__init__()

        # Load UI made in Qt Designer
        ui_path = Path(__file__).parent / "Calling_Page.ui"
        self.UI = loadUi(ui_path, self)

        self.headers = ["Invoice NO", "explanation", "record_date", "amount",
                        "expense_center", "expense_type", "company_name"]
        self.model = QStandardItemModel(self)
        self.model.setColumnCount(len(self.headers))
        self.model.setHorizontalHeaderLabels([""] * len(self.headers))  # keep header blank
        self.model.appendRow([QStandardItem(h) for h in self.headers])  # static first row

        #ASK: vaghti ino mizarim inja kar nemikoneh? "self.tableView=QTableView(self)"
        self.UI.tableView.setModel(self.model)
        self.tableView.horizontalHeader().setVisible(False)
        self.tableView.verticalHeader().setVisible(False)  # removes row numbers + corner block
        self.tableView.setCornerButtonEnabled(False)  # extra safety
        self.stackedWidget.setCurrentIndex(3)
        self.setWindowTitle("Calling_Page")

        self.logic = calling_page_logic()

        self.logic.repo = Load_Save_Data()
        self.logic.model = self.model
        self.logic.headers = self.headers

        # Radio buttons
        self.rbInvoiceNo.setChecked(True)
        self.rbInvoiceNo.toggled.connect(lambda: self.change_page(3))
        self.rbTimeRange.toggled.connect(lambda: self.change_page(2))
        self.rbRegistrationDate.toggled.connect(lambda: self.change_page(1))
        self.rbExplanation.toggled.connect(lambda: self.change_page(0))

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

        self.deRegstrationDate.setDisplayFormat("yyyy-MM-dd")

        #loading data
        self.logic.tableView = self.tableView

        self.logic.rbInvoiceNo = self.rbInvoiceNo
        self.logic.rbTimeRange = self.rbTimeRange
        self.logic.rbRegistrationDate = self.rbRegistrationDate
        self.logic.rbExplanation = self.rbExplanation

        self.logic.leInvoiceNo = self.leInvoiceNo
        self.logic.leExplanation = self.leExplanation
        self.logic.deRegstrationDate = self.deRegstrationDate
        self.logic.deLoginStart = self.deLoginStart
        self.logic.deLoginEnd = self.deLoginEnd


        self.btnSearch.clicked.connect(self.logic.load_invoices)

    def change_page(self, index):
        if self.sender().isChecked():
            self.stackedWidget.setCurrentIndex(index)
