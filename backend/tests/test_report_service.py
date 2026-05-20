import unittest
from datetime import datetime

from backend.models.user import Employee
from backend.models.time_entry import TimeEntry
from backend.models.timesheet import Timesheet
from backend.services.report_service import ReportService


class TestReportService(unittest.TestCase):

    def test_format_minutes_positive_value(self):
        service = ReportService()

        result = service.format_minutes(480)

        self.assertEqual(result, "08:00")

    def test_format_minutes_negative_value(self):
        service = ReportService()

        result = service.format_minutes(-30)

        self.assertEqual(result, "-00:30")

    def test_generate_monthly_report_contains_employee_data(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        timesheet = Timesheet(employee, month=1, year=2026, expected_minutes=480)
        service = ReportService()

        report = service.generate_monthly_report(timesheet)

        self.assertEqual(report["employee_id"], 1)
        self.assertEqual(report["employee_name"], "Max Mitarbeiter")
        self.assertEqual(report["department"], "Verkauf")
        self.assertEqual(report["month"], 1)
        self.assertEqual(report["year"], 2026)

    def test_generate_monthly_report_calculates_worked_time(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        timesheet = Timesheet(employee, month=1, year=2026, expected_minutes=480)

        entry = TimeEntry(employee_id=1)
        entry.clock_in_time = datetime(2026, 1, 1, 8, 0)
        entry.clock_out_time = datetime(2026, 1, 1, 16, 30)
        entry.add_break(30)

        timesheet.add_entry(entry)

        service = ReportService()
        report = service.generate_monthly_report(timesheet)

        self.assertEqual(report["worked_minutes"], 480)
        self.assertEqual(report["worked_time"], "08:00")
        self.assertEqual(report["break_minutes"], 30)
        self.assertEqual(report["break_time"], "00:30")
        self.assertEqual(report["overtime_minutes"], 0)
        self.assertEqual(report["overtime_time"], "00:00")

    def test_generate_monthly_report_calculates_overtime(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        timesheet = Timesheet(employee, month=1, year=2026, expected_minutes=480)

        entry = TimeEntry(employee_id=1)
        entry.clock_in_time = datetime(2026, 1, 1, 8, 0)
        entry.clock_out_time = datetime(2026, 1, 1, 17, 0)
        entry.add_break(30)

        timesheet.add_entry(entry)

        service = ReportService()
        report = service.generate_monthly_report(timesheet)

        self.assertEqual(report["worked_minutes"], 510)
        self.assertEqual(report["overtime_minutes"], 30)
        self.assertEqual(report["overtime_time"], "00:30")

    def test_generate_monthly_report_includes_confirmation_data(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        timesheet = Timesheet(employee, month=1, year=2026)

        timesheet.confirm("1234")

        service = ReportService()
        report = service.generate_monthly_report(timesheet)

        self.assertTrue(report["confirmed"])
        self.assertIsNotNone(report["confirmed_at"])
        self.assertEqual(report["confirmation_method"], "pin")

    def test_generate_printable_report_contains_relevant_information(self):
        employee = Employee(1, "Max Mitarbeiter", "1234", "Verkauf")
        timesheet = Timesheet(employee, month=1, year=2026, expected_minutes=480)

        service = ReportService()
        printable_report = service.generate_printable_report(timesheet)

        self.assertIn("Monatsbericht Arbeitszeit", printable_report)
        self.assertIn("Max Mitarbeiter", printable_report)
        self.assertIn("Verkauf", printable_report)
        self.assertIn("Soll-Zeit: 08:00 Stunden", printable_report)
        self.assertIn("Quittiert: Nein", printable_report)
        self.assertIn("Unterschrift Mitarbeiter", printable_report)


if __name__ == "__main__":
    unittest.main()
