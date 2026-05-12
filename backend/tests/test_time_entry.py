import unittest
from datetime import datetime, timedelta

from backend.models.time_entry import TimeEntry


class TestTimeEntry(unittest.TestCase):

    def test_clock_in_sets_clock_in_time(self):
        entry = TimeEntry(employee_id=1)

        entry.clock_in()

        self.assertIsNotNone(entry.clock_in_time)

    def test_clock_out_without_clock_in_raises_error(self):
        entry = TimeEntry(employee_id=1)

        with self.assertRaises(ValueError):
            entry.clock_out()

    def test_double_clock_in_raises_error(self):
        entry = TimeEntry(employee_id=1)

        entry.clock_in()

        with self.assertRaises(ValueError):
            entry.clock_in()

    def test_double_clock_out_raises_error(self):
        entry = TimeEntry(employee_id=1)

        entry.clock_in()
        entry.clock_out()

        with self.assertRaises(ValueError):
            entry.clock_out()

    def test_add_break_increases_break_minutes(self):
        entry = TimeEntry(employee_id=1)

        entry.add_break(30)

        self.assertEqual(entry.break_minutes, 30)

    def test_negative_break_raises_error(self):
        entry = TimeEntry(employee_id=1)

        with self.assertRaises(ValueError):
            entry.add_break(-15)

    def test_worked_minutes_without_clock_out_returns_zero(self):
        entry = TimeEntry(employee_id=1)

        entry.clock_in()

        self.assertEqual(entry.worked_minutes(), 0)

    def test_worked_minutes_calculates_correctly(self):
        entry = TimeEntry(employee_id=1)

        entry.clock_in_time = datetime(2026, 1, 1, 8, 0)
        entry.clock_out_time = datetime(2026, 1, 1, 16, 30)
        entry.add_break(30)

        self.assertEqual(entry.worked_minutes(), 480)


if __name__ == "__main__":
    unittest.main()
