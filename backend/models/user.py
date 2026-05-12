class User:
    def __init__(self, user_id, name, pin_code):
        self.user_id = user_id
        self.name = name
        self._pin_code = pin_code

    def check_pin(self, pin_code):
        return self._pin_code == pin_code

    def can_clock_in(self):
        return True

    def can_manage_users(self):
        return False

    def can_create_reports(self):
        return False

    def can_view_all_times(self):
        return False


class Employee(User):
    def __init__(self, user_id, name, pin_code, department):
        super().__init__(user_id, name, pin_code)
        self.department = department
        self.role = "employee"


class DepartmentManager(Employee):
    def __init__(self, user_id, name, pin_code, department):
        super().__init__(user_id, name, pin_code, department)
        self.role = "department_manager"

    def can_create_reports(self):
        return True


class Executive(User):
    def __init__(self, user_id, name, pin_code):
        super().__init__(user_id, name, pin_code)
        self.role = "executive"

    def can_create_reports(self):
        return True

    def can_view_all_times(self):
        return True


class Admin(User):
    def __init__(self, user_id, name, pin_code):
        super().__init__(user_id, name, pin_code)
        self.role = "admin"

    def can_manage_users(self):
        return True

    def can_create_reports(self):
        return True

    def can_view_all_times(self):
        return True
