from datetime import datetime


class TimeEntry:
    def __init__(self, employee_id):
        self.employee_id = employee_id
        self.clock_in_time = None
        self.clock_out_time = None
        self.break_minutes = 0

    def clock_in(self):
        if self.clock_in_time is not None:
            raise ValueError("Mitarbeiter ist bereits eingestempelt.")
        self.clock_in_time = datetime.now()

    def clock_out(self):
        if self.clock_in_time is None:
            raise ValueError("Mitarbeiter ist nicht eingestempelt.")
        if self.clock_out_time is not None:
            raise ValueError("Mitarbeiter ist bereits ausgestempelt.")
        self.clock_out_time = datetime.now()

    def add_break(self, minutes):
        if minutes < 0:
            raise ValueError("Pause darf nicht negativ sein.")
        self.break_minutes += minutes

    def worked_minutes(self):
        if self.clock_in_time is None or self.clock_out_time is None:
            return 0

        total_time = self.clock_out_time - self.clock_in_time
        total_minutes = int(total_time.total_seconds() / 60)

        return total_minutes - self.break_minutes
