from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Replace with your database username, password, hostname and db_name
dbc = { "username": "", "password": "", "hostname": "", "database": "" }

# Creates a database engine
Engine = create_engine("mysql://" + 
	dbc['username'] + ":" + dbc['password'] + "@" + 
	dbc['hostname'] + "/" + dbc['database'] , pool_pre_ping=True)

# Creates a session
SessionLocal = sessionmaker(bind=Engine, autocommit=False, autoflush=False,)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
