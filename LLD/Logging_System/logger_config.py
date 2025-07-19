from log_level import LogLevel
from log_appender import LogAppender

class LoggerConfig:
    def __init__(self, log_level:LogLevel, log_appender:LogAppender):
        self.log_level = log_level
        self.log_appender = log_appender
    
    def get_log_level(self):
        return self.log_level
    
    def set_log_level(self, log_level):
        self.log_level = log_level
    
    def get_log_appender(self):
        return self.log_appender
    
    def set_log_appender(self, log_appender):
        self.log_appender = log_appender    