from pathlib import Path
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea
)
from PIL import Image
import pillow_heif

pillow_heif.register_heif_opener()


class ImagePreviewDialog(QDialog):
    def __init__(self, image_paths: list[str], current_index: int = 0, parent=None):
        super().__init__(parent)
        self.image_paths = [p for p in image_paths if Path(p).exists()]
        self.current_index = current_index

        self.setWindowTitle("Invoice Preview")
        self.resize(800, 650)
        self.setStyleSheet("""
            QDialog { background-color: #151515; }
            QLabel { color: #EAEAEA; font-family: 'Segoe UI'; font-size: 13px; }
            QPushButton {
                background-color: #222;
                color: #FF9800;
                border: 1px solid #FF9800;
                border-radius: 8px;
                padding: 8px 16px;
                font-weight: bold;
                min-width: 90px;
            }
            QPushButton:hover { background-color: #FF9800; color: #111; }
            QPushButton:disabled { color: #555; border-color: #444; }
        """)

        layout = QVBoxLayout(self)

        # Scroll Area for high-res images
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.img_label = QLabel()
        self.img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setWidget(self.img_label)
        layout.addWidget(self.scroll_area)

        # Bottom Bar
        nav_layout = QHBoxLayout()
        self.btn_prev = QPushButton("◀ Previous")
        self.lbl_info = QLabel("")
        self.lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.btn_next = QPushButton("Next ▶")

        self.btn_prev.clicked.connect(self.prev_image)
        self.btn_next.clicked.connect(self.next_image)

        nav_layout.addWidget(self.btn_prev)
        nav_layout.addWidget(self.lbl_info)
        nav_layout.addWidget(self.btn_next)
        layout.addLayout(nav_layout)

        self.show_image()

    def show_image(self):
        if not self.image_paths:
            self.img_label.setText("No images to display.")
            return

        file_path = Path(self.image_paths[self.current_index])
        self.lbl_info.setText(f"Page {self.current_index + 1} of {len(self.image_paths)} — {file_path.name}")

        # Load image via Pillow (supports HEIC, PNG, JPG, WEBP, etc.)
        try:
            with Image.open(file_path) as img:
                img_rgb = img.convert("RGBA")
                data = img_rgb.tobytes("raw", "RGBA")
                qimg = QImage(data, img_rgb.width, img_rgb.height, QImage.Format.Format_RGBA8888)
                pixmap = QPixmap.fromImage(qimg)
        except Exception:
            pixmap = QPixmap(str(file_path))

        scaled = pixmap.scaled(720, 520, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.img_label.setPixmap(scaled)

        self.btn_prev.setEnabled(self.current_index > 0)
        self.btn_next.setEnabled(self.current_index < len(self.image_paths) - 1)

    def prev_image(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_image()

    def next_image(self):
        if self.current_index < len(self.image_paths) - 1:
            self.current_index += 1
            self.show_image()