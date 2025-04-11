import logging


def init_logger() -> logging.Logger:
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger("ScrapCompetitor")


logger = init_logger()
