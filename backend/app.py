from datetime import datetime

from backend.models.user import Employee, DepartmentManager, Executive, Admin
from backend.models.audit_log import AuditLog
from backend.models.timesheet import Timesheet
from backend.services.auth_service import AuthService
from backend.services.data_store import DataStore
from backend.services.time_tracking_service import TimeTrackingService
from backend.services.report_service import ReportService


def main():
    print("=== Time Tracking App Demo ===")
    print()

    data_store = DataStore()
    audit_log = AuditLog()

    employee_max = Employee(
        user_id=1,
        name="Max Mitarbeiter",
        pin_code="1234",
        department="Verkauf"
    )

    employee_lena = Employee(
        user_id=2,
        name="Lena Mitarbeiterin",
        pin_code="2345",
        department="Verkauf"
    )

    employee_tom = Employee(
        user_id=3,
        name="Tom Mitarbeiter",
        pin_code="3456",
        department="Lager"
    )

    manager = DepartmentManager(
        user_id=4,
        name="Anna Abteilungsleiterin",
        pin_code="4567",
        department="Verkauf"
    )

    executive = Executive(
        user_id=5,
        name="Erika Geschäftsführung",
        pin_code="5678"
    )

    admin = Admin(
        user_id=6,
        name="Alex Admin",
        pin_code="9999"
    )

    for user in [
        employee_max,
        employee_lena,
        employee_tom,
        manager,
        executive,
        admin
    ]:
        data_store.add_user(user)

    auth_service = AuthService(data_store.get_all_users(), audit_log)
    time_tracking_service = TimeTrackingService(audit_log)
    report_service = ReportService()

    print("Registrierte Benutzer:")
    for user in data_store.get_all_users():
        print(f"- {user.user_id}: {user.name} ({user.role})")

    print()
    print("Login per Mitarbeiter-ID und PIN...")
    logged_in_employee = auth_service.login_with_pin(
        user_id=1,
        pin_code="1234"
    )

    print(f"Login erfolgreich: {logged_in_employee.name}")
    print(f"Abteilung: {logged_in_employee.department}")
    print()

    print("Mitarbeiter stempelt ein...")
    time_tracking_service.clock_in(
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

    timesheet = Timesheet(
        employee=logged_in_employee,
        month=1,
        year=2026,
        expected_minutes=480
    )

    timesheet.add_entry(completed_entry)
    data_store.add_timesheet(timesheet)

    print()
    print("Stundenzettel wird per PIN quittiert...")
    timesheet.confirm("1234")

    print()
    print("=== Monatsbericht ===")
    print()

    printable_report = report_service.generate_printable_report(timesheet)
    print(printable_report)

    print()
    print("=== Abteilungsübersicht Verkauf ===")
    print()

    for user in data_store.get_users_by_department("Verkauf"):
        print(f"- {user.name} ({user.role})")

    print()
    print("=== Audit Log ===")
    print()

    for audit_entry in audit_log.get_entries():
        print(audit_entry.to_dict())


if __name__ == "__main__":
    main()
