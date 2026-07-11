import sqlite3
import bcrypt
import uuid
from pathlib import Path
from datetime import datetime
import sys
import shutil

# ==================== PATH ====================
if getattr(sys, 'frozen', False):
    EXE_DIR = Path(sys.executable).parent
    DB_PATH = EXE_DIR / "app.db"
    IMAGE_DIR = EXE_DIR / "image_records"
else:
    DB_PATH = Path(__file__).resolve().parent / "app.db"
    IMAGE_DIR = Path(r"./image_records").resolve()

IMAGE_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================================

class Load_Save_Data:
    def __init__(self) -> None:
        pass

    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        return sqlite3.connect(DB_PATH)

    @classmethod
    def fetch_all(cls, query, params=None) -> list[tuple]:
        conn = cls.get_connection()
        cur = conn.cursor()
        cur.execute(query, params if params else ())
        rows = cur.fetchall()
        conn.close()
        return rows

    @classmethod
    def get_record_by_id(cls, record_id) -> dict | None:
        conn = cls.get_connection()
        cur = conn.cursor()
        cur.execute("""
                    SELECT Invoice_NO,
                           Project_Code,
                           explanation,
                           amount,
                           record_date,
                           image_path,
                           expense_center,
                           expense_type,
                           company_name,
                           created_by
                    FROM records
                    WHERE id = ?
                      AND deleted = 0
                    """, (record_id,))
        row = cur.fetchone()
        conn.close()
        if row:
            return {
                "Invoice_NO": row[0],
                "Project_Code": row[1],
                "explanation": row[2],
                "amount": row[3],
                "record_date": row[4],
                "image_path": row[5],
                "expense_center": row[6],
                "expense_type": row[7],
                "company_name": row[8],
                "created_by": row[9]
            }
        return None

    @classmethod
    def get_invoices_by_Invoice_NO(cls, Invoice_NO) -> list[tuple]:
        query = """
                SELECT Id, \
                       Invoice_NO, \
                       Project_Code, \
                       explanation, \
                       record_date, \
                       amount, \
                       expense_center, \
                       expense_type, \
                       company_name, \
                       created_by
                FROM records
                WHERE Invoice_NO LIKE ?
                  AND deleted = 0 \
                """
        return cls.fetch_all(query, (Invoice_NO,))

    @classmethod
    def get_invoices_by_Project_Code(cls, Project_Code) -> list[tuple]:
        query = """
                SELECT Id, \
                       Invoice_NO, \
                       Project_Code, \
                       explanation, \
                       record_date, \
                       amount, \
                       expense_center, \
                       expense_type, \
                       company_name, \
                       created_by
                FROM records
                WHERE Project_Code LIKE ?
                  AND deleted = 0 \
                """
        return cls.fetch_all(query, (Project_Code,))

    @classmethod
    def get_invoices_by_explanation(cls, explanation) -> list[tuple]:
        query = """
                SELECT Id, \
                       Invoice_NO, \
                       Project_Code, \
                       explanation, \
                       record_date, \
                       amount, \
                       expense_center, \
                       expense_type, \
                       company_name, \
                       created_by
                FROM records
                WHERE explanation LIKE ?
                  AND deleted = 0 \
                """
        return cls.fetch_all(query, (f"%{explanation}%",))

    @classmethod
    def get_invoices_by_regestrationdate(cls, regestrationdate) -> list[tuple]:
        query = """
                SELECT Id, \
                       Invoice_NO, \
                       Project_Code, \
                       explanation, \
                       record_date, \
                       amount, \
                       expense_center, \
                       expense_type, \
                       company_name, \
                       created_by
                FROM records
                WHERE record_date = ?
                  AND deleted = 0 \
                """
        return cls.fetch_all(query, (regestrationdate,))

    @classmethod
    def get_invoices_by_time_range(cls, startdate, enddate) -> list[tuple]:
        query = """
                SELECT Id, \
                       Invoice_NO, \
                       Project_Code, \
                       explanation, \
                       record_date, \
                       amount, \
                       expense_center, \
                       expense_type, \
                       company_name, \
                       created_by
                FROM records
                WHERE record_date >= ? \
                  AND record_date <= ?
                  AND deleted = 0 \
                """
        conn = cls.get_connection()
        cur = conn.cursor()
        cur.execute(query, (startdate, enddate))
        rows = cur.fetchall()
        conn.close()
        return rows

    @staticmethod
    def save_data(data: dict, created_by: str) -> None:
        record_id: str = DataBase.insert_record(
            Invoice_NO=data["Invoice NO"],
            Project_Code=data["Project_Code"],
            explanation=data["explanation"],
            amount=int(data["amount"]),
            record_date=data["record_date"],
            image_path=data.get("image_paths", ""),
            source_pc=data["source_pc"],
            expense_center=data["expense_center"],
            expense_type=data["expense_type"],
            company_name=data["company_name"],
            created_by=created_by
        )
        img: list[str] = Load_Save_Data.get_image_paths_by_id(record_id)
        ImageStore.copy_images_into_record_folder(record_id, img)

    @classmethod
    def get_image_paths_by_id(cls, record_id: str) -> list[str]:
        conn = cls.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT image_path FROM records WHERE id = ?", (record_id,))
        row = cur.fetchone()
        conn.close()

        raw = "" if not row or row[0] is None else str(row[0]).strip()
        return [p.strip() for p in raw.split("|") if p.strip()]

    @classmethod
    def invoice_exists(cls, invoice_number: str) -> bool:
        conn = cls.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM records WHERE Invoice_NO = ? AND deleted = 0", (invoice_number,))
        exists = cur.fetchone() is not None
        conn.close()
        return exists

    @classmethod
    def project_exists(cls, project_code: str) -> bool:
        conn = cls.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM records WHERE Project_Code = ?", (project_code,))
        exists = cur.fetchone() is not None
        conn.close()
        return exists

    @classmethod
    def soft_delete_record(cls, record_id: str) -> None:
        # ۱. تغییر وضعیت در دیتابیس
        conn = cls.get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE records SET deleted = 1 WHERE id = ?", (record_id,))
        conn.commit()
        conn.close()

        ImageStore.delete_folder(record_id)

    @classmethod
    def update_record(cls, record_id: str, updated_data: dict) -> None:
        conn = cls.get_connection()
        cur = conn.cursor()
        now = datetime.utcnow().isoformat()
        cur.execute("""
                    UPDATE records
                    SET Invoice_NO     = ?,
                        Project_Code   = ?,
                        explanation    = ?,
                        amount         = ?,
                        record_date    = ?,
                        expense_center = ?,
                        expense_type   = ?,
                        company_name   = ?,
                        image_path     = ?,
                        last_modified  = ?
                    WHERE id = ?
                    """, (
                        updated_data["Invoice_NO"],
                        updated_data["Project_Code"],
                        updated_data["explanation"],
                        updated_data["amount"],
                        updated_data["record_date"],
                        updated_data["expense_center"],
                        updated_data["expense_type"],
                        updated_data["company_name"],
                        updated_data["image_path"],
                        now,
                        record_id
                    ))
        conn.commit()
        conn.close()

        img: list[str] = cls.get_image_paths_by_id(record_id)
        ImageStore.copy_images_into_record_folder(record_id, img)


class UserSession:
    username = ""
    full_name = ""
    role = ""


class DataBase:
    @classmethod
    def get_connection(cls) -> sqlite3.Connection:
        return sqlite3.connect(DB_PATH)

    @classmethod
    def create_tables(cls) -> None:
        query = """
                CREATE TABLE IF NOT EXISTS records (
                    id TEXT PRIMARY KEY,
                    Invoice_NO TEXT NOT NULL,
                    Project_Code NOT NULL,
                    explanation TEXT, 
                    amount REAL,
                    record_date TEXT,
                    image_path TEXT,
                    last_modified TEXT NOT NULL,
                    source_pc TEXT NOT NULL, 
                    deleted INTEGER DEFAULT 0,
                    expense_center TEXT,
                    expense_type TEXT,
                    company_name TEXT,
                    created_by TEXT)
                """
        conn = cls.get_connection()
        cur = conn.cursor()
        cur.execute(query)
        try:
            cur.execute("ALTER TABLE records ADD COLUMN deleted INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass  # column already exists
        conn.commit()

        cur.execute(
            '''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                hashed_password TEXT NOT NULL,
                role TEXT NOT NULL CHECK (role IN('admin','user')),
                full_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
            ''')
        conn.commit()
        conn.close()

    @classmethod
    def create_default_users(cls) -> None:
        conn = cls.get_connection()
        cur = conn.cursor()

        users = [
            ('1', 'q', 'admin', 'Nozhan Ghayati'),
            ('farooghi', '1234asd1234', 'admin', 'Kian Farooghi'),
            ('chalabi', '12345678', 'admin', 'Chalabi'),
            ('rahimi', '12345678', 'user', 'Rahimi'),
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
        conn = cls.get_connection()
        cur = conn.cursor()
        cur.execute('SELECT hashed_password, role FROM users WHERE username = ?', (username,))
        row = cur.fetchone()
        conn.close()

        UserSession.username = username
        UserSession.full_name = cls.get_user_full_name(username)
        UserSession.role = cls.get_user_role(username)

        if row and bcrypt.checkpw(password.encode(), row[0]):
            return True, row[1]
        return False, ""

    @classmethod
    def get_user_role(cls, username: str) -> str:
        conn = cls.get_connection()
        cur = conn.cursor()
        cur.execute('SELECT role FROM users WHERE username = ?', (username,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row else ""

    @classmethod
    def get_user_full_name(cls, username: str) -> str:
        conn = cls.get_connection()
        cur = conn.cursor()
        cur.execute("SELECT full_name FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        conn.close()
        return row[0] if row and row[0] else username

    @classmethod
    def insert_record(cls, Invoice_NO, Project_Code, explanation, amount, record_date,
                      image_path, source_pc, expense_center, expense_type,
                      company_name, created_by) -> str:
        conn = cls.get_connection()
        cur = conn.cursor()
        record_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        cur.execute("""
                    INSERT INTO records (id, Invoice_NO, Project_Code, explanation, amount, record_date, image_path,
                                         last_modified, source_pc, expense_center, expense_type, company_name,
                                         created_by)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (record_id, Invoice_NO, Project_Code, explanation, amount, record_date, image_path,
                          now, source_pc, expense_center, expense_type, company_name, created_by))
        conn.commit()
        conn.close()
        return record_id


class ImageStore:
    BASE_DIR = IMAGE_DIR

    @classmethod
    def create_folder(cls, record_id: str) -> Path:
        folder = cls.BASE_DIR / str(record_id)
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    @classmethod
    def delete_folder(cls, record_id: str) -> None:
        folder = cls.BASE_DIR / str(record_id)
        if folder.exists() and folder.is_dir():
            shutil.rmtree(folder)

    @classmethod
    def copy_images_into_record_folder(cls, record_id: str, original_paths: list[str]) -> list[str]:
        if original_paths:
            cls.delete_folder(record_id)

        if not original_paths:
            return []

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