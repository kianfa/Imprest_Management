import hashlib
import subprocess
from datetime import datetime
import winreg
from PyQt6.QtWidgets import QMessageBox, QDialog, QApplication
import sys
from app.controller.navigator import Navigator


class LicenseManager(QDialog):
    def check_or_initialize(self) -> bool :
        try:
            path = winreg.OpenKey(winreg.HKEY_CURRENT_USER, "SOFTWARE\\Imprest_Management")
            date = winreg.QueryValueEx(path ,'a3f9b2c1d4e5')
            installation_date = datetime.strptime(date[0], '%Y-%m-%d')
            if (datetime.now()-installation_date).days > 365:
                msg = QMessageBox()
                msg.setWindowTitle("License Error")
                msg.setText(f"License expired. Please contact developers.\n CPU ID: {self.get_fingerprint()}")
                about_us_btn = msg.addButton("About us", QMessageBox.ButtonRole.ActionRole)
                copy_fingerprint_btn = msg.addButton("Copy Fingerprint", QMessageBox.ButtonRole.ActionRole)
                msg.exec()
                if msg.clickedButton() == copy_fingerprint_btn:
                    finger_print = self.get_fingerprint()
                    QApplication.clipboard().setText(finger_print)
                    QMessageBox.information(None,"Fingerprint Copied","Copied!")
                elif msg.clickedButton() == about_us_btn:
                    self.open_about_page()
                sys.exit()
            else:
                return True
        except FileNotFoundError:
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, 'Software\\Imprest_Management')
            winreg.SetValueEx(key, 'a3f9b2c1d4e5', 0, winreg.REG_SZ, datetime.today().strftime('%Y-%m-%d'))
            return True

    def open_about_page(self):
        try:
            Navigator().main_window_navigator_about_us(self)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"CRASH: {e}")

    def get_fingerprint(self)-> str:
        fingerprint = subprocess.run(["C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe", "-Command", "Get-WmiObject Win32_Processor | Select-Object ProcessorId"],capture_output=True)
        lines = fingerprint.stdout.decode("utf-8", errors='ignore').strip().split('\n')
        cpu_id = [line.strip() for line in lines if line.strip()][-1]
        fingerprint_hash  = hashlib.sha256(cpu_id.encode()).hexdigest()
        return fingerprint_hash