import unittest

from backend.models.audit_log import AuditLog, AuditLogEntry


class TestAuditLog(unittest.TestCase):

    def test_audit_log_entry_stores_data(self):
        entry = AuditLogEntry(
            actor_id=1,
            action="clock_in",
            target_type="TimeEntry",
            target_id=10,
            details={"source": "web"}
        )

        self.assertEqual(entry.actor_id, 1)
        self.assertEqual(entry.action, "clock_in")
        self.assertEqual(entry.target_type, "TimeEntry")
        self.assertEqual(entry.target_id, 10)
        self.assertEqual(entry.details["source"], "web")
        self.assertIsNotNone(entry.created_at)

    def test_entry_can_be_converted_to_dict(self):
        entry = AuditLogEntry(
            actor_id=1,
            action="confirm_timesheet",
            target_type="Timesheet",
            target_id=20
        )

        data = entry.to_dict()

        self.assertEqual(data["actor_id"], 1)
        self.assertEqual(data["action"], "confirm_timesheet")
        self.assertEqual(data["target_type"], "Timesheet")
        self.assertEqual(data["target_id"], 20)
        self.assertIn("created_at", data)

    def test_add_entry_adds_audit_log_entry(self):
        audit_log = AuditLog()
        entry = AuditLogEntry(
            actor_id=1,
            action="clock_out",
            target_type="TimeEntry"
        )

        audit_log.add_entry(entry)

        self.assertEqual(len(audit_log.entries), 1)

    def test_add_invalid_entry_raises_error(self):
        audit_log = AuditLog()

        with self.assertRaises(TypeError):
            audit_log.add_entry("not an audit log entry")

    def test_record_creates_and_adds_entry(self):
        audit_log = AuditLog()

        entry = audit_log.record(
            actor_id=1,
            action="clock_in",
            target_type="TimeEntry",
            target_id=100
        )

        self.assertEqual(len(audit_log.entries), 1)
        self.assertEqual(entry.action, "clock_in")

    def test_find_by_actor(self):
        audit_log = AuditLog()

        audit_log.record(1, "clock_in", "TimeEntry")
        audit_log.record(2, "clock_in", "TimeEntry")
        audit_log.record(1, "clock_out", "TimeEntry")

        entries = audit_log.find_by_actor(1)

        self.assertEqual(len(entries), 2)

    def test_find_by_action(self):
        audit_log = AuditLog()

        audit_log.record(1, "clock_in", "TimeEntry")
        audit_log.record(1, "clock_out", "TimeEntry")
        audit_log.record(2, "clock_in", "TimeEntry")

        entries = audit_log.find_by_action("clock_in")

        self.assertEqual(len(entries), 2)


if __name__ == "__main__":
    unittest.main()
