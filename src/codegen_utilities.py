

# General utilities
import time
import uuid


DEBUG = True


def log_debug(message) -> None:
    """
    Log a debug message if the DEBUG flag is set to True
    """
    if DEBUG:
        print("")
        print(f"DEBUG {time.strftime('%Y-%m-%d %H:%M:%S')}: {message}")


def get_default_resultset() -> dict:
    """
    Returns a default resultset
    """
    return {
        "resultset": {},
        "error_message": "",
        "error": False,
    }


def get_date_time(timestamp: int):
    """
    Returns a formatted date and time
    """
    return time.strftime("%Y-%m-%d %H:%M:%S",
                         time.localtime(timestamp))


def get_new_item_id():
    """
    Get the new unique item id
    """
    return str(uuid.uuid4())
