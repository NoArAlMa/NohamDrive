from backend.database.tools.sql_reader import sql_reader
from backend.database.config import SQL_PATH
import psycopg2.errors as errors

# Function creating a user
def create_user(connection_manager, username : str, password : str, email : str, full_name : str, creation_date : str):
    """
    creation date : 'yyyy-mm-dd hh:mm:ss'
    """
    # Requestion a connection from the pool
    conn = connection_manager.request_conn()
    parameters = [username, password, email, full_name, creation_date]

    # Storing the query into a variable
    query = sql_reader(SQL_PATH["create_user"])

    # Executing the query on the database
    with conn:
        with conn.cursor() as cur:
            try:
                cur.execute(query, parameters)
            except errors.IntegrityError as error:
                print(error)
    
    # Dropping the conn
    connection_manager.drop_conn(conn)

# Function removing a user
def delete_user(connection_manager, user_id : int):
    # Requestion a connection from the pool
    conn = connection_manager.request_conn()

    # Storing the query into a variable
    query = sql_reader(SQL_PATH["delete_user"])

    # Executing the query on the database
    with conn:
        with conn.cursor() as cur:
            cur.execute(query, [user_id])
            # Checking if any row was affected
            if cur.row_count() == 0:
                print(f"ERROR : there is no such user with {user_id} as id")
    
    # Dropping the conn
    connection_manager.drop_conn(conn)

# Function replacing the field of a user with a new value
def update_user(connection_manager, user_id : int, column : str, new_value):
    # Requestion a connection from the pool
    conn = connection_manager.request_conn()
    parameters = [new_value, user_id]

    # Storing the query into a variable
    query_template = sql_reader(SQL_PATH["update_user"])
    query = query_template.format(column)

    # Executing the query on the database
    with conn:
        with conn.cursor() as cur:
            try:
                cur.execute(query, parameters)
            except errors.IntegrityError as error:
                print(error)
            # Checking if any row was affected
            if cur.rowcount == 0:
                print(f"ERROR : there is no such user with {user_id} as id")
    
    # Dropping the conn
    connection_manager.drop_conn(conn)

# Function returning the id of the owner of the asked email (if taken)
def get_email_owner(connection_manager, email : str) -> int:
    # Requestion a connection from the pool
    conn = connection_manager.request_conn()
    parameters = [email]

    # Storing the query into a variable
    query = sql_reader(SQL_PATH["get_email_owner"])

    # Executing the query on the database
    with conn:
        with conn.cursor() as cur:
            cur.execute(query, parameters)
            data = cur.fetchone()
    
    # Dropping the conn and returning the data
    connection_manager.drop_conn(conn)
    return data[0]