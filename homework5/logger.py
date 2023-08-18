import logging


def setup_logger():
    """
    Set up a logger configuration and return a logger instance.
    The logger is configured to write log messages to a file named 'my_log_file.log'. The log level is set to DEBUG,
    which includes all log messages. The log messages are formatted with the timestamp, log level, and the actual
    message content.
    Returns:
        logging.Logger: A logger instance that can be used to write log messages.
    """
    logging.basicConfig(
        filename='my_log_file.log',
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s"'
    )
    return logging.getLogger('my_logger')
