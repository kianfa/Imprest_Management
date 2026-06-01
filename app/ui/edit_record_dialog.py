from PyQt6.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QDateEdit, QFileDialog, QDialogButtonBox
from PyQt6.QtWidgets import QPushButton


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
        self.project_code_edit = QLineEdit(str(record_data["Project_Code"]))
        self.explanation_edit = QLineEdit(record_data["explanation"])
        self.amount_edit = QLineEdit(f"{int(record_data['amount']):,}")
        self.date_edit = QLineEdit(str(record_data["record_date"]))
        self.expense_center_edit = QLineEdit(str(record_data["expense_center"]))
        self.expense_type_edit = QLineEdit(str(record_data["expense_type"]))
        self.company_edit = QLineEdit(str(record_data["company_name"]))
        self.image_edit = QPushButton("Replace Image", self)

        # Combo boxes (populate as needed)
        form.addRow("Invoice No:", self.invoice_no_edit)
        form.addRow("Project Code:", self.project_code_edit)
        form.addRow("Explanation:", self.explanation_edit)
        form.addRow("Amount:", self.amount_edit)
        form.addRow("Record Date:", self.date_edit)
        form.addRow("Expense Center:", self.expense_center_edit)
        form.addRow("Expense Type:", self.expense_type_edit)
        form.addRow("Company:", self.company_edit)
        form.addRow("Image:", self.image_edit)

        self.image_edit.clicked.connect(self.add_images)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_updated_data(self):
        return {
            "Invoice_NO": self.invoice_no_edit.text(),
            "Project_Code": self.project_code_edit.text(),
            "explanation": self.explanation_edit.text(),
            "amount": float(self.amount_edit.text()),
            "record_date": self.date_edit.text(),
            "expense_center": self.expense_center_edit.text(),
            "expense_type": self.expense_type_edit.text(),
            "company_name": self.company_edit.text(),
            "image_path": (
            self.selected_image_paths[0]
            if hasattr(self, "selected_image_paths") and self.selected_image_paths
            else None
            )
        }

    def add_images(self) -> None:
        file_paths = QFileDialog.getOpenFileNames(
            self,
            "Add images",
            "./",
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp)"
        )[0]

        if file_paths:
            self.selected_image_paths = file_paths