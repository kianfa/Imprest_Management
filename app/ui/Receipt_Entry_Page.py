from PyQt6.QtWidgets import QWidget,QMessageBox
from PyQt6.uic import loadUi
from pathlib import Path
from app.data.data_base import Load_Save_Data
from app.controller.logic import receipt_entry_logic


class Expense_Receipt_Entry(QWidget):
    def __init__(self):
        super().__init__()
        from app.controller.navigator import Navigator

        ui_path = Path(__file__).parent / "Expense_Receipt_Entry.ui"
        loadUi(ui_path, self)
        self.setWindowTitle("Expense_Receipt_Entry")
        self.selected_image_path = None
        self.nav = Navigator()
        self.logic = receipt_entry_logic()
        self.btnBrowse.clicked.connect(self.browse_image)
        self.btnClear.clicked.connect(self.clear_image)
        self.btnSave.clicked.connect(self.save_record)





    def browse_image(self):
        path = self.logic.browse_image(parent=self, title = "Select an image")
        self.selected_image_path = path
        self.lblSelectPicture.setText(path)
        if not path:
            return



    def clear_image(self):
        self.selected_image_path = None
        self.lblSelectPicture.setText("No file selected")



    def open_dashboard(self):
        self.dashboard = self.nav.expense_entry_page_navigator(self)



    def save_record(self):
        data = {
            "Invoice NO": self.leInvoiceNumber.text(),
            "explanation": self.teExplanation.toPlainText(),
            "amount": self.leExpense.text(),
            "record_date": self.deDate.date().toString("yyyy-MM-dd"),
            "image_path": self.selected_image_path,
            "expense_center": self.cbExpenseCenter.currentText(),
            "expense_type": self.cbExpenseType.currentText(),
            "company_name": self.cbCompany.currentText(),
            "source_pc": "PC-1"
        }
        try:
            Load_Save_Data.save_data(data)
            self.open_dashboard()

        except ValueError as e:
            QMessageBox.warning(self, "Validation Error", str(e))

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
