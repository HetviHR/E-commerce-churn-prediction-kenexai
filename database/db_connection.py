import psycopg2

def get_connection():

    conn = psycopg2.connect(
        host="localhost",
        database="churn_db",
        user="postgres",
        password="postgres",
        port="5433"
    )   

    return conn