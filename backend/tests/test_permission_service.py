import unittest

from backend.models.user import Employee, DepartmentManager, Executive, Admin
from backend.models.timesheet import Timesheet
from backend.services.permission_service import PermissionService


class TestPermissionService(unittest.TestCase):

    def test_employee_can_view_own_times(self):
        service = PermissionService()
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")

        result = service.can_view_employee_times(employee, employee)

        self.assertTrue(result)

    def test_employee_cannot_view_other_employee_times(self):
        service = PermissionService()
        employee_one = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        employee_two = Employee(2, "Lena Mitarbeiterin", "2345", "Lager")

        result = service.can_view_employee_times(employee_one, employee_two)

        self.assertFalse(result)

    def test_department_manager_can_view_employee_in_same_department(self):
        service = PermissionService()
        manager = DepartmentManager(1, "Anna Leitung", "1234", "Verkauf")
        employee = Employee(2, "Max Mitarbeiter", "2345", "Verkauf")

        result = service.can_view_employee_times(manager, employee)

        self.assertTrue(result)

    def test_department_manager_cannot_view_employee_in_other_department(self):
        service = PermissionService()
        manager = DepartmentManager(1, "Anna Leitung", "1234", "Verkauf")
        employee = Employee(2, "Tom Mitarbeiter", "2345", "Lager")

        result = service.can_view_employee_times(manager, employee)

        self.assertFalse(result)

    def test_executive_can_view_all_employee_times(self):
        service = PermissionService()
        executive = Executive(1, "Erika Geschäftsführung", "1234")
        employee = Employee(2, "Max Mitarbeiter", "2345", "Verkauf")

        result = service.can_view_employee_times(executive, employee)

        self.assertTrue(result)

    def test_admin_can_view_all_employee_times(self):
        service = PermissionService()
        admin = Admin(1, "Alex Admin", "1234")
        employee = Employee(2, "Max Mitarbeiter", "2345", "Verkauf")

        result = service.can_view_employee_times(admin, employee)

        self.assertTrue(result)

    def test_only_admin_can_manage_users(self):
        service = PermissionService()
        admin = Admin(1, "Alex Admin", "1234")
        employee = Employee(2, "Max Mitarbeiter", "2345", "Verkauf")

        self.assertTrue(service.can_manage_users(admin))
        self.assertFalse(service.can_manage_users(employee))

    def test_admin_and_executive_can_create_company_report(self):
        service = PermissionService()
        admin = Admin(1, "Alex Admin", "1234")
        executive = Executive(2, "Erika Geschäftsführung", "2345")
        employee = Employee(3, "Max Mitarbeiter", "3456", "Verkauf")

        self.assertTrue(service.can_create_company_report(admin))
        self.assertTrue(service.can_create_company_report(executive))
        self.assertFalse(service.can_create_company_report(employee))

    def test_department_manager_can_create_report_for_own_department(self):
        service = PermissionService()
        manager = DepartmentManager(1, "Anna Leitung", "1234", "Verkauf")

        result = service.can_create_department_report(manager, "Verkauf")

        self.assertTrue(result)

    def test_department_manager_cannot_create_report_for_other_department(self):
        service = PermissionService()
        manager = DepartmentManager(1, "Anna Leitung", "1234", "Verkauf")

        result = service.can_create_department_report(manager, "Lager")

        self.assertFalse(result)

    def test_employee_can_confirm_own_timesheet(self):
        service = PermissionService()
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        timesheet = Timesheet(employee, month=1, year=2026)

        result = service.can_confirm_timesheet(employee, timesheet)

        self.assertTrue(result)

    def test_employee_cannot_confirm_other_timesheet(self):
        service = PermissionService()
        employee_one = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        employee_two = Employee(2, "Lena Mitarbeiterin", "2345", "Verkauf")
        timesheet = Timesheet(employee_two, month=1, year=2026)

        result = service.can_confirm_timesheet(employee_one, timesheet)

        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()
