import unittest
from datetime import datetime

from backend.models.audit_log import AuditLog
from backend.services.archive_service import ArchiveService, ArchivedReport


class TestArchivedReport(unittest.TestCase):

    def test_archived_report_sets_archived_until(self):
        created_at = datetime(2026, 5, 1)
        report = ArchivedReport(
            report_id=1,
            employee_id=10,
            year=2026,
            month=5,
            content={},
            created_at=created_at
        )

        self.assertEqual(report.archived_until, datetime(2036, 12, 31))

    def test_report_cannot_be_deleted_before_archive_date(self):
        created_at = datetime(2026, 5, 1)
        report = ArchivedReport(
            report_id=1,
            employee_id=10,
            year=2026,
            month=5,
            content={},
            created_at=created_at
        )

        result = report.can_be_deleted(datetime(2030, 1, 1))

        self.assertFalse(result)

    def test_report_can_be_deleted_after_archive_date(self):
        created_at = datetime(2026, 5, 1)
        report = ArchivedReport(
            report_id=1,
            employee_id=10,
            year=2026,
            month=5,
            content={},
            created_at=created_at
        )

        result = report.can_be_deleted(datetime(2037, 1, 1))

        self.assertTrue(result)

    def test_mark_deleted_sets_deleted_at(self):
        created_at = datetime(2026, 5, 1)
        report = ArchivedReport(
            report_id=1,
            employee_id=10,
            year=2026,
            month=5,
            content={},
            created_at=created_at
        )

        report.mark_deleted(datetime(2037, 1, 1))

        self.assertIsNotNone(report.deleted_at)


class TestArchiveService(unittest.TestCase):

    def test_archive_report_adds_report_to_archive(self):
        audit_log = AuditLog()
        service = ArchiveService(audit_log)

        report_data = {
            "employee_id": 1,
            "employee_name": "Max Mitarbeiter",
            "month": 1,
            "year": 2026,
            "worked_minutes": 480
        }

        archived_report = service.archive_report(
            report=report_data,
            report_id=100,
            actor_id=1
        )

        self.assertEqual(len(service.archived_reports), 1)
        self.assertEqual(archived_report.report_id, 100)

    def test_archive_report_writes_audit_log(self):
        audit_log = AuditLog()
        service = ArchiveService(audit_log)

        report_data = {
            "employee_id": 1,
            "employee_name": "Max Mitarbeiter",
            "month": 1,
            "year": 2026,
            "worked_minutes": 480
        }

        service.archive_report(
            report=report_data,
            report_id=100,
            actor_id=1
        )

        self.assertEqual(len(audit_log.entries), 1)
        self.assertEqual(audit_log.entries[0].action, "archive_report")

    def test_find_by_employee_returns_only_matching_reports(self):
        audit_log = AuditLog()
        service = ArchiveService(audit_log)

        report_one = {
            "employee_id": 1,
            "month": 1,
            "year": 2026
        }

        report_two = {
            "employee_id": 2,
            "month": 1,
            "year": 2026
        }

        service.archive_report(report_one, report_id=100, actor_id=1)
        service.archive_report(report_two, report_id=200, actor_id=2)

        result = service.find_by_employee(1)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].employee_id, 1)

    def test_find_deletable_reports(self):
        audit_log = AuditLog()
        service = ArchiveService(audit_log)

        report = ArchivedReport(
            report_id=100,
            employee_id=1,
            year=2026,
            month=1,
            content={},
            created_at=datetime(2026, 1, 1)
        )

        service.archived_reports.append(report)

        result = service.find_deletable_reports(datetime(2037, 1, 1))

        self.assertEqual(len(result), 1)

    def test_delete_report_marks_report_as_deleted(self):
        audit_log = AuditLog()
        service = ArchiveService(audit_log)

        report = ArchivedReport(
            report_id=100,
            employee_id=1,
            year=2026,
            month=1,
            content={},
            created_at=datetime(2026, 1, 1)
        )

        service.archived_reports.append(report)

        deleted_report = service.delete_report(
            report_id=100,
            actor_id=99,
            current_date=datetime(2037, 1, 1)
        )

        self.assertTrue(deleted_report.is_deleted())

    def test_delete_report_before_archive_date_raises_error(self):
        audit_log = AuditLog()
        service = ArchiveService(audit_log)

        report = ArchivedReport(
            report_id=100,
            employee_id=1,
            year=2026,
            month=1,
            content={},
            created_at=datetime(2026, 1, 1)
        )

        service.archived_reports.append(report)

        with self.assertRaises(ValueError):
            service.delete_report(
                report_id=100,
                actor_id=99,
                current_date=datetime(2030, 1, 1)
            )

    def test_delete_unknown_report_raises_error(self):
        audit_log = AuditLog()
        service = ArchiveService(audit_log)

        with self.assertRaises(ValueError):
            service.delete_report(
                report_id=999,
                actor_id=99,
                current_date=datetime(2037, 1, 1)
            )


if __name__ == "__main__":
    unittest.main()
