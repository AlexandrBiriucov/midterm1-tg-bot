from datetime import datetime

class Timer:
    def __init__(self, duration_seconds: int):
        self.duration = duration_seconds
        self.start_time = None
        self.task = None

    def start(self):
        self.start_time = datetime.now()

    def remaining_seconds(self) -> int:
        if not self.start_time:
            return self.duration
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return max(0, self.duration - int(elapsed))

# Хранилища
timers: dict[int, Timer] = {}
settings: dict[int, dict[str, int]] = {}

# Presets storage: user_id -> list of {"name": str, "seconds": int}
presets: dict[int, list[dict]] = {}