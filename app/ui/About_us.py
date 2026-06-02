from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QFont
from app.main import main

STYLE = """
QDialog {
    background-color: #1C1C1C;
}
QLabel {
    color: #EAEAEA;
    background: transparent;
}
QFrame#card {
    background-color: #161616;
    border: 1px solid #2A2A2A;
    border-radius: 12px;
}
QFrame#divider {
    background-color: #2A2A2A;
    max-height: 1px;
    min-height: 1px;
    border: none;
}
QPushButton {
    background-color: transparent;
    color: #AAAAAA;
    border: 1px solid #2A2A2A;
    border-radius: 8px;
    padding: 4px 10px;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #232323;
    color: #EAEAEA;
}
"""

def avatar_label(initials: str, bg: str, fg: str) -> QLabel:
    lbl = QLabel(initials)
    lbl.setFixedSize(40, 40)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setFont(QFont("Segoe UI", 13, QFont.Weight.Medium))
    lbl.setStyleSheet(
        f"background-color:{bg}; color:{fg}; border-radius:20px; font-weight:500;"
    )
    return lbl


def link_button(icon: str, text: str, url: str) -> QPushButton:
    btn = QPushButton(f"{icon}  {text}")
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl(url)))
    return btn


def person_row(initials, bg, fg, name, role, links) -> QHBoxLayout:
    row = QHBoxLayout()
    row.setSpacing(14)
    row.setContentsMargins(0, 0, 0, 0)

    row.addWidget(avatar_label(initials, bg, fg), alignment=Qt.AlignmentFlag.AlignTop)

    info = QVBoxLayout()
    info.setSpacing(2)

    name_lbl = QLabel(name)
    name_lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Medium))
    name_lbl.setStyleSheet("color:#EAEAEA; font-weight:500;")
    info.addWidget(name_lbl)

    role_lbl = QLabel(role)
    role_lbl.setFont(QFont("Segoe UI", 12))
    role_lbl.setStyleSheet("color:#888888;")
    info.addWidget(role_lbl)

    info.addSpacing(8)

    badges = QHBoxLayout()
    badges.setSpacing(8)
    badges.setContentsMargins(0, 0, 0, 0)
    for icon, label, url in links:
        badges.addWidget(link_button(icon, label, url))
    badges.addStretch()
    info.addLayout(badges)

    row.addLayout(info)
    return row


class AboutDialog(QDialog):
    def __init__(self, parent=None, previous_window=None):
        super().__init__(parent)
        self.previous_window = previous_window
        self.setWindowTitle("About Us")
        self.setFixedWidth(500)
        self.setStyleSheet(STYLE)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 20, 20, 20)

        # ── Card ──────────────────────────────────────────
        card = QFrame()
        card.setObjectName("card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 20)
        card_layout.setSpacing(0)

        # Header
        tag = QLabel("ABOUT US")
        tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tag.setStyleSheet(
            "color:#666666; font-size:11px; letter-spacing:2px; margin-bottom:6px;"
        )
        card_layout.addWidget(tag)

        title = QLabel("Imprest Management")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Segoe UI", 18, QFont.Weight.Medium))
        title.setStyleSheet("color:#EAEAEA;")
        card_layout.addWidget(title)

        subtitle = QLabel("Enterprise Imprest Management · v1.0.0")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle.setStyleSheet("color:#888888; font-size:13px; margin-top:4px;")
        card_layout.addWidget(subtitle)

        card_layout.addSpacing(20)

        # Top divider
        top_div = QFrame()
        top_div.setObjectName("divider")
        card_layout.addWidget(top_div)

        card_layout.addSpacing(20)

        # ── Developer 1 ───────────────────────────────────
        dev1_links = [
            ("⌥", "GitHub",   "https://github.com/NozhanQ"),
            ("in", "LinkedIn", "https://www.linkedin.com/in/nozhan-ghayati-716b94243/"),
            ("✈",  "Telegram", "https://t.me/MrGhayati"),
            ("@",  "Email",    "mailto:ghayati2006@gmail.com"),
        ]
        card_layout.addLayout(
            person_row("NG", "#1A3A5C", "#5B9BD5",
                       "Nozhan Ghayati", "Lead Developer", dev1_links)
        )

        card_layout.addSpacing(20)

        # Mid divider
        mid_div = QFrame()
        mid_div.setObjectName("divider")
        card_layout.addWidget(mid_div)

        card_layout.addSpacing(20)

        # ── Developer 2 ───────────────────────────────────
        dev2_links = [
            ("⌥", "GitHub",   "https://github.com/kianfa"),
            ("in", "LinkedIn", "https://www.linkedin.com/in/kian-farooghi-1838aa1b9?originalSubdomain=ir"),
            ("✈",  "Telegram", "https://t.me/kian_emc"),
            ("@",  "Email",    "mailto:kainfarooghi@gmail.com"),
        ]
        card_layout.addLayout(
            person_row("KF", "#1A3D2B", "#4CAF82",
                       "Kian Farooghi", "Project Manager & QA", dev2_links)
        )

        card_layout.addSpacing(20)

        # Footer
        footer = QLabel("© 2026 Imprest Management. All rights reserved.")
        footer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        footer.setStyleSheet("color:#555555; font-size:11px; margin-top:4px;")
        card_layout.addWidget(footer)

        outer.addWidget(card)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.setFixedHeight(36)
        close_btn.clicked.connect(self.go_back)
        outer.addWidget(close_btn)

    def go_back(self):
        if self.previous_window:
            self.previous_window.show()
        self.close()
