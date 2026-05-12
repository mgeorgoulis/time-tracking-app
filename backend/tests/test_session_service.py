import unittest

from backend.models.audit_log import AuditLog
from backend.models.user import Employee
from backend.services.session_service import SessionService


class TestSessionService(unittest.TestCase):

    def test_create_session_returns_session_with_token(self):
        audit_log = AuditLog()
        service = SessionService(audit_log)
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")

        session = service.create_session(employee)

        self.assertIsNotNone(session.token)
        self.assertEqual(session.user, employee)
        self.assertTrue(session.active)

    def test_create_session_writes_audit_log(self):
        audit_log = AuditLog()
        service = SessionService(audit_log)
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")

        service.create_session(employee)

        self.assertEqual(len(audit_log.entries), 1)
        self.assertEqual(audit_log.entries[0].action, "session_created")

    def test_get_user_by_valid_token_returns_user(self):
        audit_log = AuditLog()
        service = SessionService(audit_log)
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")

        session = service.create_session(employee)
        user = service.get_user_by_token(session.token)

        self.assertEqual(user, employee)

    def test_invalid_token_returns_none(self):
        audit_log = AuditLog()
        service = SessionService(audit_log)

        user = service.get_user_by_token("invalid-token")

        self.assertIsNone(user)

    def test_logout_deactivates_session(self):
        audit_log = AuditLog()
        service = SessionService(audit_log)
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")

        session = service.create_session(employee)

        service.logout(session.token)

        self.assertFalse(session.active)

    def test_logged_out_session_is_invalid(self):
        audit_log = AuditLog()
        service = SessionService(audit_log)
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")

        session = service.create_session(employee)
        service.logout(session.token)

        user = service.get_user_by_token(session.token)

        self.assertIsNone(user)

    def test_logout_unknown_token_raises_error(self):
        audit_log = AuditLog()
        service = SessionService(audit_log)

        with self.assertRaises(ValueError):
            service.logout("unknown-token")


if __name__ == "__main__":
    unittest.main()
