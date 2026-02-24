from __future__ import annotations
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from app.data.data_base import Load_Save_Data, DataBase
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QStandardItem, QStandardItemModel, QPageSize, QPageLayout
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtWidgets import (
    QWidget, QTableView, QFileDialog, QMessageBox
)
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from PyQt6.QtCore import Qt, QRect, QFile
from PyQt6.QtGui import QPainter, QPen, QFont, QImage
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtGui import QPageSize, QPageLayout
from PyQt6.QtWidgets import QTableView



class receipt_entry_logic:
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
        # Your repo functions return (headers, rows), so we ignore headers
        if self.rbInvoiceNo.isChecked():
            rows = Load_Save_Data.get_invoices_by_Invoice_NO(self.leInvoiceNo.text().strip())


        elif self.rbTimeRange.isChecked():
            date_str_start = self.deLoginStart.date().toString("yyyy-MM-dd")
            date_str_end = self.deLoginEnd.date().toString("yyyy-MM-dd")
            rows = Load_Save_Data.get_invoices_by_time_range(date_str_start, date_str_end)

        elif self.rbRegistrationDate.isChecked():
            date_str = self.deRegstrationDate.date().toString("yyyy-MM-dd")
            rows = Load_Save_Data.get_invoices_by_regestrationdate(date_str)

        else:  # rbExplanation
            rows = Load_Save_Data.get_invoices_by_explanation(self.leExplanation.text().strip())

        # Clear + keep the static first row
        self.model.clear()
        self.model.setColumnCount(len(self.headers))
        self.model.setHorizontalHeaderLabels([""] * len(self.headers))
        self.model.appendRow([QStandardItem(h) for h in self.headers])

        # Fill DB rows cell-by-cell
        for row in rows:
            items = [QStandardItem("" if v is None else str(v)) for v in row]
            self.model.appendRow(items)

    def populate_table(self, rows):
        model = QStandardItemModel()
        model.setHorizontalHeaderLabels([
            "Invoice No","amount" , "Explanation",
            "Registration Date", "Login Date"
        ])

        for row in rows:
            model.appendRow(
                [QStandardItem(str(col)) for col in row]
            )

        self.tableView.setModel(model)



    def export_tableview_to_pdf(table: QTableView, filename: str, image_col_name: str = "image_path") -> None:
        model = table.model()
        if model is None:
            raise RuntimeError("Table has no model")

        printer = QPrinter(QPrinter.PrinterMode.ScreenResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(filename)

        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        printer.setPageOrientation(QPageLayout.Orientation.Portrait)

        painter = QPainter(printer)
        painter.setPen(QPen(Qt.GlobalColor.black, 1))

        if not painter.isActive():
            raise RuntimeError("Could not start PDF painter")

        try:
            page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)
            left = int(page_rect.left())
            top = int(page_rect.top())
            right = int(page_rect.right())
            bottom = int(page_rect.bottom())
            avail_w = int(right - left)

            painter.setFont(table.font())
            fm = painter.fontMetrics()
            row_h = int(fm.height() + 10)
            header_h = int(row_h + 4)
            cell_pad = 6

            rows = model.rowCount()
            cols = model.columnCount()

            col_widths = [max(200, table.columnWidth(c)) for c in range(cols)]
            total_w = sum(col_widths)

            if total_w > avail_w:
                scale = avail_w / total_w
                col_widths = [max(60, int(w * scale)) for w in col_widths]
            else:
                col_widths = [int(w) for w in col_widths]

            def draw_table_header(y: int) -> int:
                x = left
                for c in range(cols):
                    w = col_widths[c]
                    rect = QRect(int(x), int(y), int(w), int(header_h))
                    painter.drawRect(rect)

                    text = str(model.headerData(c, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole) or "")
                    painter.drawText(
                        rect.adjusted(cell_pad, 0, -cell_pad, 0),
                        Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
                        text
                    )
                    x += w
                return y + header_h

            def new_page():
                printer.newPage()

            # ---------- DRAW TABLE ----------
            y = top
            y = draw_table_header(y)

            for r in range(rows):
                if y + row_h > bottom:
                    new_page()
                    y = top
                    y = draw_table_header(y)

                x = left
                for c in range(cols):
                    w = col_widths[c]
                    rect = QRect(int(x), int(y), int(w), int(row_h))
                    painter.drawRect(rect)

                    idx = model.index(r, c)
                    val = model.data(idx, Qt.ItemDataRole.DisplayRole)
                    text = "" if val is None else str(val)

                    align = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
                    try:
                        float(text)
                        align = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight
                    except Exception:
                        pass

                    painter.drawText(rect.adjusted(cell_pad, 0, -cell_pad, 0), align, text)
                    x += w

                y += row_h
        finally:
            painter.end()


    def export_tableview_to_excel(self, view):
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
