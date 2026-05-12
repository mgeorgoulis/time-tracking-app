import os
import tempfile
import unittest
from datetime import datetime

from backend.models.audit_log import AuditLogEntry
from backend.models.time_entry import TimeEntry
from backend.models.user import Admin, Employee
from backend.services.sqlite_store import SQLiteStore


class TestSQLiteStoreUsers(unittest.TestCase):

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.store = SQLiteStore(self.temp_file.name)

    def tearDown(self):
        self.store.close()
        os.remove(self.temp_file.name)

    def test_add_and_get_user_by_id(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")

        self.store.add_user(employee)
        result = self.store.get_user_by_id(1)

        self.assertEqual(result.user_id, 1)
        self.assertEqual(result.name, "Max Mitarbeiter")
        self.assertEqual(result.department, "Verkauf")
        self.assertEqual(result.role, "employee")

    def test_add_duplicate_user_raises_error(self):
        employee_one = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        employee_two = Employee(1, "Lena Mitarbeiterin", "2345", "Lager")

        self.store.add_user(employee_one)

        with self.assertRaises(ValueError):
            self.store.add_user(employee_two)

    def test_get_all_users_returns_all_users(self):
        self.store.add_user(Employee(1, "Max Mitarbeiter", "1234", "Verkauf"))
        self.store.add_user(Admin(2, "Alex Admin", "9999"))

        result = self.store.get_all_users()

        self.assertEqual(len(result), 2)

    def test_get_users_by_role(self):
        self.store.add_user(Employee(1, "Max Mitarbeiter", "1234", "Verkauf"))
        self.store.add_user(Admin(2, "Alex Admin", "9999"))

        admins = self.store.get_users_by_role("admin")

        self.assertEqual(len(admins), 1)
        self.assertEqual(admins[0].name, "Alex Admin")

    def test_get_users_by_department(self):
        self.store.add_user(Employee(1, "Max Mitarbeiter", "1234", "Verkauf"))
        self.store.add_user(Employee(2, "Lena Mitarbeiterin", "2345", "Verkauf"))
        self.store.add_user(Employee(3, "Tom Mitarbeiter", "3456", "Lager"))

        result = self.store.get_users_by_department("Verkauf")

        self.assertEqual(len(result), 2)


class TestSQLiteStoreTimeEntries(unittest.TestCase):

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.store = SQLiteStore(self.temp_file.name)

    def tearDown(self):
        self.store.close()
        os.remove(self.temp_file.name)

    def test_save_and_load_time_entry(self):
        entry = TimeEntry(employee_id=1)
        entry.clock_in_time = datetime(2026, 1, 1, 8, 0)
        entry.clock_out_time = datetime(2026, 1, 1, 16, 30)
        entry.break_minutes = 30

        self.store.save_time_entry(entry)

        result = self.store.get_time_entries_by_employee(1)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].employee_id, 1)
        self.assertEqual(result[0].worked_minutes(), 480)

    def test_get_time_entries_only_for_selected_employee(self):
        entry_one = TimeEntry(employee_id=1)
        entry_one.clock_in_time = datetime(2026, 1, 1, 8, 0)
        entry_one.clock_out_time = datetime(2026, 1, 1, 12, 0)

        entry_two = TimeEntry(employee_id=2)
        entry_two.clock_in_time = datetime(2026, 1, 1, 9, 0)
        entry_two.clock_out_time = datetime(2026, 1, 1, 13, 0)

        self.store.save_time_entry(entry_one)
        self.store.save_time_entry(entry_two)

        result = self.store.get_time_entries_by_employee(1)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].employee_id, 1)


class TestSQLiteStoreAuditLogs(unittest.TestCase):

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.store = SQLiteStore(self.temp_file.name)

    def tearDown(self):
        self.store.close()
        os.remove(self.temp_file.name)

    def test_save_and_load_audit_log_entry(self):
        entry = AuditLogEntry(
            actor_id=1,
            action="clock_in",
            target_type="TimeEntry",
            target_id=100,
            details={"source": "backend"}
        )

        self.store.save_audit_log_entry(entry)

        result = self.store.get_audit_log_entries()

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].actor_id, 1)
        self.assertEqual(result[0].action, "clock_in")
        self.assertEqual(result[0].details["source"], "backend")


if __name__ == "__main__":
    unittest.main()
