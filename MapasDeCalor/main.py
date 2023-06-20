import psycopg2

host = '127.0.0.1'
port = '5432'
dbname = 'simnarco'
user = 'simnarco'
password = 'simnarco'

# Establish the database connection
conn = psycopg2.connect(host=host, port=port, dbname=dbname, user=user, password=password)

# Create a cursor to interact with the database
cur = conn.cursor()

# Execute a query
cur.execute('SELECT * FROM your_table')

# Fetch all the data from the query result
data = cur.fetchall()

# Close the cursor and database connection
cur.close()
conn.close()
