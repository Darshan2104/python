from logger import Logger
from logger_config import LoggerConfig
from log_level import LogLevel
from log_appender import FileAppender


class LoggerDemo:
    @staticmethod
    def run_demo():
        # Create a logger instance
        logger = Logger.get_instance()

        # Logging with default configuration
        logger.debug("This is a debug message.")
        logger.info("This is an info message.")
        logger.warning("This is a warning message.")
        logger.error("This is an error message.")
        logger.fatal("This is a fatal message.")

        # Set a custom configuration with a file appender
        config = LoggerConfig(LogLevel.DEBUG, FileAppender("log.txt"))
        logger.set_config(config)

        # Log messages of various levels
        logger.debug("This is a debug message.")
        logger.info("This is an info message.")
        logger.warning("This is a warning message.")
        logger.error("This is an error message.")
        logger.fatal("This is a fatal message.")

if __name__ == "__main__":
    LoggerDemo.run_demo()