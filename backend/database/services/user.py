from fastapi import HTTPException, status
from app.schemas.user import CompleteUser, User
from database.tools.sql_reader import sql_reader
from database.config import SQL_PATH
import psycopg2.errors as errors
from psycopg2 import sql


CREATE_USER_QUERY = sql_reader(SQL_PATH["create_user"])
DELETE_USER_QUERY = sql_reader(SQL_PATH["delete_user"])
UPDATE_USER_QUERY_TEMPLATE = sql_reader(SQL_PATH["update_user"])
GET_EMAIL_OWNER_QUERY = sql_reader(SQL_PATH["get_email_owner"])

UPDATABLE_USER_COLUMNS = frozenset({"username", "password", "email", "full_name"})


def _build_user(data) -> User:
    return User(
        id=data[0],
        username=data[1],
        email=data[2],
        full_name=data[3],
        creation_date=data[4],
    )


def _build_complete_user(data) -> CompleteUser:
    return CompleteUser(
        id=data[0],
        username=data[1],
        password=data[2],
        email=data[3],
        full_name=data[4],
        creation_date=data[5],
    )


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

    # Executing the query on the database
    try:
        with conn.cursor() as cur:
            cur.execute(CREATE_USER_QUERY, parameters)
            user = cur.fetchone()
        conn.commit()
    except errors.UniqueViolation as e:
        conn.rollback()
        constraint_name = e.diag.constraint_name
        if constraint_name == "users_username_key":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Le nom d'utilisateur '{username}' est déjà utilisé.",
            )
        if constraint_name == "users_email_key":
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

    return _build_user(user)


# Function removing a user
def delete_user(connection_manager, user_id: int):
    # Requestion a connection from the pool
    conn = connection_manager.request_conn()

    # Executing the query on the database
    try:
        with conn.cursor() as cur:
            cur.execute(DELETE_USER_QUERY, [user_id])
            if cur.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Aucun utilisateur avec l'id {user_id}.",
                )
        conn.commit()
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur inattendue : {str(e)}",
        )
    finally:
        connection_manager.drop_conn(conn)


# Function replacing the field of a user with a new value
def update_user(connection_manager, user_id: int, column: str, new_value):
    if column not in UPDATABLE_USER_COLUMNS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Colonne utilisateur invalide : {column}",
        )

    # Requestion a connection from the pool
    conn = connection_manager.request_conn()
    parameters = [new_value, user_id]

    query = sql.SQL(UPDATE_USER_QUERY_TEMPLATE).format(sql.Identifier(column))

    # Executing the query on the database
    try:
        with conn.cursor() as cur:
            cur.execute(query, parameters)
            if cur.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Aucun utilisateur avec l'id {user_id}.",
                )
        conn.commit()
    except errors.IntegrityError as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Impossible de mettre à jour l'utilisateur : {str(e)}",
        )
    except HTTPException:
        conn.rollback()
        raise
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erreur inattendue : {str(e)}",
        )
    finally:
        connection_manager.drop_conn(conn)


# Function returning the id of the owner of the asked email (if taken)
def get_user_through_email(connection_manager, email: str) -> CompleteUser | None:
    # Requestion a connection from the pool
    conn = connection_manager.request_conn()
    parameters = [email]

    # Executing the query on the database
    try:
        with conn.cursor() as cur:
            cur.execute(GET_EMAIL_OWNER_QUERY, parameters)
            data = cur.fetchone()
        conn.commit()

        # Dropping the conn and returning the data
        if data:
            return _build_complete_user(data)
        return None

    except Exception:
        conn.rollback()
        raise
    finally:
        connection_manager.drop_conn(conn)
