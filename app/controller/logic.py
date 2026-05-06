from __future__ import annotations
from dataclasses import dataclass
from app.data.data_base import Load_Save_Data
from PyQt6.QtGui import QStandardItem
from PyQt6.QtWidgets import (
    QFileDialog, QRadioButton, QDateEdit, QLineEdit
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



PathLike = Union[str, Path]



class receipt_entry_logic:
    def __init__(self):
        self.selected_image_paths = []

    def enhance_combo(self, combo: QComboBox, settings_key: str, default_items=None) -> None:
        """Add '+' item and right‑click removal to an existing QComboBox."""
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
                            f"'{invoice_number}' already exists.\nPlease use a unique invoice number.")

    def show_wrong_type_error(self, field_name) -> None:
        QMessageBox.warning(None, "Wrong Type", f"Field '{field_name}' is not a number.")

    def duplicate_check(self, invoice) -> bool:
        db = Load_Save_Data()
        if db.invoice_exists(invoice):
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
            return LoginResult(True, role=role)
        else:
            return LoginResult(False, error_message="Incorrect username or password.")




class calling_page_logic:
    def __init__(self) ->None:
        super().__init__()

    def load_invoices(self, rbi : QRadioButton, rbt : QRadioButton,
                      lei : QLineEdit, delogins : QDateEdit, delogine : QDateEdit,
                      rbrd : QRadioButton, derd : QDateEdit,
                      lee : QLineEdit) -> None:
        # Your repo functions return (headers, rows), so we ignore headers
        if rbi.isChecked():
            rows = Load_Save_Data.get_invoices_by_Invoice_NO(lei.text().strip())

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
        self.model.appendRow([QStandardItem(h) for h in self.headers])

        # Fill DB rows cell-by-cell
        for row in rows:
            items = [QStandardItem("" if v is None else str(v)) for v in row]
            self.model.appendRow(items)




class exporting:
    def __init__(self) -> None:
        super().__init__()

    def export_tableview_to_pdf(
            self,
            table,
            filename: str,
            image_col_name: str = "image_path",  # ← column header name, not a path!
            extra_image_sources=None,
            recursive: bool = False,
            base_dir: str | None = None,  # ← set this to your images root if paths are relative
    ) -> None:
        """
        1) Exports the QTableView as a simple grid table into PDF (A4 portrait).
        2) Appends images (one per page) collected from:
           - the model column whose header == image_col_name
           - extra_image_sources (string / Path / list)
           - fallback: self.sending_img_path() if available
        """

        # ---- Qt imports ----
        from PyQt6.QtCore import Qt, QRect, QRectF
        from PyQt6.QtGui import QPainter, QPen, QFont, QImageReader, QPageSize, QPageLayout
        from PyQt6.QtPrintSupport import QPrinter
        from pathlib import Path
        import ast
        from typing import Optional

        model = table.model()
        if model is None:
            raise RuntimeError("Table has no model")

        # ----------------------------
        # Printer setup
        # ----------------------------
        printer = QPrinter(QPrinter.PrinterMode.HighResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(filename)
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        printer.setPageOrientation(QPageLayout.Orientation.Portrait)
        printer.setResolution(300)

        painter = QPainter()
        if not painter.begin(printer):
            raise RuntimeError("Could not start PDF painter")

        try:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
            painter.setPen(QPen(Qt.GlobalColor.black, 1))

            # ----------------------------
            # Small helpers
            # ----------------------------
            def pt_to_px_x(pt: float) -> int:
                return int(pt * printer.logicalDpiX() / 72.0)

            def pt_to_px_y(pt: float) -> int:
                return int(pt * printer.logicalDpiY() / 72.0)

            margin_x = pt_to_px_x(24)
            margin_y = pt_to_px_y(24)

            def page_box() -> tuple:
                page = printer.pageRect(QPrinter.Unit.DevicePixel)
                left = int(page.left() + margin_x)
                top = int(page.top() + margin_y)
                right = int(page.right() - margin_x)
                bottom = int(page.bottom() - margin_y)
                return left, top, right, bottom

            def _clean(s) -> str:
                s = str(s).strip().strip('"').strip("'").strip()
                if s.startswith("file:///"):
                    s = s.replace("file:///", "")
                return s

            def _flatten(v) -> list:
                if v is None:
                    return []
                if isinstance(v, Path):
                    return [str(v)]
                if isinstance(v, (list, tuple, set)):
                    out = []
                    for x in v:
                        out.extend(_flatten(x))
                    return out
                if isinstance(v, str):
                    s = _clean(v)
                    if (s.startswith("[") and s.endswith("]")) or (s.startswith("(") and s.endswith(")")):
                        try:
                            return _flatten(ast.literal_eval(s))
                        except Exception:
                            return [s]
                    return [s]
                return [_clean(v)]

            def _resolve_path(s: str, base: Path | None) -> Path:
                p = Path(s)
                if p.is_absolute():
                    return p
                return (base / p) if base else p

            def find_col_by_header(name: str) -> Optional[int]:
                for c in range(model.columnCount()):
                    h = model.headerData(c, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole)
                    if h is not None and str(h) == name:
                        return c
                return None

            # ----------------------------
            # Draw table (simple equal-width columns)
            # ----------------------------
            base_family = table.font().family()
            painter.setFont(QFont(base_family, 10))
            fm = painter.fontMetrics()

            left, top, right, bottom = page_box()
            rows, cols = model.rowCount(), model.columnCount()

            if cols > 0:
                cell_pad = pt_to_px_x(4)
                row_h = int(fm.height() + pt_to_px_y(10))
                header_h = int(fm.height() + pt_to_px_y(12))

                avail_w = right - left
                base_w = max(1, avail_w // cols)
                col_widths = [base_w] * cols
                col_widths[-1] += (avail_w - sum(col_widths))

                def draw_header(y: int) -> int:
                    x = left
                    for c in range(cols):
                        w = col_widths[c]
                        rect = QRect(x, y, w, header_h)
                        painter.drawRect(rect)
                        text = str(model.headerData(c, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole) or "")
                        painter.drawText(
                            rect.adjusted(cell_pad, 0, -cell_pad, 0),
                            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                            text
                        )
                        x += w
                    return y + header_h

                y = top
                y = draw_header(y)

                for r in range(rows):
                    if y + row_h > bottom:
                        printer.newPage()
                        left, top, right, bottom = page_box()
                        y = top
                        y = draw_header(y)

                    x = left
                    for c in range(cols):
                        w = col_widths[c]
                        rect = QRect(x, y, w, row_h)
                        painter.drawRect(rect)

                        val = model.data(model.index(r, c), Qt.ItemDataRole.DisplayRole)
                        text = "" if val is None else str(val)

                        painter.drawText(
                            rect.adjusted(cell_pad, 0, -cell_pad, 0),
                            Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                            text
                        )
                        x += w

                    y += row_h

            # ----------------------------
            # Collect image sources (robust)
            # ----------------------------
            # Determine base directory
            if base_dir is None:
                # Default fallback (change this to your actual default or keep None to force absolute)
                base = Path(r"D:\Work\Imprest_Management\Imprest_Management_Forked\image_records")
            else:
                base = Path(base_dir)

            sources = []

            # From model column
            img_col = find_col_by_header(image_col_name)
            if img_col is not None:
                for r in range(rows):
                    idx = model.index(r, img_col)
                    v = model.data(idx, Qt.ItemDataRole.DisplayRole)
                    if not v:
                        v = model.data(idx, Qt.ItemDataRole.EditRole)
                    if not v:
                        v = model.data(idx, Qt.ItemDataRole.UserRole)
                    sources.extend(_flatten(v))

            # Extra sources
            if extra_image_sources:
                sources.extend(_flatten(extra_image_sources))

            # Fallback like your original
            if not sources:
                try:
                    sources.extend(_flatten(self.sending_img_path()))
                except Exception:
                    pass

            # Expand sources -> actual files
            files = []
            for s in sources:
                s = _clean(s)
                if not s:
                    continue

                p = _resolve_path(s, base)

                if p.is_dir():
                    it = p.rglob("*") if recursive else p.iterdir()
                    for f in it:
                        if f.is_file():
                            files.append(f)
                elif p.is_file():
                    files.append(p)

            # Filter readable images
            readable = []
            for f in sorted(set(files)):
                r = QImageReader(str(f))
                r.setAutoTransform(True)
                try:
                    r.setDecideFormatFromContent(True)
                except Exception:
                    pass
                if r.canRead():
                    readable.append(f)

            # ----------------------------
            # Append images (one per page) or show debug page
            # ----------------------------
            if not readable:
                printer.newPage()
                left_d, top_d, right_d, bottom_d = page_box()
                msg_rect = QRect(left_d, top_d, right_d - left_d, pt_to_px_y(320))
                painter.drawText(
                    msg_rect,
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
                    "No readable images were found.\n\n"
                    f"image_col_name = {image_col_name}\n"
                    f"base_dir = {base}\n\n"
                    "First sources:\n- " + "\n- ".join([str(x) for x in sources[:20]])
                )
            else:
                for img_path in readable:
                    printer.newPage()
                    left_i, top_i, right_i, bottom_i = page_box()
                    target = QRectF(left_i, top_i, right_i - left_i, bottom_i - top_i)

                    reader = QImageReader(str(img_path))
                    reader.setAutoTransform(True)
                    try:
                        reader.setDecideFormatFromContent(True)
                    except Exception:
                        pass

                    img = reader.read()
                    if img.isNull():
                        continue

                    iw, ih = img.width(), img.height()
                    scale = min(target.width() / iw, target.height() / ih)
                    dw, dh = iw * scale, ih * scale
                    x = target.x() + (target.width() - dw) / 2
                    y = target.y() + (target.height() - dh) / 2
                    painter.drawImage(QRectF(x, y, dw, dh), img)

        finally:
            painter.end()

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
