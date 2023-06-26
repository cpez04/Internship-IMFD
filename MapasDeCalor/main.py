from sqlalchemy import create_engine, text
from sshtunnel import SSHTunnelForwarder

# ssh -J gate@s02.imfd.cl simnarco@vm01

# servidor   : s02.imfd.cl
# puerto ssh : 201
# usuario    : simnarco

# https://stackoverflow.com/questions/31506958/sqlalchemy-through-paramiko-ssh

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
            'postgresql://{}:{}@{}:{}/{}'.format(PG_USER, PG_PASS, "127.0.0.1", local_port, DB_NAME),
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
    query = "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '{}');".format(DB_TABLE)
    return conn.execute(text(query)).fetchone()[0]

if __name__ == "__main__":
    # Example connection
    engine = connect_sqlalc()
    with engine.begin() as conn:
        # Do stuff with conn
        check_table(conn)
        pass



