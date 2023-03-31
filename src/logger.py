"""
Easy universal log setting.

All log levels in separate files in logs level folders,
auto-rotaing. Linux and Windows
 """
# flake8: noqa
import logging
import os
import sys
from logging.handlers import RotatingFileHandler

LOG_DIR = "logs"
LOG_FILE_LIMIT_SIZE_BASE = 10_000


def make_file_handler(
        level: str,
        size: int = LOG_FILE_LIMIT_SIZE_BASE,
        backups_num: int = 5
) -> RotatingFileHandler:
    """Handler init decorator."""
    try:
        os.mkdir(f'{LOG_DIR}/{level}')
    except FileExistsError as ex:
        logging.warning('Logs level subfolder %s '
                        'allready exists, got %s',
                        level, ex)

    file_handler = RotatingFileHandler(f'{LOG_DIR}/{level}/{level}.log',
                                       maxBytes=size, backupCount=backups_num)
    return file_handler


def levels_size_generator():
    """Size ratio."""
    log_size = LOG_FILE_LIMIT_SIZE_BASE
    while 1:
        yield log_size
        log_size = log_size * 3


log_size_gen = levels_size_generator()
FATAL_LOGS_SIZE = next(log_size_gen)
CRITICAL_LOGS_SIZE = next(log_size_gen)
ERROR_LOGS_SIZE = next(log_size_gen)
WARNINGS_LOG_SIZE = next(log_size_gen)
INFO_LOGS_SIZE = next(log_size_gen)
DEBUG_LOGS_SIZE = next(log_size_gen)


def log():
    """Runs log engine with file initialization and connecting handlers."""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    # naming is consistent with logging names convention
    formatterError = logging.Formatter(  # pylint: disable=invalid-name
        '[%(asctime)s] - [%(levelname)s] - [%(name)s(%(filename)s)'
        ' - %(funcName)s%(lineno)d] '
        '- %(message)s\n[%(processName)s:%(process)d] [%(threadName)s:'
        '%(thread)d] - %('
        'pathname)s\n'
    )
    formatter = logging.Formatter('[%(asctime)s] - [%(levelname)s]'
                                  ' -->  %(message)s')

    try:
        os.mkdir(LOG_DIR)
        logging.info('Folder "%s" was created', LOG_DIR)
    except FileExistsError as ex:
        logging.info('Folder "%s" already exists - %s', LOG_DIR, ex)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setLevel(logging.DEBUG)
    stdout_handler.setFormatter(formatter)

    file_handler_debug = make_file_handler('debug', DEBUG_LOGS_SIZE)
    file_handler_debug.setLevel(logging.DEBUG)
    file_handler_debug.setFormatter(formatter)

    file_handler_warning = make_file_handler('warning', WARNINGS_LOG_SIZE)
    file_handler_warning.setLevel(logging.WARNING)
    file_handler_warning.setFormatter(formatterError)

    file_handler_errors = make_file_handler('error', ERROR_LOGS_SIZE)
    file_handler_errors.setLevel(logging.ERROR)
    file_handler_errors.setFormatter(formatterError)

    file_handler_info = make_file_handler('info', INFO_LOGS_SIZE)
    file_handler_info.setLevel(logging.INFO)
    file_handler_info.setFormatter(formatter)

    file_handler_critical = make_file_handler('critical', CRITICAL_LOGS_SIZE)
    file_handler_critical.setLevel(logging.CRITICAL)
    file_handler_critical.setFormatter(formatterError)

    file_handler_fatal = make_file_handler('fatal', FATAL_LOGS_SIZE)
    file_handler_fatal.setLevel(logging.FATAL)
    file_handler_fatal.setFormatter(formatterError)

    logger.addHandler(file_handler_debug)
    logger.addHandler(file_handler_warning)
    logger.addHandler(file_handler_errors)
    logger.addHandler(file_handler_info)
    logger.addHandler(file_handler_critical)
    logger.addHandler(file_handler_fatal)
    logger.addHandler(stdout_handler)
