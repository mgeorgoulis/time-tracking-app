from datetime import datetime

from backend.models.audit_log import AuditLog
from backend.models.timesheet import Timesheet
from backend.models.user import Admin, DepartmentManager, Employee, Executive
from backend.services.auth_service import AuthService
from backend.services.permission_service import PermissionService
from backend.services.report_service import ReportService
from backend.services.sqlite_store import SQLiteStore
from backend.services.time_tracking_service import TimeTrackingService


DATABASE_PATH = "data/time_tracking.db"


def sync_audit_log(store, audit_log, synced_count):
    new_entries = audit_log.get_entries()[synced_count:]

    for entry in new_entries:
        store.save_audit_log_entry(entry)

    return len(audit_log.get_entries())


def seed_default_admin(store):
    if len(store.get_all_users()) > 0:
        return

    admin = Admin(
        user_id=1,
        name="Default Admin",
        pin_code="9999"
    )

    store.add_user(admin)

    print("Standard-Admin wurde erstellt.")
    print("Benutzer-ID: 1")
    print("PIN: 9999")
    print()


def input_int(prompt):
    while True:
        value = input(prompt)

        try:
            return int(value)
        except ValueError:
            print("Bitte eine gültige Zahl eingeben.")


def create_user(store, current_user, permission_service):
    if not permission_service.can_manage_users(current_user):
        print("Keine Berechtigung: Nur Admins dürfen Benutzer anlegen.")
        return

    print()
    print("=== Benutzer anlegen ===")
    print("Rollen:")
    print("1 = Mitarbeiter")
    print("2 = Abteilungsleiter")
    print("3 = Geschäftsführung")
    print("4 = Admin")
    print()

    user_id = input_int("Benutzer-ID: ")
    name = input("Name: ")
    pin_code = input("4-stellige PIN: ")
    role_choice = input("Rolle auswählen: ")

    try:
        if role_choice == "1":
            department = input("Abteilung: ")
            user = Employee(user_id, name, pin_code, department)

        elif role_choice == "2":
            department = input("Abteilung: ")
            user = DepartmentManager(user_id, name, pin_code, department)

        elif role_choice == "3":
            user = Executive(user_id, name, pin_code)

        elif role_choice == "4":
            user = Admin(user_id, name, pin_code)

        else:
            print("Ungültige Rolle.")
            return

        store.add_user(user)
        print(f"Benutzer angelegt: {user.name} ({user.role})")

    except ValueError as error:
        print(f"Fehler: {error}")


def login(store, audit_log):
    print()
    print("=== Login ===")

    user_id = input_int("Benutzer-ID: ")
    pin_code = input("PIN: ")

    auth_service = AuthService(store.get_all_users(), audit_log)

    try:
        user = auth_service.login_with_pin(user_id, pin_code)
        print(f"Login erfolgreich: {user.name} ({user.role})")
        return user
    except ValueError as error:
        print(f"Login fehlgeschlagen: {error}")
        return None


def clock_in(current_user, time_tracking_service):
    try:
        time_tracking_service.clock_in(current_user)
        print("Einstempeln erfolgreich.")
    except ValueError as error:
        print(f"Fehler: {error}")


def add_break(current_user, time_tracking_service):
    minutes = input_int("Pausenzeit in Minuten: ")

    try:
        time_tracking_service.add_break(current_user, minutes)
        print(f"Pause hinzugefügt: {minutes} Minuten")
    except ValueError as error:
        print(f"Fehler: {error}")


def clock_out(store, current_user, time_tracking_service):
    try:
        entry = time_tracking_service.clock_out(current_user)
        print("Ausstempeln erfolgreich.")
        print(f"Gearbeitete Minuten: {entry.worked_minutes()}")
    except ValueError as error:
        print(f"Fehler: {error}")


def show_monthly_report(store, current_user, report_service):
    print()
    print("=== Monatsbericht ===")

    year = input_int("Jahr, z. B. 2026: ")
    month = input_int("Monat, z. B. 1: ")
    expected_minutes = input_int("Soll-Minuten für diesen Zeitraum, z. B. 480: ")

    entries = store.get_time_entries_by_employee(current_user.user_id)

    filtered_entries = [
        entry for entry in entries
        if entry.clock_in_time is not None
        and entry.clock_in_time.year == year
        and entry.clock_in_time.month == month
    ]

    timesheet = Timesheet(
        employee=current_user,
        month=month,
        year=year,
        expected_minutes=expected_minutes
    )

    for entry in filtered_entries:
        timesheet.add_entry(entry)

    print()
    print(report_service.generate_printable_report(timesheet))


def show_users(store, current_user, permission_service):
    if not permission_service.can_manage_users(current_user):
        print("Keine Berechtigung: Nur Admins dürfen alle Benutzer anzeigen.")
        return

    print()
    print("=== Benutzerliste ===")

    for user in store.get_all_users():
        department = getattr(user, "department", "-")
        print(f"{user.user_id}: {user.name} | Rolle: {user.role} | Abteilung: {department}")


def show_audit_log(store, current_user):
    if current_user.role not in ["admin", "executive"]:
        print("Keine Berechtigung: Nur Admin oder Geschäftsführung dürfen das Audit-Log sehen.")
        return

    print()
    print("=== Audit-Log ===")

    entries = store.get_audit_log_entries()

    if not entries:
        print("Noch keine Audit-Log-Einträge vorhanden.")
        return

    for entry in entries:
        print(entry.to_dict())


def print_menu(current_user):
    print()
    print("=== Time Tracking CLI ===")
    print(f"Aktiver Benutzer: {current_user.name} ({current_user.role})")
    print()
    print("1 = Benutzer anlegen")
    print("2 = Benutzer anzeigen")
    print("3 = Einstempeln")
    print("4 = Pause hinzufügen")
    print("5 = Ausstempeln")
    print("6 = Monatsbericht anzeigen")
    print("7 = Audit-Log anzeigen")
    print("8 = Logout")
    print("0 = Beenden")
    print()


def main():
    store = SQLiteStore(DATABASE_PATH)
    audit_log = AuditLog()
    permission_service = PermissionService()
    time_tracking_service = TimeTrackingService(audit_log, store)
    report_service = ReportService()

    synced_audit_count = 0

    seed_default_admin(store)

    current_user = None

    while True:
        if current_user is None:
            current_user = login(store, audit_log)
            synced_audit_count = sync_audit_log(store, audit_log, synced_audit_count)

            if current_user is None:
                continue

        print_menu(current_user)
        choice = input("Auswahl: ")

        if choice == "1":
            create_user(store, current_user, permission_service)

        elif choice == "2":
            show_users(store, current_user, permission_service)

        elif choice == "3":
            clock_in(current_user, time_tracking_service)

        elif choice == "4":
            add_break(current_user, time_tracking_service)

        elif choice == "5":
            clock_out(store, current_user, time_tracking_service)

        elif choice == "6":
            show_monthly_report(store, current_user, report_service)

        elif choice == "7":
            show_audit_log(store, current_user)

        elif choice == "8":
            print("Logout.")
            current_user = None

        elif choice == "0":
            synced_audit_count = sync_audit_log(store, audit_log, synced_audit_count)
            store.close()
            print("Programm beendet.")
            break

        else:
            print("Ungültige Auswahl.")

        synced_audit_count = sync_audit_log(store, audit_log, synced_audit_count)


if __name__ == "__main__":
    main()
