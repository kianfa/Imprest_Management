import sys
from pathlib import Path
from PyQt6.QtWidgets import QWidget
from PyQt6.uic import loadUi
from app.data.data_base import Load_Save_Data, DataBase
from app.controller.logic import receipt_entry_logic
from app.controller.navigator import Navigator
from app.data.data_base import UserSession
import re



class Expense_Receipt_Entry(QWidget):
    def __init__(self) -> None:
        super().__init__()
        ui_path = Path(__file__).parent / "Expense_Receipt_Entry.ui"
        self.UI = loadUi(ui_path, self)


        self.nav = Navigator()
        self.logic = receipt_entry_logic()

        # Enhance the three combo boxes (no UI changes needed)
        self.logic.enhance_combo(self.UI.cbExpenseCenter,
                      settings_key="expense_center_items")
        self.logic.enhance_combo(self.UI.cbExpenseType,
                      settings_key="expense_type_items")
        self.logic.enhance_combo(self.UI.cbCompany,
                      settings_key="company_items")

        self.setWindowTitle("Expense_Receipt_Entry")
        self.selected_image_path: list[str] = []


        self.UI.btnAdd.clicked.connect(self.add_images)
        self.UI.btnClear.clicked.connect(self.clear_image)
        self.UI.btnCancel.clicked.connect(self.open_dashboard)
        self.UI.btnSave.clicked.connect(self.save_record)

    def add_images(self) -> None:
        self.logic.add_image_logic(self)
        self.UI.lblSelectPicture.setText(f"{len(self.logic.selected_image_paths)} image(s) selected")
        self.UI.lblSelectPicture.setToolTip("\n".join(self.logic.selected_image_paths))

    def clear_image(self) -> None:
        self.selected_image_path = None
        self.UI.lblSelectPicture.setText("No file selected")

    def open_dashboard(self) -> None:
        self.nav.expense_entry_page_navigator(self)

    def save_record(self) -> None:
        current_user = UserSession.username
        if self.UI.leInvoiceNumber.text() != "":
            if re.fullmatch(r"^[0-9]*$", self.UI.leInvoiceNumber.text()):
                if self.logic.duplicate_check_invoice(self.UI.leInvoiceNumber.text().strip()):
                    if self.UI.le_Project_Code.text() != "":
                        if re.fullmatch(r"^[0-9]*$", self.UI.le_Project_Code.text()):
                            if self.logic.duplicate_check_project(self.UI.le_Project_Code.text().strip()):
                                if self.UI.leExpense.text() != "":
                                    if re.fullmatch(r"^[0-9]*$", self.UI.leExpense.text()):
                                        if self.UI.cbExpenseCenter.currentIndex() != -1:
                                            if self.UI.cbCompany.currentIndex() != -1:
                                                if self.UI.cbExpenseType.currentIndex() != -1:
                                                    data = {
                                                        "Invoice NO": self.UI.leInvoiceNumber.text(),
                                                        "Project_Code": self.UI.le_Project_Code.text(),
                                                        "explanation": self.UI.teExplanation.toPlainText(),
                                                        "amount": self.UI.leExpense.text(),
                                                        "record_date": self.UI.deDate.date().toString("yyyy-MM-dd"),
                                                        "image_paths": "|".join(self.logic.selected_image_paths),
                                                        "expense_center": self.UI.cbExpenseCenter.currentText(),
                                                        "expense_type": self.UI.cbExpenseType.currentText(),
                                                        "company_name": self.UI.cbCompany.currentText(),
                                                        "source_pc": "PC-1",
                                                        "created_by": DataBase.get_user_full_name(current_user),
                                                    }
                                                    full_name = DataBase.get_user_full_name(current_user)
                                                    Load_Save_Data().save_data(data, full_name)
                                                    self.open_dashboard()
                                                else:
                                                    self.logic.show_field_error("Expense Type")
                                            else:
                                                self.logic.show_field_error("Company")
                                        else:
                                            self.logic.show_field_error("Expense Center")
                                    else:
                                        self.logic.show_wrong_type_error("Amount")
                                else:
                                    self.logic.show_field_error("Amount")
                            else:
                                  self.logic.show_duplicate_error("Project Code")
                        else:
                            self.logic.show_wrong_type_error("Project Code")
                    else:
                        self.logic.show_field_error("Project Code")
                else:
                    self.logic.show_duplicate_error("Invoice No")
            else:
                self.logic.show_wrong_type_error("Invoice No")
        else:
            self.logic.show_field_error("Invoice No")