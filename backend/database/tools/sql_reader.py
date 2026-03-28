# Function returning the content of an .sql file
def sql_reader(path: str) -> str:  # path contains the file extension
    with open(path, "r") as file:
        sql = file.read()
    return sql