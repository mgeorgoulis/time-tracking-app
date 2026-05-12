import unittest

from backend.models.user import Employee, DepartmentManager, Executive, Admin


class TestPermissions(unittest.TestCase):

    def test_employee_cannot_create_reports(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        self.assertFalse(employee.can_create_reports())

    def test_department_manager_can_create_reports(self):
        manager = DepartmentManager(2, "Anna Leitung", "2345", "Verkauf")
        self.assertTrue(manager.can_create_reports())

    def test_executive_can_view_all_times(self):
        executive = Executive(3, "Erika Geschäftsführung", "3456")
        self.assertTrue(executive.can_view_all_times())

    def test_admin_can_manage_users(self):
        admin = Admin(4, "Alex Admin", "4567")
        self.assertTrue(admin.can_manage_users())

    def test_pin_check_correct_pin(self):
        employee = Employee(5, "Lena Mitarbeiterin", "9999", "Service")
        self.assertTrue(employee.check_pin("9999"))

    def test_pin_check_wrong_pin(self):
        employee = Employee(6, "Tom Mitarbeiter", "1111", "Lager")
        self.assertFalse(employee.check_pin("1234"))


if __name__ == "__main__":
    unittest.main()
