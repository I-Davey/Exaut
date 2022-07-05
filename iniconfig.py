import configparser
import os

class Parse():
    
    def __init__(self, logger, selected = None):
        self.selected = selected
        self.logger = logger
        self.cfg = None
        self.success = False
    

        @self.logger.catch
        def load(parent_, selected = None):
            parent_.config = configparser.ConfigParser()
            configlocation = os.path.join(os.getcwd() + '\config.ini')
            parent_.logger.debug("config file location : " + configlocation)

            #print(configlocation)
            parent_.config.read(configlocation)
            parent_.cfg = {}
            for item in parent_.config.sections():
                parent_.cfg[item] = {}
                for key, value in parent_.config.items(item):
                    parent_.cfg[item][key] = value
            if selected:
                if selected in parent_.cfg:
                    parent_.cfg = parent_.cfg[selected]
                else:
                    parent_.cfg = None
            self.success = True
        
        load(self, self.selected)
        if not self.success:
            self.logger.error("Config Parser Failed")
            input("Press Enter to continue...")
            exit()


        
               
