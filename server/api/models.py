from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from api.database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, unique=True)
    user_passcode = Column(String)

class Conf(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    basic_greeting = Column(String)
    basic_creativity = Column(Integer)
    basic_language = Column(Integer)
    #widget_name = Column(String)
    #widget_theme = Column(Integer)
    #widget_layout = Column(Integer)
    #widget_logo = Column(String)
    #widget_whitelist = Column(String)
    #widget_kb = Column(String)

class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)
    private_key = Column(String, unique=True)
    public_key = Column(String, unique=True)
    
class QGroup(Base):
    __tablename__ = "query_groups"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)
    query_group = Column(Integer, index=True)
    time = Column(DateTime)

class Query(Base):
    __tablename__ = "queries"

    query_id = Column(Integer, primary_key=True, index=True)
    query_group = Column(Integer, index=True)

    request = Column(String)
    response = Column(String)

    in_memory = Column(Integer)
    time = Column(DateTime)

    user_id = Column(Integer, unique=True, index=True)
    

class KBase(Base):
    __tablename__ = "knowledge_bases"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)
    body = Column(String)
    name = Column(String)
