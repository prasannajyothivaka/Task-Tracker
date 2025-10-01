"""class and function logging"""
import functools
from loguru import logger


def logger_wraps(*, entry=True, exit=True, level="DEBUG"):
    """
    logger to track events
    """

    def wrapper(func):
        name = func.__name__

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            logger_ = logger.opt(depth=1)
            if entry:
                logger_.log(level, "Entering '{}'", name)
            result = func(*args, **kwargs)
            if exit:
                logger_.log(level, "Exiting '{}' ", name)
            return result

        return wrapped

    return wrapper
