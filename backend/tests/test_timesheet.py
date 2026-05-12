import unittest
from datetime import datetime

from backend.models.user import Employee
from backend.models.time_entry import TimeEntry
from backend.models.timesheet import Timesheet


class TestTimesheet(unittest.TestCase):

    def test_add_entry_adds_time_entry(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        timesheet = Timesheet(employee, month=1, year=2026)

        entry = TimeEntry(employee_id=1)
        entry.clock_in_time = datetime(2026, 1, 1, 8, 0)
        entry.clock_out_time = datetime(2026, 1, 1, 16, 0)

        timesheet.add_entry(entry)

        self.assertEqual(len(timesheet.entries), 1)

    def test_add_entry_with_wrong_employee_raises_error(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        timesheet = Timesheet(employee, month=1, year=2026)

        wrong_entry = TimeEntry(employee_id=99)

        with self.assertRaises(ValueError):
            timesheet.add_entry(wrong_entry)

    def test_total_worked_minutes_calculates_sum(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        timesheet = Timesheet(employee, month=1, year=2026)

        entry_one = TimeEntry(employee_id=1)
        entry_one.clock_in_time = datetime(2026, 1, 1, 8, 0)
        entry_one.clock_out_time = datetime(2026, 1, 1, 12, 0)

        entry_two = TimeEntry(employee_id=1)
        entry_two.clock_in_time = datetime(2026, 1, 2, 8, 0)
        entry_two.clock_out_time = datetime(2026, 1, 2, 16, 30)
        entry_two.add_break(30)

        timesheet.add_entry(entry_one)
        timesheet.add_entry(entry_two)

        self.assertEqual(timesheet.total_worked_minutes(), 720)

    def test_overtime_minutes_calculates_difference(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        timesheet = Timesheet(employee, month=1, year=2026, expected_minutes=480)

        entry = TimeEntry(employee_id=1)
        entry.clock_in_time = datetime(2026, 1, 1, 8, 0)
        entry.clock_out_time = datetime(2026, 1, 1, 17, 0)
        entry.add_break(30)

        timesheet.add_entry(entry)

        self.assertEqual(timesheet.overtime_minutes(), 30)

    def test_confirm_with_correct_pin(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        timesheet = Timesheet(employee, month=1, year=2026)

        result = timesheet.confirm("1234")

        self.assertTrue(result)
        self.assertTrue(timesheet.confirmed)
        self.assertIsNotNone(timesheet.confirmed_at)
        self.assertEqual(timesheet.confirmation_method, "pin")

    def test_confirm_with_wrong_pin_raises_error(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        timesheet = Timesheet(employee, month=1, year=2026)

        with self.assertRaises(ValueError):
            timesheet.confirm("9999")

    def test_confirm_twice_raises_error(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        timesheet = Timesheet(employee, month=1, year=2026)

        timesheet.confirm("1234")

        with self.assertRaises(ValueError):
            timesheet.confirm("1234")


if __name__ == "__main__":
    unittest.main()
