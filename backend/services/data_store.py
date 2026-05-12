class DataStore:
    def __init__(self):
        self.users = {}
        self.timesheets = {}

    def add_user(self, user):
        if user.user_id in self.users:
            raise ValueError("Benutzer-ID existiert bereits.")

        self.users[user.user_id] = user
        return user

    def get_user_by_id(self, user_id):
        return self.users.get(user_id)

    def get_all_users(self):
        return list(self.users.values())

    def get_users_by_role(self, role):
        return [
            user for user in self.users.values()
            if getattr(user, "role", None) == role
        ]

    def get_users_by_department(self, department):
        return [
            user for user in self.users.values()
            if getattr(user, "department", None) == department
        ]

    def add_timesheet(self, timesheet):
        key = self._timesheet_key(
            timesheet.employee.user_id,
            timesheet.year,
            timesheet.month
        )

        if key in self.timesheets:
            raise ValueError("Stundenzettel existiert bereits.")

        self.timesheets[key] = timesheet
        return timesheet

    def get_timesheet(self, employee_id, year, month):
        key = self._timesheet_key(employee_id, year, month)
        return self.timesheets.get(key)

    def get_timesheets_by_employee(self, employee_id):
        return [
            timesheet for timesheet in self.timesheets.values()
            if timesheet.employee.user_id == employee_id
        ]

    def get_timesheets_by_month(self, year, month):
        return [
            timesheet for timesheet in self.timesheets.values()
            if timesheet.year == year and timesheet.month == month
        ]

    def _timesheet_key(self, employee_id, year, month):
        return (employee_id, year, month)
