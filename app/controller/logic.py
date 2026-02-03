from __future__ import annotations
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import QFileDialog, QWidget
from dataclasses import dataclass
from app.data import user_repository as repo
from PyQt6.QtGui import QStandardItem, QStandardItemModel


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
        rows = []
        if self.radioButton1.isChecked():
            rows = repo.load_data.get_invoices_by_invoice_no(
                self.leInvoiceNo.text()
            )

        elif self.radioButton2.isChecked():
            rows = repo.load_data.get_invoices_by_registration_date(
                self.deRegstrationDate.text()
            )

        elif self.radioButton3.isChecked():
            rows = repo.load_data.get_invoices_by_login_date(
                self.deLoginStart.text()
            )

        elif self.radioButton4.isChecked():
            rows = repo.load_data.get_invoices_by_explanation(
                self.leExplanation.text()
            )

        self.populate_table(rows)


    def populate_table(self, rows):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels([
            "Invoice No", "Title","amount" , "Explanation",
            "Registration Date", "Login Date"
        ])

        for row in rows:
            model.appendRow(
                [QStandardItem(str(col)) for col in row]
            )

        self.tableView.setModel(model)
