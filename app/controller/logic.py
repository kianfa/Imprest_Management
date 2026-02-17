from __future__ import annotations
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import QFileDialog, QWidget
from dataclasses import dataclass
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from app.data.data_base import Load_Save_Data


class receipt_entry_logic:
    def browse_image(
            self,
            parent: QWidget,
            title: str = "Select an image",
            start_dir: Optional[str | Path] = None,
    ) -> Optional[str]:
        """
        Opens a file dialog and returns the selected image path as a string.
        Returns None if the user cancels.
        """
        start_dir_str = str(start_dir) if start_dir else ""

        file_path, _ = QFileDialog.getOpenFileName(
            parent,
            title,
            start_dir_str,
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp);;All Files (*)",
        )

        return file_path or None


@dataclass
class LoginResult:
    ok: bool
    error: str = ""

class main_window_logic:
    def validate_inputs(self, username: str, password: str) -> LoginResult:
        if not username:
            return LoginResult(False, "Username is empty")
        if not password:
            return LoginResult(False, "Password is empty")
        return LoginResult(True)

    def login(self, username: str, password: str) -> LoginResult:
        # later: check DB / API
        return self.validate_inputs(username, password)



class calling_page_logic:
    def __init__(self):
        super().__init__()

    def load_invoices(self):
        # Your repo functions return (headers, rows), so we ignore headers
        if self.rbInvoiceNo.isChecked():
            rows = Load_Save_Data.get_invoices_by_Invoice_NO(self.leInvoiceNo.text().strip())


        elif self.rbTimeRange.isChecked():
            date_str_start = self.deLoginStart.date().toString("yyyy-MM-dd")
            date_str_end = self.deLoginEnd.date().toString("yyyy-MM-dd")
            rows = Load_Save_Data.get_invoices_by_time_range(date_str_start, date_str_end)

        elif self.rbRegistrationDate.isChecked():
            date_str = self.deRegstrationDate.date().toString("yyyy-MM-dd")
            rows = Load_Save_Data.get_invoices_by_regestrationdate(date_str)

        else:  # rbExplanation
            rows = Load_Save_Data.get_invoices_by_Explanation(self.leExplanation.text().strip())

        # Clear + keep the static first row
        self.model.clear()
        self.model.setColumnCount(len(self.headers))
        self.model.setHorizontalHeaderLabels([""] * len(self.headers))
        self.model.appendRow([QStandardItem(h) for h in self.headers])

        # Fill DB rows cell-by-cell
        for row in rows:
            items = [QStandardItem("" if v is None else str(v)) for v in row]
            self.model.appendRow(items)

    def populate_table(self, rows):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels([
            "Invoice No","amount" , "Explanation",
            "Registration Date", "Login Date"
        ])

        for row in rows:
            model.appendRow(
                [QStandardItem(str(col)) for col in row]
            )

        self.tableView.setModel(model)
