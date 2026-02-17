import sqlite3
from pathlib import Path
from datetime import datetime
import uuid


class Load_Save_Data:
    def __init__(self):
        pass

    DB_PATH = Path(__file__).parent / "app.db"

    @classmethod
    def get_connection(self):
        return sqlite3.connect(self.DB_PATH)

    @classmethod
    def fetch_all(self, query, params=None):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute(query,params)
        rows = cur.fetchall()
        conn.close()
        return rows

    @classmethod
    def get_invoices_by_title(self, title):
        query="""
            SELECT title, explanation, record_date, amount, expense_center,expense_type,company_name
            FROM records
            WHERE title LIKE ?
        """
        return self.fetch_all(query,(title,))

    @classmethod
    def get_invoices_by_explanation(self,explanation):
        query="""
            SELECT title, explanation, record_date, amount, expense_center,expense_type,company_name
            FROM records
            WHERE explanation LIKE ?
        """
        return self.fetch_all(query,(f"%{explanation}%",))

    @classmethod
    def get_invoices_by_regestrationdate(self, regestrationdate):
        query="""
            SELECT title, explanation, record_date, amount, expense_center, expense_type, company_name
            FROM records
            WHERE record_date = ?
        """
        return self.fetch_all(query,(regestrationdate,))

    @classmethod
    def get_invoices_by_logindate(self, startdate,enddate):
        query="""
        SELECT title, explanation, record_date, amount, expense_center,expense_type,company_name
        FROM records
        WHERE record_date >= ? AND record_date <= ?
        """
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute(query,(startdate,enddate))
        rows = cur.fetchall()
        conn.close()
        return rows

    @staticmethod
    def save_data(self,data: dict):
        DataBase.insert_record(
            title=data["title"],
            explanation=data["explanation"],
            amount=float(data["amount"]),
            record_date=data["record_date"],
            image_path=data["image_path"],
            source_pc=data["source_pc"],
            expense_center=data["expense_center"],
            expense_type=data["expense_type"],
            company_name=data["company_name"]
        )


class DataBase:
    DB_PATH = Path(__file__).parent / "app.db"

    def __init__(self):
        pass

    @classmethod
    def get_connection(self):
        return sqlite3.connect(self.DB_PATH)

    @classmethod
    def create_tables(self):
        query = """ CREATE TABLE IF NOT EXISTS records
                        (
                            id
                            TEXT
                            PRIMARY
                            KEY,
                            title
                            TEXT
                            NOT
                            NULL,
                            explanation
                            TEXT,
                            amount
                            REAL,
                            record_date
                            TEXT,
                            image_path
                            TEXT,
                            last_modified
                            TEXT
                            NOT
                            NULL,
                            source_pc
                            TEXT
                            NOT
                            NULL,
                            deleted
                            INTEGER
                            DEFAULT
                            0
                        ) """
        conn= self.get_connection()
        cur = conn.cursor()
        cur.execute(query)
        conn.commit()
        conn.close()

    def insert_record(self,title, explanation, amount, record_date, image_path, source_pc, expense_center, expense_type,company_name):
        conn = self.get_connection()
        cur = conn.cursor()
        record_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        cur.execute("""
        INSERT INTO records (
            id, title, explanation, amount,
            record_date, image_path,
            last_modified, source_pc, expense_center, expense_type, company_name
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ? , ? , ? )
        """, (
            record_id,
            title,
            explanation,
            amount,
            record_date,
            image_path,
            now,
            source_pc,
            expense_center,
            expense_type,
            company_name
        ))

        conn.commit()
        conn.close()


    def get_all_records(self):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM records WHERE deleted = 0")
        rows = cur.fetchall()
        conn.close()
        return rows
