class ReportService:
    def format_minutes(self, minutes):
        sign = "-" if minutes < 0 else ""
        absolute_minutes = abs(minutes)

        hours = absolute_minutes // 60
        remaining_minutes = absolute_minutes % 60

        return f"{sign}{hours:02d}:{remaining_minutes:02d}"

    def generate_monthly_report(self, timesheet):
        worked_minutes = timesheet.total_worked_minutes()
        overtime_minutes = timesheet.overtime_minutes()

        confirmed_at = None
        if timesheet.confirmed_at is not None:
            confirmed_at = timesheet.confirmed_at.isoformat()

        return {
            "employee_id": timesheet.employee.user_id,
            "employee_name": timesheet.employee.name,
            "department": getattr(timesheet.employee, "department", None),
            "month": timesheet.month,
            "year": timesheet.year,
            "expected_minutes": timesheet.expected_minutes,
            "worked_minutes": worked_minutes,
            "overtime_minutes": overtime_minutes,
            "expected_time": self.format_minutes(timesheet.expected_minutes),
            "worked_time": self.format_minutes(worked_minutes),
            "overtime_time": self.format_minutes(overtime_minutes),
            "confirmed": timesheet.confirmed,
            "confirmed_at": confirmed_at,
            "confirmation_method": timesheet.confirmation_method
        }

    def generate_printable_report(self, timesheet):
        report = self.generate_monthly_report(timesheet)

        confirmed_text = "Ja" if report["confirmed"] else "Nein"
        confirmed_at = report["confirmed_at"] or "Noch nicht quittiert"
        confirmation_method = report["confirmation_method"] or "Keine"

        lines = [
            "Monatsbericht Arbeitszeit",
            "=========================",
            "",
            f"Mitarbeiter: {report['employee_name']}",
            f"Mitarbeiter-ID: {report['employee_id']}",
            f"Abteilung: {report['department']}",
            f"Zeitraum: {report['month']}/{report['year']}",
            "",
            f"Soll-Zeit: {report['expected_time']} Stunden",
            f"Ist-Zeit: {report['worked_time']} Stunden",
            f"Saldo: {report['overtime_time']} Stunden",
            "",
            f"Quittiert: {confirmed_text}",
            f"Quittiert am: {confirmed_at}",
            f"Quittierungsmethode: {confirmation_method}",
            "",
            "Unterschrift Mitarbeiter:",
            "",
            "____________________________"
        ]

        return "\n".join(lines)
