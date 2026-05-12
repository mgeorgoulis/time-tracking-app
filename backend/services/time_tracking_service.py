from backend.models.time_entry import TimeEntry


class TimeTrackingService:
    def __init__(self, audit_log):
        self.audit_log = audit_log
        self.active_entries = {}
        self.completed_entries = []

    def clock_in(self, employee, timestamp=None):
        if employee.user_id in self.active_entries:
            raise ValueError("Mitarbeiter ist bereits eingestempelt.")

        entry = TimeEntry(employee_id=employee.user_id)
        entry.clock_in(timestamp=timestamp)

        self.active_entries[employee.user_id] = entry

        self.audit_log.record(
            actor_id=employee.user_id,
            action="clock_in",
            target_type="TimeEntry",
            details={"employee_name": employee.name}
        )

        return entry

    def clock_out(self, employee, timestamp=None):
        if employee.user_id not in self.active_entries:
            raise ValueError("Mitarbeiter ist nicht eingestempelt.")

        entry = self.active_entries[employee.user_id]
        entry.clock_out(timestamp=timestamp)

        self.completed_entries.append(entry)
        del self.active_entries[employee.user_id]

        self.audit_log.record(
            actor_id=employee.user_id,
            action="clock_out",
            target_type="TimeEntry",
            details={
                "employee_name": employee.name,
                "worked_minutes": entry.worked_minutes()
            }
        )

        return entry

    def add_break(self, employee, minutes):
        if employee.user_id not in self.active_entries:
            raise ValueError("Mitarbeiter ist nicht eingestempelt.")

        entry = self.active_entries[employee.user_id]
        entry.add_break(minutes)

        self.audit_log.record(
            actor_id=employee.user_id,
            action="add_break",
            target_type="TimeEntry",
            details={
                "employee_name": employee.name,
                "break_minutes": minutes
            }
        )

        return entry

    def get_active_entry(self, employee_id):
        return self.active_entries.get(employee_id)

    def get_completed_entries(self, employee_id=None):
        if employee_id is None:
            return self.completed_entries

        return [
            entry for entry in self.completed_entries
            if entry.employee_id == employee_id
        ]
