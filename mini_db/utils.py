import time
import logging


def timer(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()

        logging.debug(f"Time: {end - start:.4f}s")
        return result
    return wrapper