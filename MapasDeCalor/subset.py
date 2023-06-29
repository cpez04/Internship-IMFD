from sqlalchemy import create_engine, text, MetaData
from sshtunnel import SSHTunnelForwarder
import csv 
import random

# SSH Parameters
SERVER = "s02.imfd.cl"
SSH_PORT = 201
SSH_USER = "simnarco"
SSH_KEY = "pkchris.pem"

# Database Parameters
DB_PORT = 5432
DB_NAME = "simnarco"
PG_USER = "simnarco"
PG_PASS = "simnarco"
DB_TABLE = "delitos"

# Connect to PostgreSQL DB
def connect_sqlalc():
    try:
        print('Connecting to the PostgreSQL Database...')
    
        server = SSHTunnelForwarder(
            (SERVER, 201),
            ssh_username=SSH_USER,
            remote_bind_address=('127.0.0.1', 5432)
            )
        server.start()
        local_port = str(server.local_bind_port)
        engine = create_engine(
            'postgresql://{}:{}@{}:{}/{}'.format(PG_USER, PG_PASS, "127.0.0.1", 
                                                 local_port, DB_NAME),
            pool_pre_ping=True,
            connect_args={
                "keepalives": 1,
                "keepalives_idle": 30,
                "keepalives_interval": 10,
                "keepalives_count": 5,
            })
        print('Connection Has Been Established...')	
    except Exception as e:
        print("Error while connecting to PostgreSQL", e)
        raise e
    return engine

def check_table(conn):
    # check if table exists, returns True or False
    query = ("SELECT EXISTS ("
            "SELECT 1 "
            "FROM information_schema.tables "
            "WHERE table_name = '{}');").format(DB_TABLE)
    return conn.execute(text(query)).fetchone()[0]


def generate_csv_by_crime(crime, filename):
    print("Generating CSV file...")
    # Open the file for writing the CSV data
    with open(filename, 'w', newline='') as file:
        # Headers/Columns of info you want
        headers = ["y", "x", "fecha", "hora", "comuna", "delito"]
        writer = csv.writer(file)

        writer.writerow(headers)

        # Calculate the number of rows per iteration
        rows_per_iteration = 500

        # Initialize the offset and rows_added variables
        offset = 0
        rows_added = 0

        # Start the loop to generate the CSV data
        while True:
            # Execute the query to fetch rows where delito = "Homicidio"
            query = f"SELECT {', '.join(headers)} FROM {DB_TABLE} WHERE delito = '{crime}' LIMIT {rows_per_iteration} OFFSET {offset};"
            result_proxy = conn.execute(text(query))
            rows = result_proxy.fetchall()

            # If no rows are fetched, break out of the loop
            if not rows:
                break

            # Write the rows to the CSV file
            writer.writerows(rows)

            # Increment the offset and update the rows_added counter
            offset += rows_per_iteration
            rows_added += len(rows)

        print("CSV file generated successfully.")

if __name__ == "__main__":
    # Database connection setup
    engine = connect_sqlalc()
    with engine.begin() as conn:
        # Check if the table exists
        if check_table(conn):
            generate_csv_by_crime("Homicidio", "homicidios3.csv")
        else:
            print("The table does not exist.")

