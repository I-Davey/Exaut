
from loguru import logger 
from .HandlerInterface import HandlerInterface
class log(HandlerInterface):
    load = True
    vital = True
    
    def __init__(self):
        None

        
       
    def initialise(self) -> bool:
        #test warning, success, error, debug
        try:
            self.warning("test warning")
            self.error("test error")
            self.debug("test debug")
            self.success("tests successful")
        except:
            return False
        return True
        

    def warning(self,msg):
        logger.warning(msg)
    def success(self,msg):
        logger.success(msg)
    def error(self,msg):
        logger.error(msg)
    def debug(self,msg):
        logger.debug(msg)
    def info(self,msg):
        logger.info(msg)