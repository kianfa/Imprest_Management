from pathlib import Path
from PyQt6.QtWidgets import QWidget, QDateEdit, QMessageBox
from PyQt6.QtCore import QDate
from PyQt6.uic import loadUi
from app.data.data_base import Load_Save_Data, DataBase
from app.controller.logic import receipt_entry_logic
from app.controller.navigator import Navigator
from app.data.data_base import UserSession
import re
from app.ui.Solar_Date import JalaliCalendarPopup, JalaliDateEdit
import sys
from app.data.data_base import Load_Save_Data, DataBase
from PIL import Image
import pillow_heif
pillow_heif.register_heif_opener()
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap, QImage
from PyQt6.QtWidgets import (
    QWidget, QListWidget, QListWidgetItem, QListView, QLabel
)
from app.ui.Solar_Date import JalaliDateEdit
from app.ui.Image_Preview_Dialog import ImagePreviewDialog

import re
import sys

class Expense_Receipt_Entry(QWidget):
    def __init__(self) -> None:
        super().__init__()

        if getattr(sys, 'frozen', False):
            ui_path = Path(sys._MEIPASS) / "app" / "ui" / "Expense_Receipt_Entry.ui"
        else:
            ui_path = Path(__file__).parent / "Expense_Receipt_Entry.ui"

        self.UI = loadUi(str(ui_path), self)


        self.nav = Navigator()
        self.logic = receipt_entry_logic()

        # Expense
        self.UI.leExpense.textChanged.connect(self.update_label)


        # Enhance the three combo boxes (no UI changes needed)
        self.logic.enhance_combo(self.UI.cbProjectCode,
                                 settings_key="project_code_items")
        self.logic.enhance_combo(self.UI.cbExpenseCenter,
                      settings_key="expense_center_items")
        self.logic.enhance_combo(self.UI.cbExpenseType,
                      settings_key="expense_type_items")
        self.logic.enhance_combo(self.UI.cbCompany,
                      settings_key="company_items")

        self.setWindowTitle("Expense_Receipt_Entry")

        # Enhance the combo boxes
        self.logic.enhance_combo(self.UI.cbProjectCode, settings_key="expense_center_items")
        self.logic.enhance_combo(self.UI.cbExpenseCenter, settings_key="expense_center_items")
        self.logic.enhance_combo(self.UI.cbExpenseType, settings_key="expense_type_items")
        self.logic.enhance_combo(self.UI.cbCompany, settings_key="company_items")
        # ----------------------------------------------------
        # 🖼️ Create Clean Thumbnail List (Replaces lblSelectPicture)
        # ----------------------------------------------------
        self.thumb_list = QListWidget(self)
        self.thumb_list.setViewMode(QListView.ViewMode.IconMode)
        self.thumb_list.setIconSize(QSize(110, 110))
        self.thumb_list.setGridSize(QSize(130, 145))
        self.thumb_list.setSpacing(8)
        self.thumb_list.setMovement(QListView.Movement.Static)
        self.thumb_list.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.thumb_list.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Dark modern styling with rounded thumbnails
        self.thumb_list.setStyleSheet("""
                    QListWidget {
                        background-color: #1a1a1a;
                        border: 1px solid #333333;
                        border-radius: 10px;
                        padding: 4px;
                        color: #eaeaea;
                        font-size: 11px;
                    }
                    QListWidget::item {
                        background-color: #222222;
                        border: 1px solid #3a3a3a;
                        border-radius: 8px;
                        padding: 4px;
                    }
                    QListWidget::item:hover {
                        background-color: #2e2e2e;
                        border: 1px solid #ff9800;
                    }
                    QListWidget::item:selected {
                        background-color: #383838;
                        border: 2px solid #ff9800;
                    }
                """)
        # Swap lblSelectPicture with thumb_list in the layout
        self.UI.attachRow.replaceWidget(self.UI.lblSelectPicture, self.thumb_list)
        self.UI.lblSelectPicture.deleteLater()
        # Connect double-click on any thumbnail to open the preview
        self.thumb_list.itemDoubleClicked.connect(self.open_image_preview)
        # Buttons

        self.UI.btnAdd.clicked.connect(self.add_images)
        self.UI.btnClear.clicked.connect(self.clear_image)
        self.UI.btnCancel.clicked.connect(self.open_dashboard)
        self.UI.btnSave.clicked.connect(self.save_record)
        self.UI.leExpense.textChanged.connect(self.update_label)
        self.date_picker = JalaliDateEdit()
        self.UI.leDate.mousePressEvent = lambda event: self.UI.leDate.setText(
            self.date_picker.get_date_from_calendar()
        )

    def update_label(self, text):
        # Remove any non-digit characters (allow empty string)
        digits = ''.join(filter(str.isdigit, text))
        if digits:
            # Convert to int and format with commas
            number = int(digits)
            formatted = f"{number:,}"
        else:
            formatted = ""
        self.UI.leExpense.setText(f"{formatted}")

    def add_images(self) -> None:
        self.logic.add_image_logic(self)
        self.render_thumbnails()

    def clear_image(self) -> None:
        self.logic.selected_image_paths = []
        self.thumb_list.clear()

    def render_thumbnails(self) -> None:
        self.thumb_list.clear()
        paths = getattr(self.logic, "selected_image_paths", [])
        for idx, p in enumerate(paths, start=1):
            path = Path(p)
            if not path.exists():
                continue
            # Generate high-quality undistorted thumbnail
            try:
                with Image.open(path) as img:
                    img_rgb = img.convert("RGBA")
                    data = img_rgb.tobytes("raw", "RGBA")
                    qimg = QImage(data, img_rgb.width, img_rgb.height, QImage.Format.Format_RGBA8888)
                    pix = QPixmap.fromImage(qimg)
            except Exception:
                pix = QPixmap(str(path))
            # Scale preserving exact aspect ratio
            scaled_pix = pix.scaled(
                110, 110,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            item = QListWidgetItem(QIcon(scaled_pix), f"Page {idx}\n{path.name[:12]}")
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setToolTip(str(path))
            self.thumb_list.addItem(item)

    def open_image_preview(self, event) -> None:
        paths = getattr(self.logic, "selected_image_paths", [])
        if paths:
            dialog = ImagePreviewDialog(paths, parent=self)
            dialog.exec()

    def open_dashboard(self) -> None:
        self.nav.expense_entry_page_navigator(self)

    def save_record(self) -> None:
        current_user = UserSession.username
        if self.UI.leInvoiceNumber.text() != "":
            if re.fullmatch(r"^[0-9]*$", self.UI.leInvoiceNumber.text()):
                if self.logic.duplicate_check_invoice(self.UI.leInvoiceNumber.text().strip()):
                    if self.UI.cbProjectCode.currentIndex != -1:
                        if self.UI.leExpense.text() != "":
                            if re.fullmatch(r"^[0-9]*$", self.UI.leExpense.text().replace(",", "")):
                                if self.UI.leDate.text() != "":
                                    if self.UI.cbExpenseCenter.currentIndex() != -1:
                                        if self.UI.cbCompany.currentIndex() != -1:
                                            if self.UI.cbExpenseType.currentIndex() != -1:
                                                data = {
                                                    "Invoice NO": self.UI.leInvoiceNumber.text(),
                                                    "Project_Code": self.UI.cbProjectCode.currentText(),
                                                    "explanation": self.UI.teExplanation.toPlainText(),
                                                    "amount": int(self.UI.leExpense.text().replace(",", "")),
                                                    "record_date": self.UI.leDate.text(),
                                                    "image_paths": "|".join(self.logic.selected_image_paths),
                                                    "expense_center": self.UI.cbExpenseCenter.currentText(),
                                                    "expense_type": self.UI.cbExpenseType.currentText(),
                                                    "company_name": self.UI.cbCompany.currentText(),
                                                    "source_pc": "PC-1",
                                                    "created_by": DataBase.get_user_full_name(current_user),
                                                }
                                                full_name = DataBase.get_user_full_name(current_user)
                                                Load_Save_Data().save_data(data, full_name)
                                                QMessageBox.information(None,"Success", "✓ Record saved successfully")
                                                self.clear_form()

                                            else:
                                                self.logic.show_field_error("Expense Type")
                                        else:
                                            self.logic.show_field_error("Company")
                                    else:
                                        self.logic.show_field_error("Expense Center")
                                else:
                                    self.logic.show_field_error("Date")
                            else:
                                self.logic.show_wrong_type_error("Amount")
                        else:
                            self.logic.show_field_error("Amount")
                    else:
                        self.logic.show_field_error("Project Code")
                else:
                    self.logic.show_duplicate_error("Invoice No")
            else:
                self.logic.show_wrong_type_error("Invoice No")
        else:
            self.logic.show_field_error("Invoice No")


    def clear_form(self):
        # QLineEdit
        self.UI.leExpense.clear()
        self.UI.leInvoiceNumber.clear()

        # QTextEdit / QPlainTextEdit
        self.UI.teExplanation.clear()

        # QComboBox
        self.UI.cbProjectCode.setCurrentIndex(-1)
        self.UI.cbExpenseType.setCurrentIndex(-1)
        self.UI.cbExpenseCenter.setCurrentIndex(-1)
        self.UI.cbCompany.setCurrentIndex(-1)

        # Image label
        self.clear_image()
