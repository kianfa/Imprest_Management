from PyQt6.QtCore import QDate
from PyQt6.uic import loadUi
from pathlib import Path
from app.controller.logic import calling_page_logic, exporting
from app.data.data_base import Load_Save_Data, UserSession
from app.controller.navigator import Navigator
from PyQt6.QtGui import QStandardItemModel
from PyQt6.QtWidgets import QWidget, QFileDialog
from PyQt6.QtWidgets import QAbstractItemView
import sys
class Calling_Page(QWidget):
    def __init__(self) -> None:
        super().__init__()

        # Load UI made in Qt Designer
        if getattr(sys, 'frozen', False):
            ui_path = Path(sys._MEIPASS) / "app" / "ui" / "Calling_Page.ui"
        else:
            ui_path = Path(__file__).parent / "Calling_Page.ui"

        self.UI = loadUi(str(ui_path), self)

        self.nav = Navigator()
        self.us = UserSession()

        self.current_full_name = self.us.full_name
        self.current_role = self.us.role

        self.headers = ["id", "Invoice NO", "Project Code", "explanation", "record_date", "amount",
                        "expense_center", "expense_type", "company_name","created_by "]
        self.model = QStandardItemModel(self)
        self.model.setColumnCount(len(self.headers))
        self.model.setHorizontalHeaderLabels(self.headers)

        self.UI.tableView.setModel(self.model)
        self.UI.tableView.setModel(self.model)
        self.UI.tableView.horizontalHeader().setDefaultSectionSize(122)
        self.UI.tableView.horizontalHeader().setVisible(False)
        self.UI.tableView.verticalHeader().setVisible(False)  # removes row numbers + corner block
        self.UI.tableView.setCornerButtonEnabled(False)  # extra safety
        self.UI.stackedWidget.setCurrentIndex(3)
        self.UI.setWindowTitle("Calling_Page")

        self.logic = calling_page_logic()
        self.export = exporting()
        self.logic.repo = Load_Save_Data()
        self.logic.model = self.model
        self.logic.headers = self.headers

        # Radio buttons
        self.UI.rbInvoiceNo.setChecked(True)
        self.UI.rbProjectCode.toggled.connect(lambda: self.change_page(4))
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

        # Enable row selection on the table view
        self.UI.tableView.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.UI.tableView.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)

        # Buttons
        self.UI.btnSearch.clicked.connect(lambda :self.logic.load_invoices(self.UI.rbInvoiceNo,self.UI.leInvoiceNo,
                                                                           self.UI.rbProjectCode,self.UI.leProjectCode,
                                                                           self.UI.rbTimeRange,self.UI.deLoginStart, self.UI.deLoginEnd,
                                                                           self.UI.rbRegistrationDate, self.UI.deRegstrationDate, self.UI.leExplanation))
        self.UI.btnEditRecord.clicked.connect(self.edit_record)
        self.UI.btnDeleteRecord.clicked.connect(self.delete_record)
        self.UI.btnCancel.clicked.connect(self.open_dashboard)
        self.UI.btnSaveasPDF.clicked.connect(self.on_save_pdf_clicked)
        self.UI.btnSaveasexcel.clicked.connect(self.on_save_excel_clicked)

    def change_page(self, index) -> None:
        if self.sender().isChecked():
            self.UI.stackedWidget.setCurrentIndex(index)

    def open_dashboard(self) -> None:
        self.nav.calling_entry_page_navigator(self)

    def on_save_pdf_clicked(self) -> None:
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", "results.pdf", "PDF (*.pdf)")
        if path:
            self.export.export_table_to_pdf(table=self.UI.tableView, file_path=path)

    def on_save_excel_clicked(self) -> None:
        self.export.export_tableview_to_excel(self.UI.tableView)

    def edit_record(self) -> None:
        self.logic.edit_record(self.UI.tableView)
        # Refresh the table
        self.logic.load_invoices(self.UI.rbInvoiceNo,self.UI.leInvoiceNo,
                                 self.UI.rbProjectCode,self.UI.leProjectCode,
                                 self.UI.rbTimeRange,self.UI.deLoginStart, self.UI.deLoginEnd,
                                 self.UI.rbRegistrationDate, self.UI.deRegstrationDate, self.UI.leExplanation)

    def delete_record(self) -> None:
        self.logic.delete_record(self.UI.tableView)
        #Refresh the table
        self.logic.load_invoices(self.UI.rbInvoiceNo,self.UI.leInvoiceNo,
                                 self.UI.rbProjectCode,self.UI.leProjectCode,
                                 self.UI.rbTimeRange,self.UI.deLoginStart, self.UI.deLoginEnd,
                                 self.UI.rbRegistrationDate, self.UI.deRegstrationDate, self.UI.leExplanation)