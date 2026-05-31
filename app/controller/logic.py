from __future__ import annotations

import os
from dataclasses import dataclass
from email.headerregistry import Address

from openpyxl.utils import rows_from_range

from app.data.data_base import Load_Save_Data,UserSession
from PyQt6.QtGui import QStandardItem, QImage
from PyQt6.QtWidgets import (
    QFileDialog, QRadioButton, QDateEdit, QLineEdit, QTableView
)
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from typing import Optional, Union
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QMessageBox, QComboBox, QInputDialog, QMenu
)
from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QAction, QIcon
from app.ui.edit_record_dialog import EditRecordDialog
from PyQt6.QtCore import Qt, QRect, QRectF
from PyQt6.QtGui import QPainter, QPen, QFont, QImageReader, QPageSize, QPageLayout
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtCore import QMarginsF
from PyQt6.QtWidgets import QApplication
from PyQt6.QtWidgets import (
    QApplication,
    QTableView
)

from PyQt6.QtPrintSupport import QPrinter

from PyQt6.QtGui import (
    QPainter,
    QPageLayout,
    QPageSize
)

from PyQt6.QtCore import (
    QMarginsF,
    QEventLoop
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent


PathLike = Union[str, Path]



class receipt_entry_logic:
    def __init__(self):
        self.selected_image_paths = []

    def enhance_combo(self, combo: QComboBox, settings_key: str, default_items=None) -> None:
        if default_items is None:
            default_items = []

        combo.settings_key = settings_key
        combo._special_text = "➕ Add new…"
        combo._block_selection = False
        combo._default_items = default_items

        def load_items() -> None:
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

        def save_items() -> None:
            items = []
            for i in range(combo.count()):
                text = combo.itemText(i)
                if text != combo._special_text:
                    items.append(text)
            QSettings('MyCompany', 'MyApp').setValue(combo.settings_key, items)

        def on_index_changed(index) -> None:
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

        def remove_item_at_row(row) -> None:
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

        def on_view_context_menu(point) -> None:
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

    def browse_image(
            self,
            parent: QWidget,
            title: str = "add image",
            start_dir: Optional[str | Path] = None,
        ) -> list[str]:
        start_dir_str = str(start_dir) if start_dir else ""

        file_paths, _ = QFileDialog.getOpenFileNames(
            parent,
            title,
            start_dir_str,
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp);;All Files (*)",
        )

        return file_paths


    def add_image_logic(self, parent) -> None:
        new_paths = self.browse_image(parent=parent, title="Add images", start_dir="./")
        if not new_paths:
            return

        # initialize if not present
        if not hasattr(self, "selected_image_paths"):
            self.selected_image_paths = []

        # add without duplicates
        for p in new_paths:
            if p not in self.selected_image_paths:
                self.selected_image_paths.append(p)

    def show_field_error(self, field_name) -> None:
        QMessageBox.warning(None,"Input Error", f"Field '{field_name}' cannot be empty.")

    def show_duplicate_error(self, invoice_number) -> None:
        QMessageBox.warning(None, "Duplicate Invoice",
                            f"'{invoice_number}' already exists.\nPlease use a unique number.")

    def show_wrong_type_error(self, field_name) -> None:
        QMessageBox.warning(None, "Wrong Type", f"Field '{field_name}' is not a number.")

    def duplicate_check_invoice(self, number) -> bool:
        db = Load_Save_Data()
        if db.invoice_exists(number):
            return False
        return True

    def duplicate_check_project(self, number) -> bool:
        db = Load_Save_Data()
        if db.project_exists(number):
            return False
        return True

from app.data.data_base import DataBase

@dataclass
class LoginResult:
    ok: bool
    role: str = ""
    error_message: str = ""

class main_window_logic:
    @staticmethod
    def validate_inputs(username: str, password: str) -> LoginResult:
        if not username:
            return LoginResult(False, error_message="Username cannot be empty.")
        if not password:
            return LoginResult(False, error_message="Password cannot be empty.")
        return LoginResult(True)

    @classmethod
    def login(cls, username: str, password: str) -> LoginResult:
        # Step 1: validate input
        validation = cls.validate_inputs(username, password)
        if not validation.ok:
            return validation

        # Step 2: verify against database
        success, role = DataBase.verify_login(username, password)
        if success:
            return LoginResult(True, role)
        else:
            return LoginResult(False, error_message="Incorrect username or password.")




class calling_page_logic:
    def __init__(self) ->None:
        super().__init__()

    def load_invoices(self,
                      rbi : QRadioButton, lei : QLineEdit,
                      rbp : QRadioButton, lep: QLineEdit,
                      rbt : QRadioButton, delogins : QDateEdit, delogine : QDateEdit,
                      rbrd : QRadioButton, derd : QDateEdit,
                      lee : QLineEdit) -> None:
        # Your repo functions return (headers, rows), so we ignore headers
        if rbi.isChecked():
            rows = Load_Save_Data.get_invoices_by_Invoice_NO(lei.text().strip())

        elif rbp.isChecked():
            rows = Load_Save_Data.get_invoices_by_Project_Code(lep.text().strip())

        elif rbt.isChecked():
            date_str_start = delogins.date().toString("yyyy-MM-dd")
            date_str_end = delogine.date().toString("yyyy-MM-dd")
            rows = Load_Save_Data.get_invoices_by_time_range(date_str_start, date_str_end)

        elif rbrd.isChecked():
            date_str = derd.date().toString("yyyy-MM-dd")
            rows = Load_Save_Data.get_invoices_by_regestrationdate(date_str)

        else:  # rbExplanation
            rows = Load_Save_Data.get_invoices_by_explanation(lee.text().strip())

        # Clear + keep the static first row
        self.model.clear()
        self.model.setColumnCount(len(self.headers))
        self.model.setHorizontalHeaderLabels([""] * len(self.headers))

        # Header row (first row in the model)
        header_items = []
        for h in self.headers:
            item = QStandardItem(h)
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            header_items.append(item)
        self.model.appendRow(header_items)

        # Data rows
        for row in rows:
            items = []
            for v in row:
                if isinstance(v, float):
                    item = QStandardItem(f"{int(v):,}")
                else:
                    item = QStandardItem("" if v is None else str(v))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                items.append(item)
            self.model.appendRow(items)

        # Hide id column (column 0)
        self.tableView.setColumnHidden(0, True)


    def edit_record(self, table: QTableView) -> None:
        selected = table.selectedIndexes()
        if not selected:
            QMessageBox.warning(None, "No Selection", "Please select a record to edit.")
            return

        row = selected[0].row()
        record_id = self.model.item(row, 0).text()
        created_by = self.model.item(row, 9).text()

        if UserSession.role != 'admin' and created_by != UserSession.full_name:
            QMessageBox.warning(None, "Permission Denied", "You can only edit your own records.")
            return

        record_data = Load_Save_Data().get_record_by_id(record_id)
        if not record_data:
            QMessageBox.critical(None, "Error", "Record not found.")
            return

        dialog = EditRecordDialog(record_data)
        if dialog.exec():
            updated = dialog.get_updated_data()
            DataBase.update_record(record_id, updated)

    def delete_record(self, table: QTableView) -> None:
        # Get selected row
        selected = table.selectedIndexes()
        if not selected:
            QMessageBox.warning(None, "No Selection", "Please select a record to delete.")
            return

        row = selected[0].row()
        record_id = self.model.item(row, 0).text()
        created_by = self.model.item(row, 8).text()

        # Permission check
        if UserSession.role != 'admin' and created_by != UserSession.full_name:
            QMessageBox.warning(None, "Permission Denied", "You can only delete your own records.")
            return

        # Confirmation dialog
        reply = QMessageBox.question(None, "Confirm Delete",
                                     "Are you sure you want to delete this record?\nThis action cannot be undone.",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            Load_Save_Data.soft_delete_record(record_id)
            QMessageBox.information(None, "Deleted", "Record has been deleted.")




class exporting:
    def __init__(self) -> None:
        super().__init__()

    def export_table_to_pdf(self, table, file_path):
        # Create hidden export view
        export_view = QTableView()
        model = table.model()

        # Reuse SAME model
        export_view.setModel(table.model())

        # Copy appearance
        export_view.setFont(table.font())
        export_view.setStyleSheet(table.styleSheet())

        # copy column widths
        for col in range(table.model().columnCount()):
            export_view.setColumnWidth(
                col,
                table.columnWidth(col)
            )

        # Printer
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)

        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)

        printer.setOutputFileName(file_path)

        printer.setPageSize(
            QPageSize(QPageSize.PageSizeId.A4)
        )

        printer.setPageOrientation(
            QPageLayout.Orientation.Landscape
        )

        printer.setPageMargins(
            QMarginsF(10, 10, 10, 10)
        )

        #
        # Painter
        #

        painter = QPainter()

        if not painter.begin(printer):
            raise RuntimeError("Could not create printer")

        # Resize export view
        export_view.resizeColumnsToContents()
        export_view.resizeRowsToContents()

        export_view.setFixedHeight(
            export_view.horizontalHeader().height()
            + export_view.verticalHeader().length()
            + 4
        )

        export_view.setFixedWidth(
            export_view.verticalHeader().width()
            + export_view.horizontalHeader().length()
            + 4
        )

        QApplication.processEvents(
            QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents
        )

        export_view.setColumnHidden(0, True)

        # PAGE 1 → FULL TABLE
        painter.save()

        scale = 13

        painter.scale(scale, scale)

        export_view.render(painter)

        painter.restore()

        printer.newPage()

        # NEXT PAGES → ONE ROW EACH
        row_count = table.model().rowCount()

        for row in range(1, row_count):

            # Hide all rows
            export_view.setUpdatesEnabled(False)

            for r in range(row_count):
                export_view.setRowHidden(r, True)

            # Show rows needed
            export_view.setRowHidden(0, False)
            export_view.setColumnHidden(0, True)
            export_view.setRowHidden(row, False)

            export_view.setUpdatesEnabled(True)

            # Tight resize
            export_view.setFixedHeight(
                export_view.horizontalHeader().height()
                + export_view.rowHeight(0)
                + export_view.rowHeight(row)
                + 10
            )

            # Process events
            QApplication.processEvents(
                QEventLoop.ProcessEventsFlag.ExcludeUserInputEvents
            )

            # image
            index = model.index(row, 0)

            id = str(model.data(index)).strip()
            images_path = BASE_DIR / "image_records" / id

            image_files=[]
            for file in os.listdir(images_path):
                if file.lower().endswith((
                        ".png",
                        ".jpg",
                        ".jpeg",
                        ".bmp",
                        ".webp"
                )):
                    image_files.append(file)

            # render table
            painter.save()

            painter.scale(scale, scale)

            export_view.render(painter)

            painter.restore()

            # Start images BELOW scaled table
            table_height = export_view.height() * scale

            x = 500
            y = table_height

            page_rect = printer.pageRect(
                QPrinter.Unit.DevicePixel
            )

            page_height = page_rect.height()

            for file in image_files:
                full_path = images_path / file

                image = QImage(str(full_path))

                scaled = image.scaled(
                    7000,
                    7000,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )

                if y + scaled.height() > page_height:
                    printer.newPage()

                    y = 500

                painter.drawImage(x, y, scaled)

                y += scaled.height() + 40

            # Next page
            if row < row_count - 1:
                printer.newPage()

        # Finish
        painter.end()

        export_view.deleteLater()




    def export_tableview_to_excel(self, view) -> None:
        model = view.model()
        header = view.horizontalHeader()

        if model is None:
            raise RuntimeError("Could not find model")

        #columns
        export_col = []
        for visual in range(header.count()):
            logical = header.logicalIndex(visual)
            if 0<= logical < model.columnCount():
                export_col.append(logical)

        if export_col is None:
            raise RuntimeError("Could not find column")

        #building Excel file
        wb = Workbook()
        ws = wb.active
        ws.title = "Export Table"

        header_font = Font(bold=True)
        header_align = Alignment(horizontal="center", vertical="center", wrap_text=True)

        for out_col, logical_col in enumerate(export_col, start=1):
            title = model.headerData(logical_col, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
            text = "" if title is None else str(title)

            cell = ws.cell(row=1, column=out_col, value=text)
            cell.font = header_font
            cell.alignment = header_align

        ws.freeze_panes = "A2"

        #write all visible data rows
        start_excel_row = 2
        rows = model.rowCount()

        for r in range(rows):
            excel_row = start_excel_row + r

            for excel_col, logical_col in enumerate(export_col, start=1):
                idx = model.index(r, logical_col)
                value = model.data(idx, Qt.ItemDataRole.DisplayRole)
                if value is None:
                    state = model.data(idx, Qt.CheckStateRole)
                    if state is not None:
                        value = "✓" if state == Qt.Checked else "✗"
                    else:
                        value = ""

                ws.cell(row=excel_row, column=excel_col, value=str(value))

        #Fixing the width of cells for readability
        from openpyxl.utils import get_column_letter

        max_lens = [0] * len(export_col)

        for row in ws.iter_rows(min_row=1, max_row=ws.max_row,
                                min_col=1, max_col=len(export_col)):
            for i, cell in enumerate(row):
                v = cell.value
                if v is None:
                    continue
                s = str(v)
                if len(s) > max_lens[i]:
                    max_lens[i] = len(s)

        for i, m in enumerate(max_lens, start=1):
            col_letter = get_column_letter(i)
            width = max(10, min(60, m + 2))
            ws.column_dimensions[col_letter].width = width

        # Step 6: Save dialog + save workbook + error handling
        parent = view.window()
        path, _ = QFileDialog.getSaveFileName(
            parent,
            "Save Excel",
            "Export.xlsx",
            "Excel Workbook (*.xlsx)"
        )

        if not path:
            return  # user cancelled

        if not path.lower().endswith(".xlsx"):
            path += ".xlsx"

        try:
            wb.save(path)
        except PermissionError:
            QMessageBox.warning(
                self,
                "Save failed",
                "Could not write the file.\n"
                "If it's open in Excel, close it and try again, or choose another location."
            )
            return
        except OSError as e:
            QMessageBox.critical(
                self,
                "Save failed",
                f"OS error while saving the file:\n{e}"
            )
            return
        except Exception as e:
            QMessageBox.critical(
                self,
                "Save failed",
                f"Unexpected error while saving the file:\n{e}"
            )
            return
