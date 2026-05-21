import json
import sqlite3
from datetime import datetime

from backend.models.audit_log import AuditLogEntry
from backend.models.time_entry import TimeEntry
from backend.models.user import Admin, Apprentice, DepartmentManager, Employee, Executive


class SQLiteStore:
    def __init__(self, database_path):
        self.database_path = database_path
        self.connection = sqlite3.connect(database_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self):
        cursor = self.connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                pin_hash TEXT NOT NULL,
                role TEXT NOT NULL,
                department TEXT,
                email TEXT,
                phone TEXT,
                street TEXT,
                postal_code TEXT,
                city TEXT,
                country TEXT,
                must_change_pin INTEGER NOT NULL DEFAULT 0,
                is_active INTEGER NOT NULL DEFAULT 1
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS time_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id INTEGER NOT NULL,
                clock_in_time TEXT,
                clock_out_time TEXT,
                break_minutes INTEGER NOT NULL DEFAULT 0,
                break_started_at TEXT
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                actor_id INTEGER,
                action TEXT NOT NULL,
                target_type TEXT NOT NULL,
                target_id INTEGER,
                details TEXT,
                created_at TEXT NOT NULL
            )
        """)

        self._ensure_time_entry_columns()
        self._ensure_user_columns()

        self.connection.commit()

    def _ensure_time_entry_columns(self):
        cursor = self.connection.execute("PRAGMA table_info(time_entries)")
        columns = {row["name"] for row in cursor.fetchall()}

        if "break_started_at" not in columns:
            self.connection.execute(
                "ALTER TABLE time_entries ADD COLUMN break_started_at TEXT"
            )

    def _ensure_user_columns(self):
        cursor = self.connection.execute("PRAGMA table_info(users)")
        columns = {row["name"] for row in cursor.fetchall()}

        if "must_change_pin" not in columns:
            self.connection.execute(
                "ALTER TABLE users ADD COLUMN must_change_pin INTEGER NOT NULL DEFAULT 0"
            )

        if "is_active" not in columns:
            self.connection.execute(
                "ALTER TABLE users ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1"
            )

        additional_columns = {
            "first_name": "TEXT",
            "last_name": "TEXT",
            "email": "TEXT",
            "phone": "TEXT",
            "street": "TEXT",
            "postal_code": "TEXT",
            "city": "TEXT",
            "country": "TEXT"
        }

        for column_name, column_type in additional_columns.items():
            if column_name not in columns:
                self.connection.execute(
                    f"ALTER TABLE users ADD COLUMN {column_name} {column_type}"
                )


    def add_user(self, user):
        try:
            self.connection.execute(
                """
                INSERT INTO users (
                    user_id,
                    name,
                    first_name,
                    last_name,
                    pin_hash,
                    role,
                    department,
                    email,
                    phone,
                    street,
                    postal_code,
                    city,
                    country,
                    must_change_pin,
                    is_active
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user.user_id,
                    user.name,
                    user.first_name,
                    user.last_name,
                    user.get_pin_hash(),
                    user.role,
                    getattr(user, "department", None),
                    user.email,
                    user.phone,
                    user.street,
                    user.postal_code,
                    user.city,
                    user.country,
                    1 if user.must_change_pin else 0,
                    1 if user.is_active else 0
                )
            )
            self.connection.commit()
            return user
        except sqlite3.IntegrityError:
            raise ValueError("Benutzer-ID existiert bereits.")

    def update_user_pin(self, user):
        cursor = self.connection.execute(
            """
            UPDATE users
            SET
                pin_hash = ?,
                must_change_pin = ?
            WHERE user_id = ?
            """,
            (
                user.get_pin_hash(),
                1 if user.must_change_pin else 0,
                user.user_id
            )
        )

        self.connection.commit()

        if cursor.rowcount == 0:
            raise ValueError("Benutzer wurde nicht gefunden.")

        return user

    def update_user_status(self, user):
        cursor = self.connection.execute(
            """
            UPDATE users
            SET is_active = ?
            WHERE user_id = ?
            """,
            (
                1 if user.is_active else 0,
                user.user_id
            )
        )

        self.connection.commit()

        if cursor.rowcount == 0:
            raise ValueError("Benutzer wurde nicht gefunden.")

        return user

    def get_user_by_id(self, user_id):
        cursor = self.connection.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return self._build_user_from_row(row)

    def get_all_users(self):
        cursor = self.connection.execute(
            "SELECT * FROM users ORDER BY user_id"
        )

        return [
            self._build_user_from_row(row)
            for row in cursor.fetchall()
        ]

    def get_users_by_role(self, role):
        cursor = self.connection.execute(
            "SELECT * FROM users WHERE role = ? ORDER BY user_id",
            (role,)
        )

        return [
            self._build_user_from_row(row)
            for row in cursor.fetchall()
        ]

    def get_users_by_department(self, department):
        cursor = self.connection.execute(
            "SELECT * FROM users WHERE department = ? ORDER BY user_id",
            (department,)
        )

        return [
            self._build_user_from_row(row)
            for row in cursor.fetchall()
        ]

    def save_time_entry(self, time_entry):
        if time_entry.entry_id is not None:
            self.update_time_entry(time_entry)
            return time_entry.entry_id

        cursor = self.connection.execute(
            """
            INSERT INTO time_entries (
    		employee_id,
    		clock_in_time,
    		clock_out_time,
    		break_minutes,
    		break_started_at
	    )
	    VALUES (?, ?, ?, ?, ?)
            """,
            (
                time_entry.employee_id,
                self._datetime_to_text(time_entry.clock_in_time),
                self._datetime_to_text(time_entry.clock_out_time),
                time_entry.break_minutes,
		self._datetime_to_text(time_entry.break_started_at)
            )
        )

        self.connection.commit()
        time_entry.entry_id = cursor.lastrowid
        return time_entry.entry_id

    def update_time_entry(self, time_entry):
        if time_entry.entry_id is None:
            return self.save_time_entry(time_entry)

        cursor = self.connection.execute(
            """
            UPDATE time_entries
            SET
                employee_id = ?,
                clock_in_time = ?,
                clock_out_time = ?,
                break_minutes = ?,
		break_started_at = ?
            WHERE id = ?
            """,
            (
                time_entry.employee_id,
                self._datetime_to_text(time_entry.clock_in_time),
                self._datetime_to_text(time_entry.clock_out_time),
                time_entry.break_minutes,
		self._datetime_to_text(time_entry.break_started_at),
                time_entry.entry_id
            )
        )

        self.connection.commit()

        if cursor.rowcount == 0:
            raise ValueError("Zeiteintrag wurde nicht gefunden.")

        return time_entry

    def get_time_entries_by_employee(self, employee_id):
        cursor = self.connection.execute(
            """
            SELECT *
            FROM time_entries
            WHERE employee_id = ?
            ORDER BY clock_in_time
            """,
            (employee_id,)
        )

        return [
            self._build_time_entry_from_row(row)
            for row in cursor.fetchall()
        ]

    def get_active_time_entry_by_employee(self, employee_id):
        cursor = self.connection.execute(
            """
            SELECT *
            FROM time_entries
            WHERE employee_id = ?
            AND clock_out_time IS NULL
            ORDER BY clock_in_time DESC
            LIMIT 1
            """,
            (employee_id,)
        )

        row = cursor.fetchone()

        if row is None:
            return None

        return self._build_time_entry_from_row(row)

    def get_active_time_entries(self):
        cursor = self.connection.execute(
            """
            SELECT *
            FROM time_entries
            WHERE clock_out_time IS NULL
            ORDER BY clock_in_time
            """
        )

        return [
            self._build_time_entry_from_row(row)
            for row in cursor.fetchall()
        ]

    def get_daily_break_minutes(self, employee_id, year, month, day):
        target_date = datetime(year, month, day).date()
        entries = self.get_time_entries_by_employee(employee_id)

        return sum(
            entry.break_minutes
            for entry in entries
            if entry.clock_in_time is not None
            and entry.clock_in_time.date() == target_date
        )

    def save_audit_log_entry(self, audit_log_entry):
        self.connection.execute(
            """
            INSERT INTO audit_logs (
                actor_id,
                action,
                target_type,
                target_id,
                details,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                audit_log_entry.actor_id,
                audit_log_entry.action,
                audit_log_entry.target_type,
                audit_log_entry.target_id,
                json.dumps(audit_log_entry.details),
                audit_log_entry.created_at.isoformat()
            )
        )

        self.connection.commit()

    def get_audit_log_entries(self):
        cursor = self.connection.execute(
            """
            SELECT *
            FROM audit_logs
            ORDER BY created_at
            """
        )

        entries = []

        for row in cursor.fetchall():
            entry = AuditLogEntry(
                actor_id=row["actor_id"],
                action=row["action"],
                target_type=row["target_type"],
                target_id=row["target_id"],
                details=json.loads(row["details"] or "{}")
            )
            entry.created_at = datetime.fromisoformat(row["created_at"])
            entries.append(entry)

        return entries

    def close(self):
        self.connection.close()

    def _build_user_from_row(self, row):
        role = row["role"]
        must_change_pin = bool(row["must_change_pin"])
        is_active = bool(row["is_active"])

        profile_fields = {
            "first_name": row["first_name"],
            "last_name": row["last_name"],
            "email": row["email"],
            "phone": row["phone"],
            "street": row["street"],
            "postal_code": row["postal_code"],
            "city": row["city"],
            "country": row["country"],
            "must_change_pin": must_change_pin,
            "is_active": is_active
        }

        if role == "employee":
            return Employee(
                row["user_id"],
                row["name"],
                department=row["department"],
                pin_hash=row["pin_hash"],
                **profile_fields
            )

        if role == "apprentice":
            return Apprentice(
                row["user_id"],
                row["name"],
                department=row["department"],
                pin_hash=row["pin_hash"],
                **profile_fields
            )

        if role == "department_manager":
            return DepartmentManager(
                row["user_id"],
                row["name"],
                department=row["department"],
                pin_hash=row["pin_hash"],
                **profile_fields
            )

        if role == "executive":
            return Executive(
                row["user_id"],
                row["name"],
                pin_hash=row["pin_hash"],
                **profile_fields
            )

        if role == "admin":
            return Admin(
                row["user_id"],
                row["name"],
                pin_hash=row["pin_hash"],
                **profile_fields
            )

        raise ValueError(f"Unbekannte Rolle: {role}")

    def _build_time_entry_from_row(self, row):
        entry = TimeEntry(
            employee_id=row["employee_id"],
            entry_id=row["id"]
        )
        entry.clock_in_time = self._text_to_datetime(row["clock_in_time"])
        entry.clock_out_time = self._text_to_datetime(row["clock_out_time"])
        entry.break_minutes = row["break_minutes"]
        entry.break_started_at = self._text_to_datetime(row["break_started_at"])

        return entry

    def _datetime_to_text(self, value):
        if value is None:
            return None

        return value.isoformat()

    def _text_to_datetime(self, value):
        if value is None:
            return None

        return datetime.fromisoformat(value)
