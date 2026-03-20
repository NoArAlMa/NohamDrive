# POOL
MIN_CONN = 1
MAX_CONN = 3

# PATH
SQL_PATH = {
    "get_table_list" : "./backend/database/SQL/administration/get_table_list.sql",
    "get_column_list" : "./backend/database/SQL/administration/get_column_list.sql",
    "create_tokens_table" : "./backend/database/SQL/tokens/DDL/create_tokens_table.sql",
    "drop_tokens_table" : "./backend/database/SQL/tokens/DDL/drop_tokens_table.sql",
    "create_token" : "./backend/database/SQL/tokens/DML/create_token.sql",
    "hoover_tokens" : "./backend/database/SQL/tokens/DML/hoover_tokens.sql",
    "get_token_owner_info" : "./backend/database/SQL/tokens/DQL/get_token_owner_info.sql",
    "create_users_table" : "./backend/database/SQL/users/DDL/create_users_table.sql",
    "drop_users_table" : "./backend/database/SQL/users/DDL/drop_users_table.sql",
    "create_user" : "./backend/database/SQL/users/DML/create_user.sql",
    "delete_user" : "./backend/database/SQL/users/DML/delete_user.sql",
    "update_user" : "./backend/database/SQL/users/DML/update_user.sql",
    "get_email_owner" : "./backend/database/SQL/users/DQL/get_email_owner.sql"
}