import sqlite3
from pathlib import Path
from datetime import datetime
import uuid
from typing import Optional


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
    def get_invoices_by_Invoice_NO(self, Invoice_NO):
        query="""
            SELECT Invoice_NO, explanation, record_date, amount, expense_center,expense_type,company_name
            FROM records
            WHERE Invoice_NO LIKE ?
        """
        return self.fetch_all(query,(Invoice_NO,))


    @classmethod
    def get_invoices_by_explanation(self,explanation):
        query="""
            SELECT Invoice_NO, explanation, record_date, amount, expense_center,expense_type,company_name
            FROM records
            WHERE explanation LIKE ?
        """
        return self.fetch_all(query,(f"%{explanation}%",))


    @classmethod
    def get_invoices_by_regestrationdate(self, regestrationdate):
        query="""
            SELECT Invoice_NO, explanation, record_date, amount, expense_center, expense_type, company_name
            FROM records
            WHERE record_date = ?
        """
        return self.fetch_all(query,(regestrationdate,))


    @classmethod
    def get_invoices_by_time_range(self, startdate,enddate):
        query="""
        SELECT Invoice_NO, explanation, record_date, amount, expense_center,expense_type,company_name
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
    def save_data(data: dict):
        id: int = DataBase().insert_record(
            Invoice_NO=data["Invoice NO"],
            explanation=data["explanation"],
            amount=float(data["amount"]),
            record_date=data["record_date"],
            image_path=data.get("image_paths", ""),
            source_pc=data["source_pc"],
            expense_center=data["expense_center"],
            expense_type=data["expense_type"],
            company_name=data["company_name"]
        )
        img:list[str] = Load_Save_Data().get_image_paths_by_id(id)
        ImageStore.copy_images_into_record_folder(id, img)


    def get_image_paths_by_id(self, record_id: int) -> list[str]:
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT image_path FROM records WHERE id = ?", (record_id,))
        row = cur.fetchone()
        conn.close()

        raw = "" if not row or row[0] is None else str(row[0]).strip()
        return [p.strip() for p in raw.split("|") if p.strip()]



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
                            Invoice_NO
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



    def insert_record(self,Invoice_NO, explanation, amount, record_date, image_path, source_pc, expense_center, expense_type,company_name) -> int:
        conn = self.get_connection()
        cur = conn.cursor()
        record_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        cur.execute("""
        INSERT INTO records (
            id, Invoice_NO, explanation, amount,
            record_date, image_path,
            last_modified, source_pc, expense_center, expense_type, company_name
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ? , ? , ? )
        """, (
            record_id,
            Invoice_NO,
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
        return record_id


    def get_all_records(self):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM records WHERE deleted = 0")
        rows = cur.fetchall()
        conn.close()
        return rows

    def id_from_invoice_no(self, invoice_no:int)->Optional[str]:
        conn = self.get_connection()
        cur = conn.cursor()

        cur.execute("SELECT id FROM records WHERE Invoice_NO = ?", (invoice_no,))
        row = cur.fetchone()

        conn.close()
        return row[0] if row else None



from pathlib import Path
import shutil

class ImageStore:
    BASE_DIR = Path(r"D:\Work\Imprest_Management\Imprest_Management_Forked\image_records")
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    #Making new folder
    @classmethod
    def ensure_record_folder(cls, record_id: int) -> Path:
        folder = cls.BASE_DIR / str(record_id)
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    #Copying images in that folder
    @classmethod
    def copy_images_into_record_folder(cls, record_id: int, original_paths: list[str]) -> list[str]:
        folder = cls.ensure_record_folder(record_id)
        copied_paths: list[str] = []

        for i, src in enumerate(original_paths, start=1):
            src_path = Path(src)
            if not src_path.exists():
                continue

            dest = folder / f"{i:03d}{src_path.suffix.lower()}"
            shutil.copy2(src_path, dest)
            copied_paths.append(str(dest))

        return copied_paths