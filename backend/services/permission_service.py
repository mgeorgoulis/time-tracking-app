class PermissionService:
    def can_manage_users(self, user):
        return user.can_manage_users()

    def can_create_reports(self, user):
        return user.can_create_reports()

    def can_view_all_times(self, user):
        return user.can_view_all_times()

    def can_view_employee_times(self, viewer, employee):
        if viewer.user_id == employee.user_id:
            return True

        if viewer.role in ["admin", "executive"]:
            return True

        if viewer.role == "department_manager":
            return viewer.department == employee.department

        return False

    def can_create_company_report(self, user):
        return user.role in ["admin", "executive"]

    def can_create_department_report(self, user, department):
        if user.role in ["admin", "executive"]:
            return True

        if user.role == "department_manager":
            return user.department == department

        return False

    def can_confirm_timesheet(self, user, timesheet):
        return user.user_id == timesheet.employee.user_id
