import sys
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QMessageBox, QComboBox, QInputDialog, QMenu, QApplication
)
from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QAction, QIcon
from PyQt6.uic import loadUi

from app.data.data_base import Load_Save_Data, ImageStore
from app.controller.logic import receipt_entry_logic
from app.controller.navigator import Navigator


def enhance_combo(combo: QComboBox, settings_key: str, default_items=None):
    """Add '+' item and right‑click removal to an existing QComboBox."""
    if default_items is None:
        default_items = []

    combo.settings_key = settings_key
    combo._special_text = "➕ Add new…"
    combo._block_selection = False
    combo._default_items = default_items

    def load_items():
        settings = QSettings('MyCompany', 'MyApp')
        items = settings.value(combo.settings_key, [])
        if not items:
            items = combo._default_items.copy()

        combo.blockSignals(True)
        combo.clear()
        if items:
            combo.addItems(items)
        combo.addItem(combo._special_text)
        combo.blockSignals(False)

    def save_items():
        items = []
        for i in range(combo.count()):
            text = combo.itemText(i)
            if text != combo._special_text:
                items.append(text)
        QSettings('MyCompany', 'MyApp').setValue(combo.settings_key, items)

    def on_index_changed(index):
        if combo._block_selection:
            return
        if combo.itemText(index) == combo._special_text:
            combo._block_selection = True
            new_item, ok = QInputDialog.getText(combo, "Add new item", "Enter item name:")
            if ok and new_item.strip():
                new_item = new_item.strip()
                if combo.findText(new_item) == -1:
                    insert_pos = combo.count() - 1  # before the special item
                    combo.insertItem(insert_pos, new_item)
                    save_items()
                    combo.setCurrentIndex(insert_pos)
                else:
                    QMessageBox.information(combo, "Duplicate", f'"{new_item}" already exists.')
            # Reset selection to first normal item
            if combo.count() > 1:
                combo.setCurrentIndex(0)
            combo._block_selection = False

    def remove_item_at_row(row):
        if row < 0 or row >= combo.count():
            return
        item_text = combo.itemText(row)
        if item_text == combo._special_text:
            return
        reply = QMessageBox.question(
            combo, "Remove item",
            f'Are you sure you want to remove "{item_text}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            combo._block_selection = True
            combo.removeItem(row)
            save_items()
            combo._block_selection = False

    def on_view_context_menu(point):
        """Called when right‑clicking inside the dropdown list."""
        view = combo.view()
        index = view.indexAt(point)
        if not index.isValid():
            return
        row = index.row()
        if combo.itemText(row) == combo._special_text:
            return
        menu = QMenu()
        remove_action = QAction("Remove", combo)
        icon = QIcon.fromTheme("edit-delete")
        if not icon.isNull():
            remove_action.setIcon(icon)
        else:
            remove_action.setText("🗑 Remove")
        remove_action.triggered.connect(lambda checked, r=row: remove_item_at_row(r))
        menu.addAction(remove_action)
        menu.exec(view.mapToGlobal(point))

    # Get the dropdown view (this creates it if necessary)
    view = combo.view()
    view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
    view.customContextMenuRequested.connect(on_view_context_menu)

    # Disconnect any previous connection to avoid duplicates
    try:
        combo.currentIndexChanged.disconnect()
    except TypeError:
        pass
    combo.currentIndexChanged.connect(on_index_changed)

    # Attach helper methods (optional)
    combo.load_items = load_items
    combo.save_items = save_items

    load_items()


class Expense_Receipt_Entry(QWidget):
    def __init__(self) -> None:
        super().__init__()
        ui_path = Path(__file__).parent / "Expense_Receipt_Entry.ui"
        self.UI = loadUi(ui_path, self)

        # Enhance the three combo boxes (no UI changes needed)
        enhance_combo(self.UI.cbExpenseCenter,
                      settings_key="expense_center_items",
                      default_items=["Center A", "Center B"])
        enhance_combo(self.UI.cbExpenseType,
                      settings_key="expense_type_items",
                      default_items=["Type 1", "Type 2"])
        enhance_combo(self.UI.cbCompany,
                      settings_key="company_items",
                      default_items=["Company X", "Company Y"])

        self.setWindowTitle("Expense_Receipt_Entry")
        self.selected_image_path: list[str] = []

        self.nav = Navigator()
        self.logic = receipt_entry_logic()

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
        data = {
            "Invoice NO": self.UI.leInvoiceNumber.text(),
            "explanation": self.UI.teExplanation.toPlainText(),
            "amount": self.UI.leExpense.text(),
            "record_date": self.UI.deDate.date().toString("yyyy-MM-dd"),
            "image_paths": "|".join(self.logic.selected_image_paths),
            "expense_center": self.UI.cbExpenseCenter.currentText(),
            "expense_type": self.UI.cbExpenseType.currentText(),
            "company_name": self.UI.cbCompany.currentText(),
            "source_pc": "PC-1"
        }
        Load_Save_Data().save_data(data)
        self.open_dashboard()