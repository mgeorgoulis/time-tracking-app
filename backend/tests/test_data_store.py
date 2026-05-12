import unittest

from backend.models.user import Employee, DepartmentManager, Executive, Admin
from backend.models.timesheet import Timesheet
from backend.services.data_store import DataStore


class TestDataStoreUsers(unittest.TestCase):

    def test_add_user_stores_user(self):
        store = DataStore()
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")

        store.add_user(employee)

        self.assertEqual(store.get_user_by_id(1), employee)

    def test_add_duplicate_user_raises_error(self):
        store = DataStore()
        employee_one = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        employee_two = Employee(1, "Lena Mitarbeiterin", "2345", "Lager")

        store.add_user(employee_one)

        with self.assertRaises(ValueError):
            store.add_user(employee_two)

    def test_get_all_users_returns_all_users(self):
        store = DataStore()

        store.add_user(Employee(1, "Max Mitarbeiter", "1234", "Verkauf"))
        store.add_user(Employee(2, "Lena Mitarbeiterin", "2345", "Lager"))

        self.assertEqual(len(store.get_all_users()), 2)

    def test_get_users_by_role(self):
        store = DataStore()

        store.add_user(Employee(1, "Max Mitarbeiter", "1234", "Verkauf"))
        store.add_user(Admin(2, "Alex Admin", "9999"))

        admins = store.get_users_by_role("admin")

        self.assertEqual(len(admins), 1)
        self.assertEqual(admins[0].name, "Alex Admin")

    def test_get_users_by_department(self):
        store = DataStore()

        store.add_user(Employee(1, "Max Mitarbeiter", "1234", "Verkauf"))
        store.add_user(Employee(2, "Lena Mitarbeiterin", "2345", "Verkauf"))
        store.add_user(Employee(3, "Tom Mitarbeiter", "3456", "Lager"))

        verkauf_users = store.get_users_by_department("Verkauf")

        self.assertEqual(len(verkauf_users), 2)


class TestDataStoreTimesheets(unittest.TestCase):

    def test_add_timesheet_stores_timesheet(self):
        store = DataStore()
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        timesheet = Timesheet(employee, month=1, year=2026)

        store.add_timesheet(timesheet)

        result = store.get_timesheet(employee_id=1, year=2026, month=1)

        self.assertEqual(result, timesheet)

    def test_add_duplicate_timesheet_raises_error(self):
        store = DataStore()
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")

        timesheet_one = Timesheet(employee, month=1, year=2026)
        timesheet_two = Timesheet(employee, month=1, year=2026)

        store.add_timesheet(timesheet_one)

        with self.assertRaises(ValueError):
            store.add_timesheet(timesheet_two)

    def test_get_timesheets_by_employee(self):
        store = DataStore()

        employee_one = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        employee_two = Employee(2, "Lena Mitarbeiterin", "2345", "Verkauf")

        store.add_timesheet(Timesheet(employee_one, month=1, year=2026))
        store.add_timesheet(Timesheet(employee_one, month=2, year=2026))
        store.add_timesheet(Timesheet(employee_two, month=1, year=2026))

        result = store.get_timesheets_by_employee(1)

        self.assertEqual(len(result), 2)

    def test_get_timesheets_by_month(self):
        store = DataStore()

        employee_one = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        employee_two = Employee(2, "Lena Mitarbeiterin", "2345", "Lager")

        store.add_timesheet(Timesheet(employee_one, month=1, year=2026))
        store.add_timesheet(Timesheet(employee_two, month=1, year=2026))
        store.add_timesheet(Timesheet(employee_one, month=2, year=2026))

        result = store.get_timesheets_by_month(year=2026, month=1)

        self.assertEqual(len(result), 2)


if __name__ == "__main__":
    unittest.main()
