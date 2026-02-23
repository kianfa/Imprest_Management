from __future__ import annotations
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import QFileDialog, QWidget
from dataclasses import dataclass
from PyQt6.QtGui import QStandardItem, QStandardItemModel
from app.data.data_base import Load_Save_Data
from PyQt6.QtCore import Qt, QRect
from PyQt6.QtGui import QPainter, QStandardItem, QStandardItemModel, QPageSize, QPageLayout
from PyQt6.QtPrintSupport import QPrinter
from PyQt6.QtWidgets import (
    QWidget, QTableView, QFileDialog
)
from PyQt6.QtGui import QFont, QPen

class receipt_entry_logic:
    def browse_image(
            self,
            parent: QWidget,
            title: str = "Select an image",
            start_dir: Optional[str | Path] = None,
    ) -> Optional[str]:
        """
        Opens a file dialog and returns the selected image path as a string.
        Returns None if the user cancels.
        """
        start_dir_str = str(start_dir) if start_dir else ""

        file_path, _ = QFileDialog.getOpenFileName(
            parent,
            title,
            start_dir_str,
            "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp);;All Files (*)",
        )

        return file_path or None


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


    def export_tableview_to_pdf(table: QTableView, filename: str) -> None:
        model = table.model()
        if model is None:
            raise RuntimeError("Table has no model")

        # PDF Output
        printer = QPrinter(QPrinter.PrinterMode.ScreenResolution)
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        printer.setOutputFileName(filename)

        # Page settings
        printer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        printer.setPageOrientation(QPageLayout.Orientation.Portrait)

        # Font
        painter = QPainter(printer)
        painter.setPen(QPen(Qt.GlobalColor.black, 1))
        base_font = QFont(table.font())
        base_font.setPointSize(20)
        painter.setFont(base_font)

        if not painter.isActive():
            raise RuntimeError("Could not start PDF painter")

        try:
            # praintable part
            page_rect = printer.pageRect(QPrinter.Unit.DevicePixel)
            left = int(page_rect.left())
            top = int(page_rect.top())
            right = int(page_rect.right())
            bottom = int(page_rect.bottom())

            # Basic typography / spacing
            painter.setFont(table.font())
            fm = painter.fontMetrics()
            row_h = int(fm.height() + 10)
            header_h = int(row_h + 4)
            cell_pad = 6

            rows = model.rowCount()
            cols = model.columnCount()

            # Column widths (start from view widths, then scale to fit page width)
            col_widths = [max(200, table.columnWidth(c)) for c in range(cols)]
            total_w = sum(col_widths)
            avail_w = int(right - left)

            if total_w > avail_w:
                scale = avail_w / total_w
                col_widths = [max(60, int(w * scale)) for w in col_widths]
            else:
                col_widths = [int(w) for w in col_widths]

            def draw_header(y: int) -> int:
                x = left
                for c in range(cols):
                    w = col_widths[c]
                    rect = QRect(int(x), int(y), int(w), int(header_h))
                    painter.drawRect(rect)

                    text = str(model.headerData(c, Qt.Orientation.Horizontal, Qt.ItemDataRole.DisplayRole) or "")
                    painter.drawText(rect.adjusted(cell_pad, 0, -cell_pad, 0),
                                     Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, text)
                    x += w
                return y + header_h

            def new_page():
                printer.newPage()

            y = top
            y = draw_header(y)

            for r in range(rows):
                # Page break if next row doesn't fit
                if y + row_h > bottom:
                    new_page()
                    y = top
                    y = draw_header(y)

                x = left
                for c in range(cols):
                    w = col_widths[c]
                    rect = QRect(int(x), int(y), int(w), int(row_h))
                    painter.drawRect(rect)

                    idx = model.index(r, c)
                    val = model.data(idx, Qt.ItemDataRole.DisplayRole)
                    text = "" if val is None else str(val)

                    # Simple alignment heuristic: numbers right, text left
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
