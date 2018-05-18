"""mess like fun_tools, logger"""
import datetime
import functools
import logging
import logging.handlers

def fun_logger(text='Fun_logger'):
    """log function call and result with custom text head"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            logging.info('%s:Called %s(%r, %r)', text, func.__name__, args, kw)
            result = func(*args, **kw)
            logging.info('%s:%s Returned %r', text, func.__name__, result)
            return result
        return wrapper
    return decorator

def set_logger(log_path):
    """Adapt to Flask, log into log file at `log_path`, at level `INFO`"""
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(asctime)s %(filename)s:%(lineno)d %(message)s')
    file_handler = logging.handlers.TimedRotatingFileHandler(
        log_path, when='midnight', interval=1, backupCount=10, encoding='utf8', atTime=datetime.time(3, 30))
    file_handler.setFormatter(logging.Formatter('[%(levelname)s] %(asctime)s %(filename)s:%(lineno)d %(message)s'))
    logging.getLogger(None).addHandler(file_handler)
    logging.info("Start ....")
