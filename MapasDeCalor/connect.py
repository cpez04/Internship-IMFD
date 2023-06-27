from sqlalchemy import create_engine, text, MetaData
from sshtunnel import SSHTunnelForwarder
from flask import Flask, render_template, request

app = Flask(__name__)

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

def get_headers():
    # Fetch the table metadata
    metadata = MetaData()
    metadata.reflect(bind=engine)
    table = metadata.tables[DB_TABLE]
    columns = table.columns

    # Print the column headers
    headers = [column.name for column in columns]
    print("Column Headers:")
    print(", ".join(headers))
        
def db_size():
    query = "SELECT pg_size_pretty(pg_database_size('{}'));".format(DB_NAME)
    result = conn.execute(text(query)).fetchone()

    if result:
        size = result[0]
        print("Size of the database '{}': {}".format(DB_NAME, size))
    else:
        print("Failed to retrieve the size of the database.")

@app.route('/')
def view_data():
    # Database connection setup
    engine = connect_sqlalc()
    with engine.begin() as conn:
        # Pagination parameters
        page_size = 30  # Number of rows per page
        current_page = request.args.get('page', default=1, type=int)  # Get current page from query parameters

        # Retrieve data for the current page
        query = f"SELECT * FROM {DB_TABLE} LIMIT {page_size} OFFSET {(current_page - 1) * page_size};"
        result = conn.execute(text(query)).fetchall()

        # Render the template with the data
        return render_template('data.html', data=result, current_page=current_page)

if __name__ == "__main__":
    engine = connect_sqlalc()
    with engine.begin() as conn:
        # Check if the table exists
        if check_table(conn):
            get_headers()
            db_size()
        else:
            print("The table does not exist.")
        
    app.run(debug=True)


