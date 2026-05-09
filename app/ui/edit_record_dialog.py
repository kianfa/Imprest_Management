# edit_record_dialog.py
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDateEdit, QComboBox, QDialogButtonBox
from PyQt6.QtCore import QDate


class EditRecordDialog(QDialog):
    def __init__(self, record_data, parent=None):
        super().__init__(parent)
        self.record_data = record_data
        self.setWindowTitle("Edit Record")
        self.setModal(True)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Editable fields
        self.invoice_no_edit = QLineEdit(str(record_data["Invoice_NO"]))
        self.explanation_edit = QLineEdit(record_data["explanation"])
        self.amount_edit = QLineEdit(str(record_data["amount"]))
        self.date_edit = QDateEdit()
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        self.date_edit.setDate(QDate.fromString(record_data["record_date"], "yyyy-MM-dd"))
        self.expense_center_edit = QLineEdit(str(record_data["expense_center"]))
        self.expense_type_edit = QLineEdit(str(record_data["expense_type"]))
        self.company_edit = QLineEdit(str(record_data["company_name"]))

        # Combo boxes (populate as needed)
        form.addRow("Invoice No:", self.invoice_no_edit)
        form.addRow("Explanation:", self.explanation_edit)
        form.addRow("Amount:", self.amount_edit)
        form.addRow("Record Date:", self.date_edit)
        form.addRow("Expense Center:", self.expense_center_edit)
        form.addRow("Expense Type:", self.expense_type_edit)
        form.addRow("Company:", self.company_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_updated_data(self):
        return {
            "Invoice_NO": self.invoice_no_edit.text(),
            "explanation": self.explanation_edit.text(),
            "amount": float(self.amount_edit.text()),
            "record_date": self.date_edit.date().toString("yyyy-MM-dd"),
            "expense_center": self.expense_center_edit.text(),
            "expense_type": self.expense_type_edit.text(),
            "company_name": self.company_edit.text()
        }