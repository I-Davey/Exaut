
import errno
from loguru import _defaults
from loguru._logger import Core as _Core
from loguru._logger import Logger as _Logger
from .HandlerInterface import HandlerInterface
import atexit as _atexit
import sys as _sys
import sys




class customLogger(_Logger):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
  
logger = customLogger(
    core=_Core(),
    exception=None,
    depth=0,
    record=False,
    lazy=False,
    colors=False,
    raw=False,
    capture=True,
    patcher=None,
    extra={},
)

if _defaults.LOGURU_AUTOINIT and _sys.stderr:
    logger.add(_sys.stderr)

_atexit.register(logger.remove)


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
    def catch(self,msg):
        #cause error with msg
        return logger.catch(msg)
        
        input("Press Enter to continue...")

