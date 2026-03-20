SELECT users.id, users.username, users.password, users.email, users.full_name, users.creation_date
FROM tokens
INNER JOIN users
ON tokens.user_id = users.id 
WHERE tokens.token = %s; 