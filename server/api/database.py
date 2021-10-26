from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

dbc = { "username": "u311585670_ma3stro", "password": "06151525Alex8969", "hostname": "109.106.246.101", "database": "u311585670_master" }

Engine = create_engine("mysql://" + 
	dbc['username'] + ":" + dbc['password'] + "@" + 
	dbc['hostname'] + "/" + dbc['database'] , pool_pre_ping=True)

SessionLocal = sessionmaker(bind=Engine, autocommit=False, autoflush=False,)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()