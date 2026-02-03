from app.data.data_base import insert_record
import sqlite3


def save_data(data: dict):
    insert_record(
        title=data["title"],
        description=data["description"],
        amount=float(data["amount"]),
        record_date=data["record_date"],
        image_path=data["image_path"],
        source_pc=data["source_pc"],
        expense_center=data["expense_center"],
        expense_type=data["expense_type"],
        company_name=data["company_name"]
    )



class load_data():
    DB_PATH = "app/data/app.db"

    @staticmethod
    def get_connection():
        return sqlite3.connect(load_data.DB_PATH)

    @staticmethod
    def fetch_all(query, params=()):
        conn = load_data.get_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def get_invoices_by_invoice_no(text):
        query = """
            SELECT invoice_no, explanation, record_date, amount, image_path
            FROM records
            WHERE invoice_no LIKE ?
        """
        return load_data.fetch_all(query, (f"%{text}%",))

    def get_invoices_by_registration_date(text):
        query = """
            SELECT invoice_no, explanation, record_date, amount, image_path
            FROM records
            WHERE registration_date LIKE ?
        """
        return load_data.fetch_all(query, (f"%{text}%",))

    def get_invoices_by_login_date(text):
        query = """
            SELECT invoice_no, explanation,  record_date, amount, image_path
            FROM records
            WHERE login_date LIKE ?
        """
        return load_data.fetch_all(query, (f"%{text}%",))

    def get_invoices_by_explanation(text):
        query = """
            SELECT invoice_no, explanation, record_date, amount, image_path
            FROM records
            WHERE explanation LIKE ?
        """
        return load_data.fetch_all(query, (f"%{text}%",))
