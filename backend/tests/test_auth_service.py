import unittest

from backend.models.user import Employee
from backend.models.audit_log import AuditLog
from backend.services.auth_service import AuthService


class TestAuthService(unittest.TestCase):

    def test_login_with_correct_pin_returns_user(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        audit_log = AuditLog()
        service = AuthService([employee], audit_log)

        result = service.login_with_pin(1, "1234")

        self.assertEqual(result, employee)

    def test_login_with_correct_pin_writes_success_log(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        audit_log = AuditLog()
        service = AuthService([employee], audit_log)

        service.login_with_pin(1, "1234")

        self.assertEqual(len(audit_log.entries), 1)
        self.assertEqual(audit_log.entries[0].action, "login_success")

    def test_login_with_wrong_pin_raises_error(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        audit_log = AuditLog()
        service = AuthService([employee], audit_log)

        with self.assertRaises(ValueError):
            service.login_with_pin(1, "9999")

    def test_login_with_wrong_pin_writes_failed_log(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        audit_log = AuditLog()
        service = AuthService([employee], audit_log)

        try:
            service.login_with_pin(1, "9999")
        except ValueError:
            pass

        self.assertEqual(len(audit_log.entries), 1)
        self.assertEqual(audit_log.entries[0].action, "login_failed")
        self.assertEqual(audit_log.entries[0].details["reason"], "invalid_pin")

    def test_inactive_user_cannot_login(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        employee.is_active = False

        audit_log = AuditLog()
        service = AuthService([employee], audit_log)

        with self.assertRaises(ValueError):
            service.login_with_pin(1, "1234")

        self.assertEqual(audit_log.entries[0].action, "login_failed")
        self.assertEqual(audit_log.entries[0].details["reason"], "user_inactive")

    def test_login_with_unknown_user_raises_error(self):
        audit_log = AuditLog()
        service = AuthService([], audit_log)

        with self.assertRaises(ValueError):
            service.login_with_pin(99, "1234")

    def test_login_with_unknown_user_writes_failed_log(self):
        audit_log = AuditLog()
        service = AuthService([], audit_log)

        try:
            service.login_with_pin(99, "1234")
        except ValueError:
            pass

        self.assertEqual(len(audit_log.entries), 1)
        self.assertEqual(audit_log.entries[0].action, "login_failed")
        self.assertEqual(audit_log.entries[0].details["reason"], "user_not_found")


if __name__ == "__main__":
    unittest.main()
