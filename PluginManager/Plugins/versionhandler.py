from .__important.PluginInterface import PluginInterface

import os
import time




class versionhandler(PluginInterface):
    load = True
    #type maps directly to the readsql query results
    types = {"ftype":2}
    callname = "setversion"
    hooks_handler = ["log"]

    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True



    def main(self,ftype) -> bool:
        if ftype == "setversion":
            #get file names in ../../Components/versionhandler/
            my_file = open("version.py", "w")
            #get date in this format: 18 march 2022 20:10
            date = time.strftime("%d %B %Y %H:%M")
            my_file.write(f"version = '{str(date)}'")
            my_file.close()



