import time
import datetime
import inspect
import os  # <-- Add this import

class LogMessage:
    def __init__(self, level, message):
        self.level = level
        self.message = message
        self.timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        frame = inspect.currentframe()
        outer_frames = inspect.getouterframes(frame)
        if len(outer_frames) > 2:
            abs_file = outer_frames[2].filename
            self.file = os.path.relpath(abs_file)
            self.line = outer_frames[2].lineno
        else:
            self.file = "unknown"
            self.line = 0

    def get_level(self):
        return self.level.name

    def get_message(self):
        return self.message

    def get_timestamp(self):
        return self.timestamp

    def get_location(self):
        return f"{self.file}:{self.line}"

    def __str__(self):
        return (f"[{self.level.name}][{self.timestamp}]"
                f"[{self.get_location()}] :=> {self.message}")