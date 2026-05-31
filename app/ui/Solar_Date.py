import jdatetime

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLabel, QLineEdit, QDialog
)
from PyQt6.QtCore import Qt, pyqtSignal


PERSIAN_MONTHS = [
    "فروردین", "اردیبهشت", "خرداد",
    "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر",
    "دی", "بهمن", "اسفند"
]

PERSIAN_WEEKDAYS = [
    "ش", "ی", "د", "س", "چ", "پ", "ج"
]


class JalaliCalendarPopup(QDialog):
    date_selected = pyqtSignal(jdatetime.date)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setStyleSheet("""
        \n/* ===== Base ===== */\nQWidget {\n    background-color: #191919;\n    color: #EAEAEA;\n    font-family: "Segoe UI";\n    font-size: 13px;\n}\n\nQLabel {\n    color: #EAEAEA;\n}\n\n/* ===== GroupBox (card) ===== */\nQGroupBox {\n    background-color: #161616;\n    border: 1px solid #2A2A2A;\n    border-radius: 10px;\n    margin-top: 14px;\n    padding: 12px;\n}\n\nQGroupBox::title {\n    subcontrol-origin: margin;\n    subcontrol-position: top left;\n    left: 10px;\n    padding: 0 6px;\n    color: #EAEAEA;\n    font-weight: bold;\n}\n\n/* ===== Inputs ===== */\nQLineEdit, QComboBox, QDateEdit {\n    background-color: #1C1C1C;\n    color: #FFFFFF;\n    border: 1px solid #3A3A3A;\n    border-radius: 8px;\n    padding: 6px 10px;\n    min-height: 34px;\n}\n\nQLineEdit:focus, QComboBox:focus, QDateEdit:focus {\n    border: 2px solid #FF9800;\n}\n\n/* ===== ComboBox dropdown button ===== */\nQComboBox {\n    padding-right: 30px;\n}\n\nQComboBox::drop-down {\n    width: 26px;\n    border-left: 1px solid #3A3A3A;\n    background-color: #1C1C1C;\n}\n\nQComboBox::drop-down:hover {\n    background-color: #232323;\n}\n\n/* ===== DateEdit calendar button ===== */\nQDateEdit {\n    padding-right: 30px;\n}\n\nQDateEdit::drop-down {\n    width: 26px;\n    border-left: 1px solid #3A3A3A;\n    background-color: #FF9800;   /* calendar button color */\n}\n\nQDateEdit::drop-down:hover {\n    background-color: #FFA726;\n}\n\nQDateEdit::drop-down:pressed {\n    background-color: #F57C00;\n}\n\n/* ===== Calendar popup ===== */\nQCalendarWidget {\n    background-color: #151515;\n    color: #EAEAEA;\n    border: 1px solid #FF9800;\n}\n\nQCalendarWidget QToolButton {\n    color: #FFFFFF;\n    background-color: transparent;\n    border: none;\n    padding: 6px;\n}\n\nQCalendarWidget QToolButton:hover {\n    background-color: #232323;\n}\n\nQCalendarWidget QAbstractItemView {\n    background-color: #141414;\n    color: #EAEAEA;\n    selection-background-color: #FF9800;\n    selection-color: #111111;\n}\n\n/* ===== RadioButton ===== */\nQRadioButton {\n    color: #EAEAEA;\n    padding: 6px 4px;\n}\n\nQRadioButton::indicator {\n    width: 16px;\n    height: 16px;\n}\n\nQRadioButton::indicator:unchecked {\n    border: 2px solid #3A3A3A;\n    background-color: #1C1C1C;\n    border-radius: 8px;\n}\n\nQRadioButton::indicator:checked {\n    border: 2px solid #FF9800;\n    background-color: #FF9800;\n    border-radius: 8px;\n}\n\n/* ===== Buttons ===== */\nQPushButton {\n    background-color: transparent;\n    color: #FF9800;\n    font-weight: bold;\n    border: 2px solid #FF9800;\n    border-radius: 10px;\n    padding: 10px 14px;\n    min-height: 40px;\n}\n\nQPushButton:hover {\n    background-color: #232323;\n}\n\nQPushButton:pressed {\n    background-color: #2B2B2B;\n}\n\n/* Primary (Search) */\nQPushButton#btnSearch {\n    background-color: #FF9800;\n    color: #111111;\n    border: none;\n}\n\nQPushButton#btnSearch:hover { background-color: #FFA726; }\nQPushButton#btnSearch:pressed { background-color: #F57C00; }\n\n/* Secondary */\nQPushButton#btnSaveasexcel {\n    color: #EAEAEA;\n    border: 1px solid #3A3A3A;\n}\n\nQPushButton#btnSaveasexcel:hover {\n    background-color: #232323;\n}\n\n/* Disabled */\nQPushButton:disabled {\n    color: #777777;\n    border-color: #444444;\n}\n\n/* ===== Table ===== */\nQTableView {\n    background-color: #111827;\n    alternate-background-color: #0B1220;\n    color: #E5E7EB;\n    gridline-color: #1F2937;\n    border: 1px solid #1F2937;\n    border-radius: 8px;\n    selection-background-color: #FF9800;\n    selection-color: #111111;\n}\n\nQHeaderView::section {\n    background-color: #0F172A;\n    color: #E5E7EB;\n    padding: 8px 10px;\n    border: none;\n    border-right: 1px solid #1F2937;\n    font-weight: bold;\n}\n   
        """)

        self.setWindowTitle("انتخاب تاریخ")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        today = jdatetime.date.today()
        self.current_year = today.year
        self.current_month = today.month

        self.main_layout = QVBoxLayout(self)

        header_layout = QHBoxLayout()

        self.prev_btn = QPushButton("ماه قبل")
        self.next_btn = QPushButton("ماه بعد")
        self.title_label = QLabel()
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.prev_btn.clicked.connect(self.previous_month)
        self.next_btn.clicked.connect(self.next_month)

        header_layout.addWidget(self.prev_btn)
        header_layout.addWidget(self.title_label)
        header_layout.addWidget(self.next_btn)

        self.calendar_grid = QGridLayout()

        self.main_layout.addLayout(header_layout)
        self.main_layout.addLayout(self.calendar_grid)

        self.draw_calendar()

    def clear_grid(self):
        while self.calendar_grid.count():
            item = self.calendar_grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

    def month_length(self, year, month):
        if month <= 6:
            return 31
        elif month <= 11:
            return 30
        else:
            return 30 if jdatetime.date(year, 1, 1).isleap() else 29

    def draw_calendar(self):
        self.clear_grid()

        self.title_label.setText(
            f"{PERSIAN_MONTHS[self.current_month - 1]} {self.current_year}"
        )

        for col, name in enumerate(PERSIAN_WEEKDAYS):
            label = QLabel(name)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.calendar_grid.addWidget(label, 0, col)

        first_day = jdatetime.date(self.current_year, self.current_month, 1)

        # jdatetime weekday:
        # Saturday = 0, Sunday = 1, ..., Friday = 6
        start_col = first_day.weekday()

        days_count = self.month_length(self.current_year, self.current_month)

        row = 1
        col = start_col

        today = jdatetime.date.today()

        for day in range(1, days_count + 1):
            btn = QPushButton(str(day))

            btn.setFixedSize(55,55)

            btn.setStyleSheet("""
                QPushButton {
                    font-size: 20px;
                    font-weight: bold;
                    border: 2px solid orange;
                    border-radius: 15px;
                }

                QPushButton:hover {
                    background-color: #333;
                }
            """)

            selected_date = jdatetime.date(
                self.current_year,
                self.current_month,
                day
            )

            if selected_date == today:
                btn.setStyleSheet("""
                    QPushButton {
                        font-size: 20px;
                        font-weight: bold;
                        border: 3px solid #666;
                        border-radius: 15px;
                        background-color: #222;
                    }
                """)

            btn.clicked.connect(
                lambda checked=False, d=selected_date: self.select_date(d)
            )

            self.calendar_grid.addWidget(btn, row, col)

            col += 1
            if col > 6:
                col = 0
                row += 1

    def select_date(self, date):
        self.date_selected.emit(date)
        self.accept()

    def previous_month(self):
        self.current_month -= 1

        if self.current_month < 1:
            self.current_month = 12
            self.current_year -= 1

        self.draw_calendar()

    def next_month(self):
        self.current_month += 1

        if self.current_month > 12:
            self.current_month = 1
            self.current_year += 1

        self.draw_calendar()


class JalaliDateEdit(QWidget):
    def __init__(self):
        super().__init__()

        self.selected_jalali_date = None

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

    def get_date_from_calendar(self):
        popup = JalaliCalendarPopup(self)
        selected = None

        def on_date(d):
            nonlocal selected
            selected = d

        popup.date_selected.connect(on_date)
        popup.exec()
        if selected:
            return f"{selected.year:04d}/{selected.month:02d}/{selected.day:02d}"
        return ""

    def get_jalali_date(self):
        return self.selected_jalali_date

    def get_gregorian_date(self):
        if self.selected_jalali_date is None:
            return None

        return self.selected_jalali_date.togregorian()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Jalali Date Picker Example")
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)

        layout = QVBoxLayout(self)

        self.date_picker = JalaliDateEdit()
        self.result_label = QLabel("")

        self.submit_btn = QPushButton("نمایش تاریخ")
        self.submit_btn.clicked.connect(self.show_selected_date)

        layout.addWidget(self.date_picker)
        layout.addWidget(self.submit_btn)
        layout.addWidget(self.result_label)

    def show_selected_date(self):
        jalali = self.date_picker.get_jalali_date()
        gregorian = self.date_picker.get_gregorian_date()

        if jalali is None:
            self.result_label.setText("هیچ تاریخی انتخاب نشده است.")
            return

        self.result_label.setText(
            f"تاریخ شمسی: {jalali.year:04d}/{jalali.month:02d}/{jalali.day:02d}\n"
            f"تاریخ میلادی برای ذخیره‌سازی: {gregorian}"
        )