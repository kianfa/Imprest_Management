import sqlite3
import bcrypt
import uuid
import os
import secrets
import logging
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime
import sys
import shutil
import jdatetime

logger = logging.getLogger(__name__)

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
# Shared connection helper
# ============================================================================

@contextmanager
def db_connection():
    """
    Single place that owns connection lifecycle.
    Guarantees close() even if an exception is raised mid-query,
    and commits only if no exception occurred.
    """
    conn = sqlite3.connect(DB_PATH)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


class UserSession:
    username = ""
    full_name = ""
    role = ""
    must_change_password = False

    @classmethod
    def clear(cls) -> None:
        cls.username = ""
        cls.full_name = ""
        cls.role = ""
        cls.must_change_password = False


# ============================================================================

class Load_Save_Data:

    @classmethod
    def fetch_all(cls, query, params=None) -> list[tuple]:
        with db_connection() as conn:
            cur = conn.cursor()
            cur.execute(query, params if params else ())
            return cur.fetchall()

    @classmethod
    def get_record_by_id(cls, record_id) -> dict | None:
        with db_connection() as conn:
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

        if not row:
            return None
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

    @classmethod
    def get_invoices_by_Invoice_NO(cls, Invoice_NO) -> list[tuple]:
        query = """
                SELECT Id, Invoice_NO, Project_Code, explanation, record_date, amount,
                       expense_center, expense_type, company_name, created_by
                FROM records
                WHERE Invoice_NO LIKE ?
                  AND deleted = 0
                """
        return cls.fetch_all(query, (Invoice_NO,))

    @classmethod
    def get_invoices_by_Project_Code(cls, Project_Code) -> list[tuple]:
        query = """
                SELECT Id, Invoice_NO, Project_Code, explanation, record_date, amount,
                       expense_center, expense_type, company_name, created_by
                FROM records
                WHERE Project_Code LIKE ?
                  AND deleted = 0
                """
        return cls.fetch_all(query, (Project_Code,))

    @classmethod
    def get_invoices_by_explanation(cls, explanation) -> list[tuple]:
        query = """
                SELECT Id, Invoice_NO, Project_Code, explanation, record_date, amount,
                       expense_center, expense_type, company_name, created_by
                FROM records
                WHERE explanation LIKE ?
                  AND deleted = 0
                """
        return cls.fetch_all(query, (f"%{explanation}%",))

    @classmethod
    def get_invoices_by_regestrationdate(cls, regestrationdate) -> list[tuple]:
        query = """
                SELECT Id, Invoice_NO, Project_Code, explanation, record_date, amount,
                       expense_center, expense_type, company_name, created_by
                FROM records
                WHERE last_modified = ?
                  AND deleted = 0
                """
        return cls.fetch_all(query, (regestrationdate,))

    @classmethod
    def get_invoices_by_time_range(cls, startdate, enddate) -> list[tuple]:
        query = """
                SELECT Id, Invoice_NO, Project_Code, explanation, record_date, amount,
                       expense_center, expense_type, company_name, created_by
                FROM records
                WHERE record_date >= ?
                  AND record_date <= ?
                  AND deleted = 0
                """
        return cls.fetch_all(query, (startdate, enddate))

    @staticmethod
    def save_data(data: dict, created_by: str) -> None:
        record_id: str = DataBase.insert_record(
            Invoice_NO=int(data["Invoice NO"]),
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
        with db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT image_path FROM records WHERE id = ?", (record_id,))
            row = cur.fetchone()
        raw = "" if not row or row[0] is None else str(row[0]).strip()
        return [p.strip() for p in raw.split("|") if p.strip()]

    @classmethod
    def invoice_exists(cls, invoice_number: str) -> bool:
        with db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM records WHERE Invoice_NO = ? AND deleted = 0", (invoice_number,))
            return cur.fetchone() is not None

    @classmethod
    def project_exists(cls, project_code: str) -> bool:
        with db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT 1 FROM records WHERE Project_Code = ?", (project_code,))
            return cur.fetchone() is not None

    @classmethod
    def soft_delete_record(cls, record_id: str) -> None:
        with db_connection() as conn:
            cur = conn.cursor()
            cur.execute("UPDATE records SET deleted = 1 WHERE id = ?", (record_id,))
        ImageStore.delete_folder(record_id)

    @classmethod
    def update_record(cls, record_id: str, updated_data: dict) -> None:
        now = datetime.utcnow().isoformat()
        with db_connection() as conn:
            cur = conn.cursor()
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

        img: list[str] = cls.get_image_paths_by_id(record_id)
        ImageStore.copy_images_into_record_folder(record_id, img)


# ============================================================================

class DataBase:

    @classmethod
    def create_tables(cls) -> None:
        with db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                        CREATE TABLE IF NOT EXISTS records (
                            id TEXT PRIMARY KEY,
                            Invoice_NO INTEGER NOT NULL,
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
                        """)
            try:
                cur.execute("ALTER TABLE records ADD COLUMN deleted INTEGER DEFAULT 0")
            except sqlite3.OperationalError:
                pass

            cur.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            hashed_password TEXT NOT NULL,
                            role TEXT NOT NULL CHECK (role IN ('admin','user')),
                            full_name TEXT,
                            must_change_password INTEGER NOT NULL DEFAULT 1,
                            failed_attempts INTEGER NOT NULL DEFAULT 0,
                            locked_until TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
                        """)
            try:
                cur.execute("ALTER TABLE users ADD COLUMN must_change_password INTEGER NOT NULL DEFAULT 1")
            except sqlite3.OperationalError:
                pass
            try:
                cur.execute("ALTER TABLE users ADD COLUMN failed_attempts INTEGER NOT NULL DEFAULT 0")
            except sqlite3.OperationalError:
                pass
            try:
                cur.execute("ALTER TABLE users ADD COLUMN locked_until TEXT")
            except sqlite3.OperationalError:
                pass

    # ------------------------------------------------------------------
    # Default user provisioning — NO plaintext passwords in source.
    # ------------------------------------------------------------------
    @classmethod
    def create_default_users(cls) -> None:
        """
        Creates the initial admin account only, on first run, with either:
          - a password supplied via the DEFAULT_ADMIN_PASSWORD env var, or
          - a securely generated random password, printed ONCE to the console/log.
        The account is flagged must_change_password so it can't be used long-term as-is.
        Regular users should be created afterwards through the app itself by an admin,
        not hardcoded here — that was the actual privacy/security hole.
        """
        with db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM users")
            if cur.fetchone()[0] > 0:
                return  # already provisioned, do nothing

            admin_username = os.environ.get("DEFAULT_ADMIN_USERNAME", "admin")
            admin_password = os.environ.get("DEFAULT_ADMIN_PASSWORD")
            generated = admin_password is None
            if generated:
                admin_password = secrets.token_urlsafe(12)

            hashed = bcrypt.hashpw(admin_password.encode(), bcrypt.gensalt())
            cur.execute("""
                        INSERT INTO users (username, hashed_password, role, full_name, must_change_password)
                        VALUES (?, ?, 'admin', ?, 1)
                        """, (admin_username, hashed, "Administrator"))

        if generated:
            # Printed once, at provisioning time only — never stored in source or in the DB in plaintext.
            logger.warning(
                "First-run admin account created. Username: %s | Temporary password: %s "
                "— store this now, it will not be shown again. You must change it on first login.",
                admin_username, admin_password
            )
            print(f"[SETUP] Admin username: {admin_username}")
            print(f"[SETUP] Temporary password: {admin_password}")
            print("[SETUP] Save this now — it will not be shown again. Change it after logging in.")

    @classmethod
    def create_user(cls, username: str, password: str, role: str, full_name: str,
                     force_password_change: bool = True) -> None:
        """Use this from an admin-only UI action to add real users — no plaintext creds in code."""
        if role not in ("admin", "user"):
            raise ValueError("role must be 'admin' or 'user'")
        hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        with db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                        INSERT INTO users (username, hashed_password, role, full_name, must_change_password)
                        VALUES (?, ?, ?, ?, ?)
                        """, (username, hashed, role, full_name, int(force_password_change)))

    @classmethod
    def change_password(cls, username: str, new_password: str) -> None:
        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
        with db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                        UPDATE users
                        SET hashed_password = ?, must_change_password = 0
                        WHERE username = ?
                        """, (hashed, username))

    # ------------------------------------------------------------------
    # Auth
    # ------------------------------------------------------------------
    @classmethod
    def verify_login(cls, username: str, password: str) -> tuple[bool, str]:
        with db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                        SELECT hashed_password, role, full_name, must_change_password,
                               failed_attempts, locked_until
                        FROM users WHERE username = ?
                        """, (username,))
            row = cur.fetchone()

            if not row:
                return False, ""

            hashed_password, role, full_name, must_change, failed_attempts, locked_until = row

            if locked_until and datetime.utcnow().isoformat() < locked_until:
                return False, ""

            if bcrypt.checkpw(password.encode(), hashed_password):
                cur.execute(
                    "UPDATE users SET failed_attempts = 0, locked_until = NULL WHERE username = ?",
                    (username,)
                )
                UserSession.username = username
                UserSession.full_name = full_name or username
                UserSession.role = role
                UserSession.must_change_password = bool(must_change)
                return True, role

            # wrong password: bump failed_attempts, lock briefly after 5 tries
            failed_attempts += 1
            locked_until_val = None
            if failed_attempts >= 5:
                from datetime import timedelta
                locked_until_val = (datetime.utcnow() + timedelta(minutes=5)).isoformat()
                failed_attempts = 0
            cur.execute(
                "UPDATE users SET failed_attempts = ?, locked_until = ? WHERE username = ?",
                (failed_attempts, locked_until_val, username)
            )

        UserSession.clear()
        return False, ""

    @classmethod
    def get_user_role(cls, username: str) -> str:
        with db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT role FROM users WHERE username = ?", (username,))
            row = cur.fetchone()
        return row[0] if row else ""

    @classmethod
    def get_user_full_name(cls, username: str) -> str:
        with db_connection() as conn:
            cur = conn.cursor()
            cur.execute("SELECT full_name FROM users WHERE username = ?", (username,))
            row = cur.fetchone()
        return row[0] if row and row[0] else username

    # ------------------------------------------------------------------
    @classmethod
    def insert_record(cls, Invoice_NO, Project_Code, explanation, amount, record_date,
                       image_path, source_pc, expense_center, expense_type,
                       company_name, created_by) -> str:
        record_id = str(uuid.uuid4())
        now = jdatetime.datetime.now().strftime('%Y/%m/%d')
        with db_connection() as conn:
            cur = conn.cursor()
            cur.execute("""
                        INSERT INTO records (id, Invoice_NO, Project_Code, explanation, amount, record_date,
                                             image_path, last_modified, source_pc, expense_center, expense_type,
                                             company_name, created_by)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (record_id, Invoice_NO, Project_Code, explanation, amount, record_date, image_path,
                              now, source_pc, expense_center, expense_type, company_name, created_by))
        return record_id


# ============================================================================
from PIL import Image
import pillow_heif
pillow_heif.register_heif_opener()

class ImageStore:
    BASE_DIR = IMAGE_DIR
    BASE_DIR.mkdir(parents=True, exist_ok=True)

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
        folder = cls.create_folder(record_id)
        copied_paths: list[str] = []

        for i, src in enumerate(original_paths, start=1):
            src_path = Path(src)
            if not src_path.exists():
                continue

            suffix = src_path.suffix.lower()

            # If it is an iPhone HEIC/HEIF photo, convert it to standard JPEG (.jpg)
            if suffix in [".heic", ".heif"]:
                dest = folder / f"{i:03d}.jpg"
                try:
                    with Image.open(src_path) as img:
                        # Convert color profile to RGB and save as JPG
                        img.convert("RGB").save(dest, format="JPEG", quality=95)
                    copied_paths.append(str(dest))
                except Exception as e:
                    print(f"Error converting HEIC image {src_path}: {e}")
            else:
                # Standard formats (.png, .jpg, .webp, .bmp) are copied as normal
                dest = folder / f"{i:03d}{suffix}"
                shutil.copy2(src_path, dest)
                copied_paths.append(str(dest))

        return copied_paths