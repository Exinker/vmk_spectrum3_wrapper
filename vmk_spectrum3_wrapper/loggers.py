import logging

from vmk_spectrum3_wrapper.config import LOGGER_LEVEL


def setdefault_logger():
    logging.basicConfig(
        level=LOGGER_LEVEL,
        datefmt='%Y-%m-%d %H:%M:%S',
        format='[%(asctime)s.%(msecs)04d] %(levelname)-8s %(module)s - %(message)s',
    )
