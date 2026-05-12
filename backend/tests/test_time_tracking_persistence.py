import os
import tempfile
import unittest
from datetime import datetime

from backend.models.audit_log import AuditLog
from backend.models.user import Employee
from backend.services.sqlite_store import SQLiteStore
from backend.services.time_tracking_service import TimeTrackingService


class TestTimeTrackingPersistence(unittest.TestCase):

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.store = SQLiteStore(self.temp_file.name)
        self.audit_log = AuditLog()
        self.employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")

    def tearDown(self):
        self.store.close()
        os.remove(self.temp_file.name)

    def test_clock_in_is_saved_as_active_entry(self):
        service = TimeTrackingService(self.audit_log, self.store)

        service.clock_in(
            self.employee,
            timestamp=datetime(2026, 1, 1, 8, 0)
        )

        active_entry = self.store.get_active_time_entry_by_employee(1)

        self.assertIsNotNone(active_entry)
        self.assertEqual(active_entry.employee_id, 1)

    def test_active_entry_is_restored_after_service_restart(self):
        first_service = TimeTrackingService(self.audit_log, self.store)

        first_service.clock_in(
            self.employee,
            timestamp=datetime(2026, 1, 1, 8, 0)
        )

        second_service = TimeTrackingService(self.audit_log, self.store)

        restored_entry = second_service.get_active_entry(1)

        self.assertIsNotNone(restored_entry)
        self.assertEqual(restored_entry.employee_id, 1)

    def test_clock_out_updates_persistent_entry(self):
        service = TimeTrackingService(self.audit_log, self.store)

        service.clock_in(
            self.employee,
            timestamp=datetime(2026, 1, 1, 8, 0)
        )

        service.add_break(self.employee, 30)

        service.clock_out(
            self.employee,
            timestamp=datetime(2026, 1, 1, 16, 30)
        )

        active_entry = self.store.get_active_time_entry_by_employee(1)
        entries = self.store.get_time_entries_by_employee(1)

        self.assertIsNone(active_entry)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].worked_minutes(), 480)


if __name__ == "__main__":
    unittest.main()
