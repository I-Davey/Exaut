from ast import For
import string
from sqlalchemy import Column, Integer, String, ForeignKey

from sqlalchemy.orm import declarative_base
Base = declarative_base()



start = dir()

class completed_jobs(Base):
    __tablename__ = 'completed_jobs'
    assetvision = Column(String(63), primary_key=True)
    w3w = Column(String(63))
    location = Column(String(63))
    sqm_painted = Column(Integer)
    sqm_cleaned = Column(Integer)
    date = Column(String(63))

class inspections(Base):
    __tablename__ = 'inspections'
    w3w = Column(String(63), primary_key=True)
    location = Column(String(63))
    notes = Column(String(63))
    tm = Column(String(63))
    date = Column(String(63), primary_key=True)

class inspection_routes(Base):
    __tablename__ = 'inspection_routes'
    inspection_route = Column(String(63), primary_key=True)
    start = Column(String(63), primary_key=True)
    end = Column(String(63))
    notes = Column(String(63))
    date = Column(String(63), primary_key=True)

class schedule(Base):
    __tablename__ = 'schedule'
    w3w = Column(String(63), primary_key=True)
    location = Column(String(63))
    notes = Column(String(63))
    date = Column(String(63), primary_key=True)

class comments(Base):
    __tablename__ = 'comments'
    comments = Column(String(63), primary_key=True)    
    date = Column(String(63), primary_key=True)



end = dir()
tables = [x for x in end if x not in start and x != "start"]
