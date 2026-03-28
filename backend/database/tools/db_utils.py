from psycopg2 import OperationalError
from core.logging import setup_logger

logger = setup_logger(__name__)


def test_db_connection(connection_manager):
    try:
        conn = connection_manager.request_conn()
        if conn:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1;")
            connection_manager.drop_conn(conn)
            logger.info("Connexion à la base de données réussie.")
            return True
    except OperationalError as e:
        logger.error(f"Impossible de se connecter à la base de données: {e}")
        return False
    except Exception as e:
        logger.error(f"Erreur inattendue lors du test de la base de données: {e}")
        return False
