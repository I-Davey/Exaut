from asyncio import futures
from backend.db.Exaut_sql import *
from backend.iniconfig import Parse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .HandlerInterface import HandlerInterface
from .log import log
class Sqlite(HandlerInterface):

    load = True
    vital = False


    def __init__(self):
        self.logger = log()
        db_config = Parse( self.logger,"SQLCONN").cfg
        connectionpath = db_config["connectionpath"]
        connection = db_config["connection"]
        self.db_loc = f"{connectionpath}\\{connection}"





    def initialise(self) -> bool:
        self.session = sessionmaker(bind=create_engine(f'sqlite:///{self.db_loc}'), future=True)
        self.tables = []

        for item in tables:
            self.tables.append(eval(f"{item}"))
        return True



"""from backend.db.Exaut_sql import *
from backend.iniconfig import Parse

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .HandlerInterface import HandlerInterface
from .log import log
class Sqlite(HandlerInterface):

    load = True
    vital = False


    def __init__(self):
        self.logger = log()
        db_config = Parse( self.logger,"SQLCONN").cfg
        connectionpath = db_config["connectionpath"]
        connection = db_config["connection"]
        self.db_loc = f"{connectionpath}\\{connection}"





    def initialise(self) -> bool:
        self.engine_data = sessionmaker, create_engine, f'sqlite:///{self.db_loc}'
        self.tables = []

        for item in tables:
            self.tables.append(eval(f"{item}"))
        return True

"""


