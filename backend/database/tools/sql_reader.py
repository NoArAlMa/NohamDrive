from pathlib import Path


_BACKEND_ROOT = Path(__file__).resolve().parents[2]


def sql_reader(path: str) -> str:
    """
    Return the content of an .sql file.

    `path` is typically a repo-relative path like "database/SQL/.../file.sql".
    We resolve it relative to the backend root so imports work no matter the CWD.
    """
    sql_path = Path(path)
    if not sql_path.is_absolute():
        sql_path = _BACKEND_ROOT / sql_path

    with sql_path.open("r", encoding="utf-8") as file:
        return file.read()

