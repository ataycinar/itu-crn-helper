import logging
import os
from datetime import datetime

if not os.path.exists('logs'):
    os.makedirs('logs')


timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")  # safe format
logFile = os.path.join("logs", timestamp + ".log")
print(logFile)

# Create handlers with different log levels
file_handler = logging.FileHandler(logFile, encoding="utf-8")
file_handler.setLevel(logging.DEBUG)  # File gets all logs including debug

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Console only gets INFO and above

logging.basicConfig(
    level=logging.DEBUG,  # Root logger level (lowest level)
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        file_handler,
        console_handler
    ]
)

logger = logging.getLogger("logger")

def debug(msg):
    logger.debug(msg)

def info(msg):
    logger.info(msg)

def warning(msg):
    logger.warning(msg)

def error(msg):
    logger.error(msg)

def critical(msg):
    logger.critical(msg)

if __name__ == "__main__":
    info("This is an info message")
    debug("This is a debug message")
    warning("This is a warning message")
    error("This is an error message")
    critical("This is a critical message")