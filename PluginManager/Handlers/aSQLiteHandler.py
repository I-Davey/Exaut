from iniconfig import Parse
import os
import apsw
from loguru import logger #logger needs its' own method
from .HandlerInterface import HandlerInterface
class SQLiteHandler(HandlerInterface):
    logger.debug("initilising SQLiteHandler")
    vital = True
    def __init__(self):
        
        db_cfg = Parse("SQLCONN").cfg
        connectionpath = db_cfg["connectionpath"] if db_cfg["connectionpath"] else os.getcwd()
        connection_db ="\\" + db_cfg["connection"]
        self.__db_conn = connectionpath + connection_db
        self.connection = None
        self.cursor = None
        logger.debug(f"SQLiteHandler initialised with {self.__db_conn}")
        logger.debug(f"vars: {vars(self)}")
       
    def initialise(self) -> bool:
        #if path not exist
        if not os.path.exists(self.__db_conn):
            return f"DB File {self.__db_conn} not found"
        try:
            self.connection = apsw.Connection(self.__db_conn)
            self.cursor = self.connection.cursor()
            return True
            
        except Exception as e:
            return e


       
