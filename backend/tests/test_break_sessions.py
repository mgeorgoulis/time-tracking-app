import unittest
from datetime import datetime

from backend.models.time_entry import TimeEntry


class TestTimeEntryBreakSessions(unittest.TestCase):

    def test_start_break_sets_break_started_at(self):
        entry = TimeEntry(employee_id=1)
        entry.clock_in_time = datetime(2026, 1, 1, 8, 0)

        entry.start_break(datetime(2026, 1, 1, 10, 0))

        self.assertIsNotNone(entry.break_started_at)
        self.assertTrue(entry.is_on_break())

    def test_end_break_adds_break_minutes(self):
        entry = TimeEntry(employee_id=1)
        entry.clock_in_time = datetime(2026, 1, 1, 8, 0)

        entry.start_break(datetime(2026, 1, 1, 10, 0))
        duration = entry.end_break(datetime(2026, 1, 1, 10, 17))

        self.assertEqual(duration, 17)
        self.assertEqual(entry.break_minutes, 17)
        self.assertIsNone(entry.break_started_at)
        self.assertFalse(entry.is_on_break())

    def test_multiple_breaks_are_added(self):
        entry = TimeEntry(employee_id=1)
        entry.clock_in_time = datetime(2026, 1, 1, 8, 0)

        entry.start_break(datetime(2026, 1, 1, 10, 0))
        entry.end_break(datetime(2026, 1, 1, 10, 15))

        entry.start_break(datetime(2026, 1, 1, 12, 0))
        entry.end_break(datetime(2026, 1, 1, 12, 30))

        self.assertEqual(entry.break_minutes, 45)

    def test_start_break_without_clock_in_raises_error(self):
        entry = TimeEntry(employee_id=1)

        with self.assertRaises(ValueError):
            entry.start_break(datetime(2026, 1, 1, 10, 0))

    def test_start_break_twice_raises_error(self):
        entry = TimeEntry(employee_id=1)
        entry.clock_in_time = datetime(2026, 1, 1, 8, 0)

        entry.start_break(datetime(2026, 1, 1, 10, 0))

        with self.assertRaises(ValueError):
            entry.start_break(datetime(2026, 1, 1, 10, 5))

    def test_end_break_without_active_break_raises_error(self):
        entry = TimeEntry(employee_id=1)
        entry.clock_in_time = datetime(2026, 1, 1, 8, 0)

        with self.assertRaises(ValueError):
            entry.end_break(datetime(2026, 1, 1, 10, 15))

    def test_clock_out_while_break_is_active_raises_error(self):
        entry = TimeEntry(employee_id=1)
        entry.clock_in_time = datetime(2026, 1, 1, 8, 0)

        entry.start_break(datetime(2026, 1, 1, 10, 0))

        with self.assertRaises(ValueError):
            entry.clock_out(datetime(2026, 1, 1, 16, 0))

    def test_worked_minutes_uses_added_breaks(self):
        entry = TimeEntry(employee_id=1)
        entry.clock_in_time = datetime(2026, 1, 1, 8, 0)

        entry.start_break(datetime(2026, 1, 1, 10, 0))
        entry.end_break(datetime(2026, 1, 1, 10, 15))

        entry.start_break(datetime(2026, 1, 1, 12, 0))
        entry.end_break(datetime(2026, 1, 1, 12, 30))

        entry.clock_out(datetime(2026, 1, 1, 16, 30))

        self.assertEqual(entry.break_minutes, 45)
        self.assertEqual(entry.worked_minutes(), 465)

import os
import tempfile

from backend.models.audit_log import AuditLog
from backend.models.user import Employee
from backend.services.sqlite_store import SQLiteStore
from backend.services.time_tracking_service import TimeTrackingService


class TestTimeTrackingServiceBreakSessions(unittest.TestCase):

    def setUp(self):
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.close()
        self.store = SQLiteStore(self.temp_file.name)
        self.audit_log = AuditLog()
        self.employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        self.service = TimeTrackingService(self.audit_log, self.store)

    def tearDown(self):
        self.store.close()
        os.remove(self.temp_file.name)

    def test_start_and_end_break_via_service(self):
        self.service.clock_in(
            self.employee,
            timestamp=datetime(2026, 1, 1, 8, 0)
        )

        self.service.start_break(
            self.employee,
            timestamp=datetime(2026, 1, 1, 10, 0)
        )

        entry = self.service.end_break(
            self.employee,
            timestamp=datetime(2026, 1, 1, 10, 17)
        )

        self.assertEqual(entry.break_minutes, 17)
        self.assertFalse(entry.is_on_break())

    def test_multiple_breaks_via_service_are_added(self):
        self.service.clock_in(
            self.employee,
            timestamp=datetime(2026, 1, 1, 8, 0)
        )

        self.service.start_break(
            self.employee,
            timestamp=datetime(2026, 1, 1, 10, 0)
        )
        self.service.end_break(
            self.employee,
            timestamp=datetime(2026, 1, 1, 10, 15)
        )

        self.service.start_break(
            self.employee,
            timestamp=datetime(2026, 1, 1, 12, 0)
        )
        entry = self.service.end_break(
            self.employee,
            timestamp=datetime(2026, 1, 1, 12, 30)
        )

        self.assertEqual(entry.break_minutes, 45)

    def test_break_actions_are_written_to_audit_log(self):
        self.service.clock_in(
            self.employee,
            timestamp=datetime(2026, 1, 1, 8, 0)
        )

        self.service.start_break(
            self.employee,
            timestamp=datetime(2026, 1, 1, 10, 0)
        )
        self.service.end_break(
            self.employee,
            timestamp=datetime(2026, 1, 1, 10, 20)
        )

        actions = [entry.action for entry in self.audit_log.entries]

        self.assertIn("break_start", actions)
        self.assertIn("break_end", actions)

    def test_break_is_persisted_in_sqlite(self):
        self.service.clock_in(
            self.employee,
            timestamp=datetime(2026, 1, 1, 8, 0)
        )

        self.service.start_break(
            self.employee,
            timestamp=datetime(2026, 1, 1, 10, 0)
        )

        restored_entry = self.store.get_active_time_entry_by_employee(1)

        self.assertIsNotNone(restored_entry)
        self.assertTrue(restored_entry.is_on_break())

        self.service.end_break(
            self.employee,
            timestamp=datetime(2026, 1, 1, 10, 25)
        )

        restored_entry = self.store.get_active_time_entry_by_employee(1)

        self.assertEqual(restored_entry.break_minutes, 25)
        self.assertFalse(restored_entry.is_on_break())

if __name__ == "__main__":
    unittest.main()
