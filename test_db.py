from database.db_connection import get_connection

conn = get_connection()
print("Database connected successfully!")

conn.close()