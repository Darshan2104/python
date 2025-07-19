from abc import ABC, abstractmethod
import sqlite3

class LogAppender(ABC):
    @abstractmethod
    def append(self, message: str) -> None:
        pass


# 1. ConsoleAppender
class ConsoleAppender(LogAppender):
    COLORS = {
        "DEBUG": "\033[94m",    # Blue
        "INFO": "\033[92m",     # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",    # Red
        "FATAL": "\033[95m",    # Magenta
        "RESET": "\033[0m"
    }

    def append(self, message) -> None:
        # message is a LogMessage instance
        color = self.COLORS.get(str(message.get_level()).split('.')[-1], "")
        reset = self.COLORS["RESET"]
        print(f"{color}{message}{reset}")

# 2. FileAppender
class FileAppender(LogAppender):
    def __init__(self, filename: str):
        self.filename = filename

    def append(self, message: str) -> None:
        with open(self.filename, 'a') as file:
            file.write(str(message) + '\n')

# 3. DatabaseAppender
class DatabaseAppender(LogAppender):
    def __init__(self, db_name: str):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS logs (message TEXT, log_level TEXT DEFAULT "INFO", timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)')

    def append(self, log_message: str) -> None:
        self.cursor.execute('INSERT INTO logs (message, log_level, timestamp) VALUES (?,?,?)', (log_message.get_level().name, log_message.get_message(), log_message.get_timestamp()))
        self.connection.commit()
        self.connection.close()
