DELETE FROM tokens
WHERE expiration_date - CURRENT_DATE < INTERVAL '0 months 0 days 0 hours 0 minutes';