from backend.database.tools.sql_reader import sql_reader
from backend.database.config import SQL_PATH

# Function creating the user table 
def create_users_table(connection_manager):
    # Requestion a connection from the pool
    conn = connection_manager.request_conn()

    # Storing the query into a variable
    query = sql_reader(SQL_PATH["create_users_table"])

    # Executing the query on the database
    with conn:
        with conn.cursor() as cur:
            cur.execute(query)
    
    # Dropping the conn
    connection_manager.drop_conn(conn)

# Function removing the user table
def drop_users_table(connection_manager):
    # Requestion a connection from the pool
    conn = connection_manager.request_conn()

    # Storing the query into a variable
    query = sql_reader(SQL_PATH["drop_users_table"])

    # Executing the query on the database
    with conn:
        with conn.cursor() as cur:
            cur.execute(query)
    
    # Dropping the conn
    connection_manager.drop_conn(conn)

# Function creating the token table
def create_tokens_table(connection_manager):
    # Requestion a connection from the pool
    conn = connection_manager.request_conn()

    # Storing the query into a variable
    query = sql_reader(SQL_PATH["create_tokens_table"])

    # Executing the query on the database
    with conn:
        with conn.cursor() as cur:
            cur.execute(query)
    
    # Dropping the conn
    connection_manager.drop_conn(conn)

# Function removing the token table
def drop_tokens_table(connection_manager):
    # Requestion a connection from the pool
    conn = connection_manager.request_conn()

    # Storing the query into a variable
    query = sql_reader(SQL_PATH["drop_tokens_table"])

    # Executing the query on the database
    with conn:
        with conn.cursor() as cur:
            cur.execute(query)
    
    # Dropping the conn
    connection_manager.drop_conn(conn)