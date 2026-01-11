# app/core/logging.py
import logging
from rich.logging import RichHandler
from rich.console import Console
from rich.traceback import install


install(show_locals=True)


def setup_logger(name: str = __name__) -> logging.Logger:
    """
    Fonction pour instancier le logger
    """

    console = Console(stderr=True, force_terminal=True)
    rich_handler = RichHandler(
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        console=console,
        markup=True,
        log_time_format="",
    )

    # Configuration du logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()  # Supprime les handlers par défaut
    logger.addHandler(rich_handler)

    # Désactive la propagation pour éviter les doublons
    logger.propagate = False

    return logger


# Exemple d'utilisation :
# from app.core.logging import setup_logger
# logger = setup_logger(__name__)
