import psycopg2

HOSTNAME = "localhost"
DB_NAME = "ptcgb"
USERNAME = "postgres"
PASSWORD = "postgres"
PORT_ID = 5432

try:
    connection = psycopg2.connect(host=HOSTNAME, dbname=DB_NAME, user=USERNAME, password=PASSWORD, port=PORT_ID)
    connection.close()
except Exception as e:
    print(e)
