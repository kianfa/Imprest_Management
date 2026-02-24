from PyQt6.QtWidgets import QWidget,QMessageBox
from PyQt6.uic import loadUi
from pathlib import Path
from app.data.data_base import Load_Save_Data
from app.controller.logic import receipt_entry_logic
from app.controller.navigator import Navigator

class Expense_Receipt_Entry(QWidget):
    def __init__(self):
        super().__init__()

        ui_path = Path(__file__).parent / "Expense_Receipt_Entry.ui"
        self.UI=loadUi(ui_path, self)

        self.setWindowTitle("Expense_Receipt_Entry")
        self.selected_image_path : list[str]=[]

        self.nav = Navigator()

        self.logic = receipt_entry_logic()
        self.UI.btnAdd.clicked.connect(self.add_images)
        self.UI.btnClear.clicked.connect(self.clear_image)
        self.UI.btnCancel.clicked.connect(self.open_dashboard)
        self.UI.btnSave.clicked.connect(self.save_record)

    def add_images(self):
        new_paths = self.logic.browse_image(parent=self, title="Add images")
        if not new_paths:
            return

        # initialize if not present
        if not hasattr(self, "selected_image_paths"):
            self.selected_image_paths = []

        # add without duplicates
        for p in new_paths:
            if p not in self.selected_image_paths:
                self.selected_image_paths.append(p)

        self.UI.lblSelectPicture.setText(f"{len(self.selected_image_paths)} image(s) selected")
        self.UI.lblSelectPicture.setToolTip("\n".join(self.selected_image_paths))


    def clear_image(self):
        self.selected_image_path = None
        self.UI.lblSelectPicture.setText("No file selected")


    def open_dashboard(self):
        self.UI.dashboard = self.nav.expense_entry_page_navigator(self)


    def save_record(self):
        data = {
            "Invoice NO": self.UI.leInvoiceNumber.text(),
            "explanation": self.UI.teExplanation.toPlainText(),
            "amount": self.UI.leExpense.text(),
            "record_date": self.UI.deDate.date().toString("yyyy-MM-dd"),
            "image_paths": "|".join(self.selected_image_paths),
            "expense_center": self.UI.cbExpenseCenter.currentText(),
            "expense_type": self.UI.cbExpenseType.currentText(),
            "company_name": self.UI.cbCompany.currentText(),
            "source_pc": "PC-1"
        }
        #try:
        Load_Save_Data().save_data(data)
        self.open_dashboard()

        #except ValueError as e:
         #   QMessageBox.warning(self, "Validation Error", str(e))

        #except Exception as e:
         #   QMessageBox.critical(self, "Error", str(e))
