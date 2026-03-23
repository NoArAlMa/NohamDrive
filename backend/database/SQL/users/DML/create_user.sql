INSERT INTO users (username, password, email, full_name, creation_date)
VALUES (%s, %s, %s, %s, %s)
RETURNING username, email, full_name, creation_date;