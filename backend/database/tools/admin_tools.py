from psycopg2 import errors
from backend.database.tools.sql_reader import sql_reader
from backend.database.config import SQL_PATH

# Class for database administration / testing / debugging
class AdminTools():
    def __init__(self, connection_manager):
        self.connection_manager = connection_manager

    def query_executor(self):
        # First borrowing a connection from the pool
        conn = self.connection_manager.request_conn()

        # SQL execution menu
        print("You may enter a query you wish to execute on the database (!Q to stop)")
        query = input("> ")
        while query != "!Q":
            with conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    try:
                        print(f"output : {cur.fetchall()}")
                    except errors.ProgrammingError: # it crashes when there's fuck all to fetch (I hope whoever made it this way dies)
                        pass
            query = input("> ")
        
        # Dropping the conn
        self.connection_manager.drop_conn(conn)

    # function returning all the public tables
    def get_table_list(self) -> list:
        # First borrowing a connection from the pool
        conn = self.connection_manager.request_conn()
        
        # Getting the SQL code to execute
        query = sql_reader(SQL_PATH["get_table_list"])

        # Executing the query on the database
        with conn:
            with conn.cursor() as cur:
                cur.execute(query)
                data = cur.fetchall()
            
        # Dropping the conn and returning the data
        self.connection_manager.drop_conn(conn)
        return data
    
    # function returning all the columns of a specified table
    def get_columns(self, table : str):
        # First borrowing a connection from the pool
        conn = self.connection_manager.request_conn()

        # Getting the SQL code to execute
        query = sql_reader(SQL_PATH["get_column_list"]).format('test')

        # Executing the query on the database
        with conn:
            with conn.cursor() as cur:
                cur.execute(query)
                data = cur.fetchall()
        
        # Dropping the conn and returning the data
        self.connection_manager.drop_conn(conn)
        return data