import logging
import sys


def set_logger():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(message)s'))
    logging.root.setLevel(logging.INFO)
    if not logging.root.handlers:
        logging.root.addHandler(console_handler)
