import unittest

from backend.models.user import Employee
from backend.models.audit_log import AuditLog
from backend.services.time_tracking_service import TimeTrackingService


class TestTimeTrackingService(unittest.TestCase):

    def test_clock_in_creates_active_entry(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        audit_log = AuditLog()
        service = TimeTrackingService(audit_log)

        entry = service.clock_in(employee)

        self.assertIsNotNone(entry.clock_in_time)
        self.assertEqual(service.get_active_entry(1), entry)

    def test_clock_in_writes_audit_log_entry(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        audit_log = AuditLog()
        service = TimeTrackingService(audit_log)

        service.clock_in(employee)

        self.assertEqual(len(audit_log.entries), 1)
        self.assertEqual(audit_log.entries[0].action, "clock_in")

    def test_double_clock_in_raises_error(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        audit_log = AuditLog()
        service = TimeTrackingService(audit_log)

        service.clock_in(employee)

        with self.assertRaises(ValueError):
            service.clock_in(employee)

    def test_clock_out_completes_entry(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        audit_log = AuditLog()
        service = TimeTrackingService(audit_log)

        service.clock_in(employee)
        entry = service.clock_out(employee)

        self.assertIsNotNone(entry.clock_out_time)
        self.assertIsNone(service.get_active_entry(1))
        self.assertEqual(len(service.get_completed_entries(1)), 1)

    def test_clock_out_without_clock_in_raises_error(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        audit_log = AuditLog()
        service = TimeTrackingService(audit_log)

        with self.assertRaises(ValueError):
            service.clock_out(employee)

    def test_clock_out_writes_audit_log_entry(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        audit_log = AuditLog()
        service = TimeTrackingService(audit_log)

        service.clock_in(employee)
        service.clock_out(employee)

        self.assertEqual(len(audit_log.entries), 2)
        self.assertEqual(audit_log.entries[1].action, "clock_out")

    def test_add_break_to_active_entry(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        audit_log = AuditLog()
        service = TimeTrackingService(audit_log)

        service.clock_in(employee)
        entry = service.add_break(employee, 30)

        self.assertEqual(entry.break_minutes, 30)

    def test_add_break_without_clock_in_raises_error(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        audit_log = AuditLog()
        service = TimeTrackingService(audit_log)

        with self.assertRaises(ValueError):
            service.add_break(employee, 30)


if __name__ == "__main__":
    unittest.main()
