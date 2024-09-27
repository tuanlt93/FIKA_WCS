import logging
import os

class ColoredFormatter(logging.Formatter):
    FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"
    COLORS = {
        'DEBUG': "\033[94m",  # Blue
        'INFO': "\033[92m",   # Green
        'WARNING': "\033[93m",# Yellow
        'ERROR': "\033[91m",  # Red
        'CRITICAL': "\033[95m" # Purple
    }
    RESET = "\033[0m"  # Reset color to default

    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        message = super().format(record)
        # Create clickable path format (absolute path):<line_number>
        pathname = os.path.abspath(record.pathname)
        line_info = f"{pathname}:{record.lineno}"
        # return f"{log_color}{message} ({line_info}){self.RESET}"
        return f"{log_color}{message} ({line_info}){self.RESET}"

# Set up logging with colored output and clickable line info
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(ColoredFormatter())
logger.handlers = [handler]

# def exception_handler(func):
#     def wrapper(*args, **kwargs):
#         out_data = None
#         try:
#             logger.info(f"Arguments: {args}, {kwargs}")
#             out_data = func(*args, **kwargs)
#         except Exception as e:
#             logger.error(f"An exception occurred in {func.__name__}: {e}", exc_info=True)
#         return out_data

#     return wrapper

# @exception_handler
# def divide(a, b):
#     return a / b

# result = divide(a=10, b=0)


def exception_handler(func):
    def wrapper(*args, **kwargs):
        out_data = None
        try:
            logger.info(f"Arguments: {args}, {kwargs}")
            out_data = func(*args, **kwargs)
        except Exception as e:
            logger.error(f"An exception occurred in {func.__name__}: {e}", exc_info=True)
        return out_data

    return wrapper