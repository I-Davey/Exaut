from .MethodInterface import MethodInterface
from loguru import logger
import apsw, time
import ctypes

class ReadSQL(MethodInterface):
    load = False
    hooks = ["SQLiteHandler"]

    def __init__(self):
        self.connection = None

        self.cursor = None
        self.types = {"query":str,"attempts":int,"sec":float,"msg":bool}

    def load_self(self, hooks):
        self.connection = hooks["SQLiteHandler"].connection
        
        self.cursor = self.connection.cursor()
        return True

    def main(self, query,attempts=12,sec=0.2,msg=False):
        val = []####
        try:
            results = self.cursor.execute(query)
            for result in results:
                val.append(list(result))
            return(val)
        except apsw.SQLError as e:
            err = str(e)
            for i in range(0,attempts):
                try:
                    results = self.cursor.execute(query)
                    for result in results:
                        val.append(list(result))
                    return(val)
                except apsw.SQLError as e:
                    if err.find("database is locked")>=0:
                        time.sleep(sec)
                        i -= 1
                    if i==attempts-1:
                        logger.debug(query)
                        logger.error(str(e))
                        if msg==True:
                            ctypes.windll.user32.MessageBoxW(0,str(e),"SQL Query Error",1)
                        return(val)
                    else:
                        time.sleep(sec)
                        continue
        except apsw.ConstraintError as e2:
            err = str(e2)
            for i in range(0,attempts):
                try:
                    results = self.cursor.execute(query)
                    for result in results:
                        val.append(list(result))
                    return(val)
                except apsw.ConstraintError as e2:
                    if i==attempts-1:
                        logger.debug(query)
                        logger.error(str(e2))
                        if msg==True:
                            ctypes.windll.user32.MessageBoxW(0,str(e2),"SQL Query Error",1)
                        return(val)
                    else:
                        time.sleep(sec)
                        continue
        except apsw.BusyError as e3:
            err = str(e3)
            while err.find("database is locked")>=0:
                time.sleep(sec)

