import os
import tempfile
import unittest
from datetime import datetime

from backend.models.audit_log import AuditLogEntry
from backend.models.time_entry import TimeEntry
from backend.models.user import Admin, Apprentice, Employee
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

    def test_add_and_get_apprentice(self):
        apprentice = Apprentice(
            4,
            "Tim Auszubildender",
            "1234",
            "Verkauf",
            must_change_pin=True
        )

        self.store.add_user(apprentice)
        loaded_user = self.store.get_user_by_id(4)

        self.assertEqual(loaded_user.role, "apprentice")
        self.assertEqual(loaded_user.department, "Verkauf")
        self.assertTrue(loaded_user.must_change_pin)
        self.assertTrue(loaded_user.check_pin("1234"))

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

    def test_update_user_profile_persists_profile_fields(self):
        employee = Employee(
            user_id=1,
            first_name="Max",
            last_name="Mustermann",
            pin_code="1234",
            department="Verkauf",
            email="max@example.com",
            phone="0123",
            street="Alte Straße 1",
            postal_code="12345",
            city="Altstadt",
            country="Deutschland"
        )

        self.store.add_user(employee)

        employee.first_name = "Maria"
        employee.last_name = "Musterfrau"
        employee.name = employee.full_name
        employee.email = "maria@example.com"
        employee.phone = "0987"
        employee.street = "Neue Straße 2"
        employee.postal_code = "54321"
        employee.city = "Neustadt"
        employee.country = "Deutschland"

        self.store.update_user_profile(employee)

        loaded_employee = self.store.get_user_by_id(1)

        self.assertEqual(loaded_employee.first_name, "Maria")
        self.assertEqual(loaded_employee.last_name, "Musterfrau")
        self.assertEqual(loaded_employee.full_name, "Maria Musterfrau")
        self.assertEqual(loaded_employee.email, "maria@example.com")
        self.assertEqual(loaded_employee.phone, "0987")
        self.assertEqual(loaded_employee.street, "Neue Straße 2")
        self.assertEqual(loaded_employee.postal_code, "54321")
        self.assertEqual(loaded_employee.city, "Neustadt")

    def test_add_and_load_user_with_must_change_pin(self):
        employee = Employee(
            1,
            "Max Mitarbeiter",
            "1234",
            "Verkauf",
            must_change_pin=True
        )

        self.store.add_user(employee)
        loaded_employee = self.store.get_user_by_id(1)

        self.assertTrue(loaded_employee.must_change_pin)

    def test_update_user_pin_persists_new_pin(self):
        employee = Employee(
            1,
            "Max Mitarbeiter",
            "1234",
            "Verkauf",
            must_change_pin=True
        )

        self.store.add_user(employee)

        employee.change_pin("1234", "5678")
        self.store.update_user_pin(employee)

        loaded_employee = self.store.get_user_by_id(1)

        self.assertTrue(loaded_employee.check_pin("5678"))
        self.assertFalse(loaded_employee.must_change_pin)

    def test_add_and_load_inactive_user(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        employee.is_active = False

        self.store.add_user(employee)
        loaded_employee = self.store.get_user_by_id(1)

        self.assertFalse(loaded_employee.is_active)

    def test_update_user_status_persists_status(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")

        self.store.add_user(employee)

        employee.is_active = False
        self.store.update_user_status(employee)

        loaded_employee = self.store.get_user_by_id(1)

        self.assertFalse(loaded_employee.is_active)

    def test_add_and_load_user_profile_fields(self):
        employee = Employee(
            user_id=1,
            first_name="Max",
            last_name="Mustermann",
            pin_code="1234",
            department="Verkauf",
            email="max.mustermann@example.com",
            phone="0123456789",
            street="Musterstraße 1",
            postal_code="12345",
            city="Musterstadt",
            country="Deutschland"
        )

        self.store.add_user(employee)
        loaded_employee = self.store.get_user_by_id(1)

        self.assertEqual(loaded_employee.first_name, "Max")
        self.assertEqual(loaded_employee.last_name, "Mustermann")
        self.assertEqual(loaded_employee.full_name, "Max Mustermann")
        self.assertEqual(loaded_employee.email, "max.mustermann@example.com")
        self.assertEqual(loaded_employee.phone, "0123456789")
        self.assertEqual(loaded_employee.street, "Musterstraße 1")
        self.assertEqual(loaded_employee.postal_code, "12345")
        self.assertEqual(loaded_employee.city, "Musterstadt")
        self.assertEqual(loaded_employee.country, "Deutschland")


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

class TestSQLiteStoreBreakSessions(unittest.TestCase):

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.store = SQLiteStore(self.temp_file.name)

    def tearDown(self):
        self.store.close()
        os.remove(self.temp_file.name)

    def test_save_and_load_active_break(self):
        entry = TimeEntry(employee_id=1)
        entry.clock_in_time = datetime(2026, 1, 1, 8, 0)
        entry.break_started_at = datetime(2026, 1, 1, 10, 0)

        self.store.save_time_entry(entry)

        active_entry = self.store.get_active_time_entry_by_employee(1)

        self.assertIsNotNone(active_entry)
        self.assertTrue(active_entry.is_on_break())
        self.assertEqual(
            active_entry.break_started_at,
            datetime(2026, 1, 1, 10, 0)
        )

    def test_update_time_entry_persists_break_minutes(self):
        entry = TimeEntry(employee_id=1)
        entry.clock_in_time = datetime(2026, 1, 1, 8, 0)

        self.store.save_time_entry(entry)

        entry.start_break(datetime(2026, 1, 1, 10, 0))
        entry.end_break(datetime(2026, 1, 1, 10, 20))

        self.store.update_time_entry(entry)

        loaded_entries = self.store.get_time_entries_by_employee(1)

        self.assertEqual(len(loaded_entries), 1)
        self.assertEqual(loaded_entries[0].break_minutes, 20)

    def test_get_daily_break_minutes_sums_breaks_for_day(self):
        entry_one = TimeEntry(employee_id=1)
        entry_one.clock_in_time = datetime(2026, 1, 1, 8, 0)
        entry_one.break_minutes = 20

        entry_two = TimeEntry(employee_id=1)
        entry_two.clock_in_time = datetime(2026, 1, 1, 13, 0)
        entry_two.break_minutes = 15

        entry_other_day = TimeEntry(employee_id=1)
        entry_other_day.clock_in_time = datetime(2026, 1, 2, 8, 0)
        entry_other_day.break_minutes = 30

        self.store.save_time_entry(entry_one)
        self.store.save_time_entry(entry_two)
        self.store.save_time_entry(entry_other_day)

        result = self.store.get_daily_break_minutes(1, 2026, 1, 1)

        self.assertEqual(result, 35)

if __name__ == "__main__":
    unittest.main()
