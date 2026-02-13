from core.config import settings
from psycopg2.pool import ThreadedConnectionPool

# Function initialising a pool of connections
def init_pool(min_conn:int = 1, max_conn: int = 5) -> None:
    global _pool
    if _pool is None:
        _pool = ThreadedConnectionPool(
            minconn=min_conn,
            maxconn=max_conn,
            dsn=settings.DB_DSN)

# Function borrowing a connection from the pool (if it exists) and returning it
def request_conn():
    if _pool is not None:
        return _pool.getconn()

# Function returning a borrowed connection to the pool (if it exists)
def drop_conn(conn) -> None:
    if _pool is not None:
        _pool.putconn()