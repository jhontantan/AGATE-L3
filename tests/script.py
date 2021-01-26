DB_HOST = "localhost"
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASS = "user"

# Exemples d'utilisation de psycopg2 (n'utilise pas flask)

# Connection Python
import psycopg2
import psycopg2.extras

conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# cur.execute("CREATE TABLE student (id SERIAL PRIMARY KEY, name VARCHAR);")
cur.execute("INSERT INTO student(name) VALUES(%s)", ("Elodie",))

cur.execute("SELECT * FROM student;")
print(cur.fetchall())
# print(cur.fetchone()['name'])
conn.commit()

cur.close()

conn.close()