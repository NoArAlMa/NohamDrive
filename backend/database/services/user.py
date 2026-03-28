from fastapi import HTTPException, status
from app.schemas.user import CompleteUser, User
from database.tools.sql_reader import sql_reader
from database.config import SQL_PATH
import psycopg2.errors as errors


# Function creating a user
def create_user(
    connection_manager,
    username: str,
    password: str,
    email: str,
    full_name: str,
    creation_date: str,
) -> User:
    """
    creation date : 'yyyy-mm-dd hh:mm:ss'
    """
    # Requestion a connection from the pool
    conn = connection_manager.request_conn()
    parameters = [username, password, email, full_name, creation_date]

    # Storing the query into a variable
    query = sql_reader(SQL_PATH["create_user"])

    # Executing the query on the database
    try:
        with conn.cursor() as cur:
            cur.execute(query, parameters)
            user = cur.fetchone()
        conn.commit()
    except errors.UniqueViolation as e:
        conn.rollback()
        if "users_username_key" in str(e):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Le nom d'utilisateur '{username}' est déjà utilisé.",
            )
        elif "users_email_key" in str(e):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"L'email '{email}' est déjà utilisé.",
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erreur lors de la création de l'utilisateur.",
            )
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur inattendue : {str(e)}",
        )
    finally:
        connection_manager.drop_conn(conn)

    return User(
        id=user[0],
        username=user[1],
        email=user[2],
        full_name=user[3],
        creation_date=user[4],
    )


# Function removing a user
def delete_user(connection_manager, user_id: int):
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
def update_user(connection_manager, user_id: int, column: str, new_value):
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
def get_user_through_email(connection_manager, email: str) -> CompleteUser | None:
    # Requestion a connection from the pool
    conn = connection_manager.request_conn()
    parameters = [email]

    # Storing the query into a variable
    query = sql_reader(SQL_PATH["get_email_owner"])

    # Executing the query on the database
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(query, parameters)
                data = cur.fetchone()

        # Dropping the conn and returning the data
        if data:
            return CompleteUser(
                id=data[0],
                username=data[1],
                password=data[2],
                email=data[3],
                full_name=data[4],
                creation_date=data[5],
            )
        return None

    finally:
        connection_manager.drop_conn(conn)
