from .__important.PluginInterface import PluginInterface
import os
import time




class versionhandler(PluginInterface):
    load = True
    #type maps directly to the readsql query results
    types = {"source":3}
    callname = "setversion"
    hooks_handler = ["log"]
    type_types = {"source":{"type":"drag_drop_folder", "description":"please select the Source Folder", "optional":True}}

    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True



    def main(self,Popups,source = None) -> bool:
        if source != None:
            curdir = os.getcwd()
            if not os.path.exists(source):
                self.logger.error(f"{source} does not exist")
                return False
            os.chdir(source)
        my_file = open("version.py", "w")
        date = time.strftime("%d %B %Y %H:%M")
        my_file.write(f"version = '{str(date)}'")
        my_file.close()
        self.logger.success(f"{date} written to version.py")
        if source != None:
            os.chdir(curdir)




