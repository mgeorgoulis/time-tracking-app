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

class TestSQLiteStoreActiveTimeEntries(unittest.TestCase):

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.store = SQLiteStore(self.temp_file.name)

    def tearDown(self):
        self.store.close()
        os.remove(self.temp_file.name)

    def test_save_time_entry_sets_entry_id(self):
        entry = TimeEntry(employee_id=1)
        entry.clock_in_time = datetime(2026, 1, 1, 8, 0)

        entry_id = self.store.save_time_entry(entry)

        self.assertIsNotNone(entry_id)
        self.assertEqual(entry.entry_id, entry_id)

    def test_get_active_time_entry_by_employee(self):
        entry = TimeEntry(employee_id=1)
        entry.clock_in_time = datetime(2026, 1, 1, 8, 0)

        self.store.save_time_entry(entry)

        active_entry = self.store.get_active_time_entry_by_employee(1)

        self.assertIsNotNone(active_entry)
        self.assertEqual(active_entry.employee_id, 1)
        self.assertIsNone(active_entry.clock_out_time)

    def test_completed_entry_is_not_active(self):
        entry = TimeEntry(employee_id=1)
        entry.clock_in_time = datetime(2026, 1, 1, 8, 0)
        entry.clock_out_time = datetime(2026, 1, 1, 16, 0)

        self.store.save_time_entry(entry)

        active_entry = self.store.get_active_time_entry_by_employee(1)

        self.assertIsNone(active_entry)

    def test_update_time_entry_persists_clock_out(self):
        entry = TimeEntry(employee_id=1)
        entry.clock_in_time = datetime(2026, 1, 1, 8, 0)

        self.store.save_time_entry(entry)

        entry.clock_out_time = datetime(2026, 1, 1, 16, 30)
        entry.break_minutes = 30

        self.store.update_time_entry(entry)

        loaded_entries = self.store.get_time_entries_by_employee(1)

        self.assertEqual(len(loaded_entries), 1)
        self.assertEqual(loaded_entries[0].worked_minutes(), 480)

    def test_get_active_time_entries_returns_only_open_entries(self):
        active_entry = TimeEntry(employee_id=1)
        active_entry.clock_in_time = datetime(2026, 1, 1, 8, 0)

        completed_entry = TimeEntry(employee_id=2)
        completed_entry.clock_in_time = datetime(2026, 1, 1, 8, 0)
        completed_entry.clock_out_time = datetime(2026, 1, 1, 16, 0)

        self.store.save_time_entry(active_entry)
        self.store.save_time_entry(completed_entry)

        active_entries = self.store.get_active_time_entries()

        self.assertEqual(len(active_entries), 1)
        self.assertEqual(active_entries[0].employee_id, 1)


if __name__ == "__main__":
    unittest.main()
