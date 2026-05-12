from datetime import datetime


class Timesheet:
    def __init__(self, employee, month, year, expected_minutes=0):
        self.employee = employee
        self.month = month
        self.year = year
        self.expected_minutes = expected_minutes
        self.entries = []
        self.confirmed = False
        self.confirmed_at = None
        self.confirmation_method = None

    def add_entry(self, entry):
        if entry.employee_id != self.employee.user_id:
            raise ValueError("Zeiteintrag gehört nicht zu diesem Mitarbeiter.")
        self.entries.append(entry)

    def total_worked_minutes(self):
        return sum(entry.worked_minutes() for entry in self.entries)

    def overtime_minutes(self):
        return self.total_worked_minutes() - self.expected_minutes

    def confirm(self, pin_code):
        if self.confirmed:
            raise ValueError("Stundenzettel wurde bereits quittiert.")

        if not self.employee.check_pin(pin_code):
            raise ValueError("PIN-Code ist ungültig.")

        self.confirmed = True
        self.confirmed_at = datetime.now()
        self.confirmation_method = "pin"

        return True
