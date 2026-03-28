from database.tools.sql_reader import sql_reader
from database.config import SQL_PATH
import psycopg2.errors as errors

# Function creating a token
def create_token(connection_manager, user_id : int, token : str, creation_date : str, expiration_date : str, scope : str):
    """
    creation_date / expiration_date : 'yyyy-mm-dd hh:mm:ss'
    """
    # Requestion a connection from the pool
    conn = connection_manager.request_conn()
    parameters = [user_id, token, creation_date, expiration_date, scope]

    # Storing the query into a variable
    query = sql_reader(SQL_PATH["create_token"])

    # Executing the query on the database
    with conn:
        with conn.cursor() as cur:
            try:
                cur.execute(query, parameters)
            except errors.IntegrityError as error:
                print(error)
    
    # Dropping the conn
    connection_manager.drop_conn(conn)

# Function removing every expired token
def hoover_tokens(connection_manager):
    # Requestion a connection from the pool
    conn = connection_manager.request_conn()

    # Storing the query into a variable
    query = sql_reader(SQL_PATH["hoover_tokens"])

    # Executing the query on the database
    with conn:
        with conn.cursor() as cur:
            cur.execute(query)
            print(f"DEBUGGING : {cur.rowcount} lines were affected by the hoover")
    
    # Dropping the conn
    connection_manager.drop_conn(conn)

# Function returning all the info of a specific token
def get_token_owner_info(connection_manager, token : str) -> tuple:
    # Requestion a connection from the pool
    conn = connection_manager.request_conn()

    # Storing the query into a variable
    query = sql_reader(SQL_PATH["get_token_owner_info"])

    # Executing the query on the database
    with conn:
        with conn.cursor() as cur:
            cur.execute(query, [token])
            data = cur.fetchone()
    
    # Dropping the conn and returning the data
    connection_manager.drop_conn(conn)
    return data