from datetime import datetime


class ArchivedReport:
    def __init__(self, report_id, employee_id, year, month, content, created_at=None):
        self.report_id = report_id
        self.employee_id = employee_id
        self.year = year
        self.month = month
        self.content = content
        self.created_at = created_at or datetime.now()
        self.archived_until = datetime(self.created_at.year + 10, 12, 31)
        self.deleted_at = None

    def is_deleted(self):
        return self.deleted_at is not None

    def can_be_deleted(self, current_date=None):
        current_date = current_date or datetime.now()
        return current_date > self.archived_until

    def mark_deleted(self, current_date=None):
        if not self.can_be_deleted(current_date):
            raise ValueError("Bericht darf noch nicht gelöscht werden.")

        self.deleted_at = current_date or datetime.now()


class ArchiveService:
    def __init__(self, audit_log):
        self.audit_log = audit_log
        self.archived_reports = []

    def archive_report(self, report, report_id, actor_id):
        archived_report = ArchivedReport(
            report_id=report_id,
            employee_id=report["employee_id"],
            year=report["year"],
            month=report["month"],
            content=report
        )

        self.archived_reports.append(archived_report)

        self.audit_log.record(
            actor_id=actor_id,
            action="archive_report",
            target_type="ArchivedReport",
            target_id=report_id,
            details={
                "employee_id": report["employee_id"],
                "month": report["month"],
                "year": report["year"],
                "archived_until": archived_report.archived_until.isoformat()
            }
        )

        return archived_report

    def get_archived_reports(self):
        return self.archived_reports

    def find_by_employee(self, employee_id):
        return [
            report for report in self.archived_reports
            if report.employee_id == employee_id and not report.is_deleted()
        ]

    def find_deletable_reports(self, current_date=None):
        return [
            report for report in self.archived_reports
            if report.can_be_deleted(current_date) and not report.is_deleted()
        ]

    def delete_report(self, report_id, actor_id, current_date=None):
        report = self.find_by_id(report_id)

        if report is None:
            raise ValueError("Archivierter Bericht wurde nicht gefunden.")

        report.mark_deleted(current_date)

        self.audit_log.record(
            actor_id=actor_id,
            action="delete_archived_report",
            target_type="ArchivedReport",
            target_id=report_id,
            details={
                "employee_id": report.employee_id,
                "month": report.month,
                "year": report.year,
                "deleted_at": report.deleted_at.isoformat()
            }
        )

        return report

    def find_by_id(self, report_id):
        for report in self.archived_reports:
            if report.report_id == report_id:
                return report

        return None
