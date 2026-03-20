from psycopg2 import errors
from psycopg2.pool import ThreadedConnectionPool
from backend.database.config import MIN_CONN, MAX_CONN
from backend.core.config import Settings

class ConnectionManager():
    _pool = None # the pool, global to all instances of the class

    # Initialising the pool if it doesn't already exist
    def __init__(self):
        # Defining the boundaries of the pool
        self.min_conn = MIN_CONN
        self.max_conn = MAX_CONN
        # If the pool does not already exist, try making one
        if ConnectionManager._pool is None:
            try:
                ConnectionManager._pool = ThreadedConnectionPool(
                    minconn=self.min_conn,
                    maxconn=self.max_conn,
                    dsn=Settings.get_db_dsn()
                )
            except errors.ConnectionException as error: # not 100% sure it's the right error
                print(error)
    
    # Function borrowing a connection from the pool (if it exists, which it should) and returning it
    def request_conn(self):
        if ConnectionManager._pool is not None:
            return ConnectionManager._pool.getconn()
        else:
            print("Error : pool does not exist")

    # Function returning a borrowed connection to the pool (if it exists)
    def drop_conn(self, conn) -> None:
        if ConnectionManager._pool is not None:
            ConnectionManager._pool.putconn(conn)
        else:
            print("Error : pool does not exist")