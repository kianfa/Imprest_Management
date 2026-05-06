import sqlite3
import bcrypt
import uuid
from pathlib import Path
from datetime import datetime


class Load_Save_Data:
    def __init__(self) -> None:
        pass
    DB_PATH = Path(__file__).parent / "app.db"


    @classmethod
    def get_connection(self) -> sqlite3.Connection:
        return sqlite3.connect(self.DB_PATH)


    @classmethod
    def fetch_all(self, query, params=None) -> list[tuple]:
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute(query,params)
        rows = cur.fetchall()
        conn.close()
        return rows


    @classmethod
    def get_invoices_by_Invoice_NO(self, Invoice_NO) -> list[tuple]:
        query="""
            SELECT Invoice_NO, explanation, record_date, amount, expense_center,expense_type,company_name
            FROM records
            WHERE Invoice_NO LIKE ?
        """
        return self.fetch_all(query,(Invoice_NO,))


    @classmethod
    def get_invoices_by_explanation(self, explanation) -> list[tuple]:
        query="""
            SELECT Invoice_NO, explanation, record_date, amount, expense_center,expense_type,company_name
            FROM records
            WHERE explanation LIKE ?
        """
        return self.fetch_all(query,(f"%{explanation}%",))


    @classmethod
    def get_invoices_by_regestrationdate(self, regestrationdate) -> list[tuple]:
        query="""
            SELECT Invoice_NO, explanation, record_date, amount, expense_center, expense_type, company_name
            FROM records
            WHERE record_date = ?
        """
        return self.fetch_all(query,(regestrationdate,))


    @classmethod
    def get_invoices_by_time_range(self, startdate,enddate) -> list[tuple]:
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
    def save_data(data: dict) -> None:
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


    def invoice_exists(self, invoice_number: str) -> bool:
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM records WHERE Invoice_NO = ?", (invoice_number,))
        exists = cur.fetchone() is not None
        conn.close()
        return exists



class DataBase:
    DB_PATH = Path(__file__).parent / "app.db"

    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        return sqlite3.connect(cls.DB_PATH)

    @classmethod
    def create_tables(cls) -> None:
        query = """ CREATE TABLE IF NOT EXISTS records
                    (
                        id \
                        TEXT \
                        PRIMARY \
                        KEY,
                        Invoice_NO \
                        TEXT \
                        NOT \
                        NULL,
                        explanation \
                        TEXT, \
                        amount \
                        REAL,
                        record_date \
                        TEXT,
                        image_path \
                        TEXT,
                        last_modified \
                        TEXT \
                        NOT \
                        NULL,
                        source_pc \
                        TEXT \
                        NOT \
                        NULL,
                        deleted \
                        INTEGER \
                        DEFAULT \
                        0,
                        expense_center \
                        TEXT,
                        expense_type \
                        TEXT,
                        company_name \
                        TEXT
                    ) """
        conn = cls.get_connection()
        cur = conn.cursor()
        cur.execute(query)

        # Create users table (if not exists)
        cur.execute('''CREATE TABLE IF NOT EXISTS users
        (
            id
            INTEGER
            PRIMARY
            KEY
            AUTOINCREMENT,
            username
            TEXT
            UNIQUE
            NOT
            NULL,
            hashed_password
            TEXT
            NOT
            NULL,
            role
            TEXT
            NOT
            NULL
            CHECK (
            role
            IN
                       (
            'admin',
            'user'
                       )),
            full_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

        conn.commit()
        conn.close()

    # ========== USER AUTHENTICATION METHODS ==========

    @classmethod
    def create_default_users(cls) -> None:
        conn = cls.get_connection()
        cur = conn.cursor()

        users = [
            ('1', 'q', 'admin', 'Nozhan Ghayati'),
            ('admin2', 'SecurePass456', 'admin', 'Bob Admin'),
            ('user1', 'user111', 'user', 'Charlie User'),
            ('user2', 'user222', 'user', 'Diana User'),
            ('user3', 'user333', 'user', 'Eve User'),
            ('user4', 'user444', 'user', 'Frank User'),
            ('user5', 'user555', 'user', 'Grace User'),
        ]

        for username, plain_pw, role, full_name in users:
            hashed = bcrypt.hashpw(plain_pw.encode(), bcrypt.gensalt())
            try:
                cur.execute('''
                            INSERT INTO users (username, hashed_password, role, full_name)
                            VALUES (?, ?, ?, ?)
                            ''', (username, hashed, role, full_name))
            except sqlite3.IntegrityError:
                continue

        conn.commit()
        conn.close()

    @classmethod
    def verify_login(cls, username: str, password: str) -> tuple[bool, str]:
        """
        Returns (success, role)
        success: True if password matches, else False
        role: 'admin' or 'user' (empty string if login fails)
        """
        conn = cls.get_connection()
        cur = conn.cursor()
        cur.execute('SELECT hashed_password, role FROM users WHERE username = ?', (username,))
        row = cur.fetchone()
        conn.close()

        if row and bcrypt.checkpw(password.encode(), row[0]):
            return True, row[1]
        return False, ""

    @classmethod
    def get_user_role(cls, username: str) -> str:
        """Return role ('admin' / 'user') or empty string if user not found."""
        conn = cls.get_connection()
        cur = conn.cursor()
        cur.execute('SELECT role FROM users WHERE username = ?', (username,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else ""


    @classmethod
    def insert_record(cls, Invoice_NO, explanation, amount, record_date,
                      image_path, source_pc, expense_center, expense_type, company_name) -> str:
        conn = cls.get_connection()
        cur = conn.cursor()
        record_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        cur.execute("""
                    INSERT INTO records (id, Invoice_NO, explanation, amount, record_date, image_path,
                                         last_modified, source_pc, expense_center, expense_type, company_name)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (record_id, Invoice_NO, explanation, amount, record_date, image_path,
                          now, source_pc, expense_center, expense_type, company_name))
        conn.commit()
        conn.close()
        return record_id



from pathlib import Path
import shutil

class ImageStore:
    BASE_DIR = Path(r"./")
    BASE_DIR.mkdir(parents=True, exist_ok=True)

    #Making new folder
    @classmethod
    def create_folder(cls, record_id: int) -> Path:
        folder = cls.BASE_DIR / str(record_id)
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    #Copying images in that folder
    @classmethod
    def copy_images_into_record_folder(cls, record_id: int, original_paths: list[str]) -> list[str]:
        folder = cls.create_folder(record_id)
        copied_paths: list[str] = []

        for i, src in enumerate(original_paths, start=1):
            src_path = Path(src)
            if not src_path.exists():
                continue

            dest = folder / f"{i:03d}{src_path.suffix.lower()}"
            shutil.copy2(src_path, dest)
            copied_paths.append(str(dest))

        return copied_paths