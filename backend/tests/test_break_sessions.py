import unittest
from datetime import datetime

from backend.models.time_entry import TimeEntry


class TestTimeEntryBreakSessions(unittest.TestCase):

    def test_start_break_sets_break_started_at(self):
        entry = TimeEntry(employee_id=1)
        entry.clock_in_time = datetime(2026, 1, 1, 8, 0)

        entry.start_break(datetime(2026, 1, 1, 10, 0))

        self.assertIsNotNone(entry.break_started_at)
        self.assertTrue(entry.is_on_break())

    def test_end_break_adds_break_minutes(self):
        entry = TimeEntry(employee_id=1)
        entry.clock_in_time = datetime(2026, 1, 1, 8, 0)

        entry.start_break(datetime(2026, 1, 1, 10, 0))
        duration = entry.end_break(datetime(2026, 1, 1, 10, 17))

        self.assertEqual(duration, 17)
        self.assertEqual(entry.break_minutes, 17)
        self.assertIsNone(entry.break_started_at)
        self.assertFalse(entry.is_on_break())

    def test_multiple_breaks_are_added(self):
        entry = TimeEntry(employee_id=1)
        entry.clock_in_time = datetime(2026, 1, 1, 8, 0)

        entry.start_break(datetime(2026, 1, 1, 10, 0))
        entry.end_break(datetime(2026, 1, 1, 10, 15))

        entry.start_break(datetime(2026, 1, 1, 12, 0))
        entry.end_break(datetime(2026, 1, 1, 12, 30))

        self.assertEqual(entry.break_minutes, 45)

    def test_start_break_without_clock_in_raises_error(self):
        entry = TimeEntry(employee_id=1)

        with self.assertRaises(ValueError):
            entry.start_break(datetime(2026, 1, 1, 10, 0))

    def test_start_break_twice_raises_error(self):
        entry = TimeEntry(employee_id=1)
        entry.clock_in_time = datetime(2026, 1, 1, 8, 0)

        entry.start_break(datetime(2026, 1, 1, 10, 0))

        with self.assertRaises(ValueError):
            entry.start_break(datetime(2026, 1, 1, 10, 5))

    def test_end_break_without_active_break_raises_error(self):
        entry = TimeEntry(employee_id=1)
        entry.clock_in_time = datetime(2026, 1, 1, 8, 0)

        with self.assertRaises(ValueError):
            entry.end_break(datetime(2026, 1, 1, 10, 15))

    def test_clock_out_while_break_is_active_raises_error(self):
        entry = TimeEntry(employee_id=1)
        entry.clock_in_time = datetime(2026, 1, 1, 8, 0)

        entry.start_break(datetime(2026, 1, 1, 10, 0))

        with self.assertRaises(ValueError):
            entry.clock_out(datetime(2026, 1, 1, 16, 0))

    def test_worked_minutes_uses_added_breaks(self):
        entry = TimeEntry(employee_id=1)
        entry.clock_in_time = datetime(2026, 1, 1, 8, 0)

        entry.start_break(datetime(2026, 1, 1, 10, 0))
        entry.end_break(datetime(2026, 1, 1, 10, 15))

        entry.start_break(datetime(2026, 1, 1, 12, 0))
        entry.end_break(datetime(2026, 1, 1, 12, 30))

        entry.clock_out(datetime(2026, 1, 1, 16, 30))

        self.assertEqual(entry.break_minutes, 45)
        self.assertEqual(entry.worked_minutes(), 465)


if __name__ == "__main__":
    unittest.main()
