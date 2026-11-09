
from enum import Enum
from threading import Event, RLock


class BotStatus(str, Enum):
    IDLE = "Idle"
    RUNNING = "Running"
    PAUSED = "Paused"
    STOPPING = "Stopping"
    STOPPED = "Stopped"


class StateManager:

    def __init__(self):
        self.stop_event = Event()
        self.pause_event = Event()

        self._lock = RLock()

        self.status = BotStatus.IDLE
        self.cycle_count = 0

    def start(self):
        with self._lock:
            if self.status in (
                BotStatus.RUNNING,
                BotStatus.PAUSED,
                BotStatus.STOPPING
            ):
                return False

            self.stop_event.clear()
            self.pause_event.clear()

            self.status = BotStatus.RUNNING
            self.cycle_count = 0

            return True

    def pause(self):
        with self._lock:
            if self.status != BotStatus.RUNNING:
                return False

            self.pause_event.set()
            self.status = BotStatus.PAUSED

            return True

    def resume(self):
        with self._lock:
            if self.status != BotStatus.PAUSED:
                return False

            self.pause_event.clear()
            self.status = BotStatus.RUNNING

            return True

    def stop(self):
        with self._lock:
            if self.status not in (
                BotStatus.RUNNING,
                BotStatus.PAUSED
            ):
                return False

            self.status = BotStatus.STOPPING

            self.stop_event.set()
            self.pause_event.clear()

            return True

    def mark_stopped(self):
        with self._lock:
            self.status = BotStatus.STOPPED

    def increment_cycle(self):
        with self._lock:
            self.cycle_count += 1
            return self.cycle_count
