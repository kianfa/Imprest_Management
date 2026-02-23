from PyQt6.QtCore import QDate
from PyQt6.uic import loadUi
from pathlib import Path
from app.controller.logic import calling_page_logic
from app.data.data_base import Load_Save_Data
from app.controller.navigator import Navigator
from PyQt6.QtGui import QStandardItemModel
from PyQt6.QtWidgets import QWidget, QFileDialog



class Calling_Page(QWidget):
    def __init__(self):
        super().__init__()

        # Load UI made in Qt Designer
        ui_path = Path(__file__).parent / "Calling_Page.ui"
        self.UI = loadUi(ui_path, self)

        self.nav = Navigator()

        self.headers = ["Invoice NO", "explanation", "record_date", "amount",
                        "expense_center", "expense_type", "company_name"]
        self.model = QStandardItemModel(self)
        self.model.setColumnCount(len(self.headers))
        self.model.setHorizontalHeaderLabels(self.headers)

        self.UI.tableView.setModel(self.model)
        self.UI.tableView.horizontalHeader().setVisible(False)
        self.UI.tableView.verticalHeader().setVisible(False)  # removes row numbers + corner block
        self.UI.tableView.setCornerButtonEnabled(False)  # extra safety
        self.UI.stackedWidget.setCurrentIndex(3)
        self.UI.setWindowTitle("Calling_Page")

        self.logic = calling_page_logic()
        self.logic.repo = Load_Save_Data()
        self.logic.model = self.model
        self.logic.headers = self.headers

        # Radio buttons
        self.UI.rbInvoiceNo.setChecked(True)
        self.UI.rbInvoiceNo.toggled.connect(lambda: self.change_page(3))
        self.UI.rbTimeRange.toggled.connect(lambda: self.change_page(2))
        self.UI.rbRegistrationDate.toggled.connect(lambda: self.change_page(1))
        self.UI.rbExplanation.toggled.connect(lambda: self.change_page(0))

        # DateEdit 2 (Start)
        self.UI.deLoginEnd.setMinimumDate(QDate(2000, 1, 1))
        self.UI.deLoginEnd.setSpecialValueText("End")
        self.UI.deLoginEnd.setDisplayFormat("yyyy-MM-dd")
        self.UI.deLoginEnd.setDate(self.UI.deLoginEnd.minimumDate())

        # DateEdit 3 (End)
        self.UI.deLoginStart.setMinimumDate(QDate(2000, 1, 1))
        self.UI.deLoginStart.setSpecialValueText("Start")
        self.UI.deLoginStart.setDisplayFormat("yyyy-MM-dd")
        self.UI.deLoginStart.setDate(self.UI.deLoginStart.minimumDate())

        self.UI.deRegstrationDate.setDisplayFormat("yyyy-MM-dd")

        #loading data
        self.logic.tableView = self.UI.tableView

        self.logic.rbInvoiceNo = self.UI.rbInvoiceNo
        self.logic.rbTimeRange = self.UI.rbTimeRange
        self.logic.rbRegistrationDate = self.UI.rbRegistrationDate
        self.logic.rbExplanation = self.UI.rbExplanation

        self.logic.leInvoiceNo = self.UI.leInvoiceNo
        self.logic.leExplanation = self.UI.leExplanation
        self.logic.deRegstrationDate = self.UI.deRegstrationDate
        self.logic.deLoginStart = self.UI.deLoginStart
        self.logic.deLoginEnd = self.UI.deLoginEnd

        self.UI.btnSearch.clicked.connect(self.logic.load_invoices)

        self.UI.btnCancel.clicked.connect(self.open_dashboard)

        self.UI.btnSaveasPDF.clicked.connect(self.on_save_pdf_clicked)

    def change_page(self, index):
        if self.sender().isChecked():
            self.UI.stackedWidget.setCurrentIndex(index)

    def open_dashboard(self):
        self.UI.dashboard = self.nav.calling_entry_page_navigator(self)

    def on_save_pdf_clicked(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "results.pdf", "PDF (*.pdf)")
        if path:
            calling_page_logic.export_tableview_to_pdf(self.UI.tableView, path)