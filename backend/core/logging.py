# app/core/logging.py
import logging
from rich.logging import RichHandler
from rich.console import Console
from rich.traceback import install

# Active les traces Rich pour toutes les exceptions
install(show_locals=True)


def setup_logger(name: str = __name__) -> logging.Logger:
    """Configure un logger moderne et coloré pour ton app."""
    # Console Rich pour un rendu optimal
    console = Console(stderr=True, force_terminal=True)
    rich_handler = RichHandler(
        rich_tracebacks=True,
        tracebacks_show_locals=True,
        console=console,
        markup=True,
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
# logger.info("[bold green]MinIO est disponible[/bold green]")
