from datetime import datetime


class TimeEntry:
    def __init__(self, employee_id, entry_id=None):
        self.entry_id = entry_id
        self.employee_id = employee_id
        self.clock_in_time = None
        self.clock_out_time = None
        self.break_minutes = 0
        self.break_started_at = None

    def clock_in(self, timestamp=None):
        if self.clock_in_time is not None:
            raise ValueError("Mitarbeiter ist bereits eingestempelt.")

        self.clock_in_time = timestamp or datetime.now()

    def clock_out(self, timestamp=None):
        if self.clock_in_time is None:
            raise ValueError("Mitarbeiter ist nicht eingestempelt.")

        if self.clock_out_time is not None:
            raise ValueError("Mitarbeiter ist bereits ausgestempelt.")

        if self.break_started_at is not None:
            raise ValueError("Pause muss beendet werden, bevor ausgestempelt werden kann.")

        self.clock_out_time = timestamp or datetime.now()

    def add_break(self, minutes):
        if minutes < 0:
            raise ValueError("Pause darf nicht negativ sein.")

        self.break_minutes += minutes

    def start_break(self, timestamp=None):
        if self.clock_in_time is None:
            raise ValueError("Pause kann nicht vor dem Einstempeln begonnen werden.")

        if self.clock_out_time is not None:
            raise ValueError("Pause kann nicht nach dem Ausstempeln begonnen werden.")

        if self.break_started_at is not None:
            raise ValueError("Pause läuft bereits.")

        self.break_started_at = timestamp or datetime.now()

    def end_break(self, timestamp=None):
        if self.break_started_at is None:
            raise ValueError("Es läuft aktuell keine Pause.")

        end_time = timestamp or datetime.now()

        if end_time < self.break_started_at:
            raise ValueError("Pausenende darf nicht vor Pausenbeginn liegen.")

        duration_minutes = int((end_time - self.break_started_at).total_seconds() // 60)

        self.break_minutes += duration_minutes
        self.break_started_at = None

        return duration_minutes

    def is_on_break(self):
        return self.break_started_at is not None

    def worked_minutes(self):
        if self.clock_in_time is None or self.clock_out_time is None:
            return 0

        total_time = self.clock_out_time - self.clock_in_time
        total_minutes = int(total_time.total_seconds() / 60)

        return total_minutes - self.break_minutes
