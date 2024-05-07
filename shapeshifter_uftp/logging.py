import logging
from datetime import datetime

from termcolor import colored

color_map = {
    logging.DEBUG: "cyan",
    logging.INFO: "green",
    logging.WARNING: "yellow",
    logging.ERROR: "red",
    logging.CRITICAL: "magenta",
}


class ShapeshifterLogFormatter(logging.Formatter):
    """
    Formatter for the shapeshifter logs.
    """

    def format(self, record):
        """
        Format log recors using colors.
        """
        color = color_map[record.levelno]
        return (
            colored(f"{record.levelname:10}", color)
            + f"{datetime.now().astimezone().isoformat()} - {record.getMessage()}"
        )


handler = logging.StreamHandler()
handler.setFormatter(ShapeshifterLogFormatter())
handler.setLevel(logging.DEBUG)

logger = logging.getLogger("shapeshifter-uftp")
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)
