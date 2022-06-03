import configparser
import os
from loguru import logger

@logger.catch
class Parse():
    def __init__(self, selected = None):
        self.config = configparser.ConfigParser()
        configlocation = os.path.join(os.getcwd() + '\config.ini')
        logger.debug("config file location : " + configlocation)

        #print(configlocation)
        self.config.read(configlocation)
        self.cfg = {}
        for item in self.config.sections():
            self.cfg[item] = {}
            for key, value in self.config.items(item):
               self.cfg[item][key] = value
        if item:
            self.cfg = self.cfg[selected]

        
               
