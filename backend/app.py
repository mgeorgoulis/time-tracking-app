from datetime import datetime

from backend.models.user import Employee
from backend.models.audit_log import AuditLog
from backend.models.timesheet import Timesheet
from backend.services.auth_service import AuthService
from backend.services.time_tracking_service import TimeTrackingService
from backend.services.report_service import ReportService


def main():
    print("=== Time Tracking App Demo ===")
    print()

    employee = Employee(
        user_id=1,
        name="Max Mitarbeiter",
        pin_code="1234",
        department="Verkauf"
    )

    users = [employee]

    audit_log = AuditLog()
    auth_service = AuthService(users, audit_log)
    time_tracking_service = TimeTrackingService(audit_log)
    report_service = ReportService()

    print("Login per Mitarbeiter-ID und PIN...")
    logged_in_employee = auth_service.login_with_pin(
        user_id=1,
        pin_code="1234"
    )

    print(f"Login erfolgreich: {logged_in_employee.name}")
    print(f"Abteilung: {logged_in_employee.department}")
    print()

    print("Mitarbeiter stempelt ein...")
    entry = time_tracking_service.clock_in(
        logged_in_employee,
        timestamp=datetime(2026, 1, 1, 8, 0)
    )

    print("Pause wird hinzugefügt: 30 Minuten")
    time_tracking_service.add_break(logged_in_employee, 30)

    print("Mitarbeiter stempelt aus...")
    completed_entry = time_tracking_service.clock_out(
        logged_in_employee,
        timestamp=datetime(2026, 1, 1, 16, 30)
    )

    print()

    timesheet = Timesheet(
        employee=logged_in_employee,
        month=1,
        year=2026,
        expected_minutes=480
    )

    timesheet.add_entry(completed_entry)

    print("Stundenzettel wird per PIN quittiert...")
    timesheet.confirm("1234")

    print()
    print("=== Monatsbericht ===")
    print()

    printable_report = report_service.generate_printable_report(timesheet)
    print(printable_report)

    print()
    print("=== Audit Log ===")
    print()

    for audit_entry in audit_log.get_entries():
        print(audit_entry.to_dict())


if __name__ == "__main__":
    main()
