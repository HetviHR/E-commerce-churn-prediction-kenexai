import psycopg2
import random
import time
import sys

conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="churn_db",
    user="postgres",
    password="postgres"
)

cursor = conn.cursor()

print("Streaming simulation started...", flush=True)

while True:

    customer_id = random.randint(60000, 70000)
    order_count = random.randint(1, 10)
    session_time = random.randint(1, 10)

    query = """
    INSERT INTO raw_customers("CustomerID","OrderCount","HourSpendOnApp")
    VALUES (%s,%s,%s)
    """

    cursor.execute(query, (customer_id, order_count, session_time))
    conn.commit()

    print("Inserted new streaming row", flush=True)

    time.sleep(5)