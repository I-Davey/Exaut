from .__important.PluginInterface import PluginInterface
import os
import time




class versionhandler(PluginInterface):
    load = True
    #type maps directly to the readsql query results
    types = {"source":3, "ced":4}
    callname = "setversion"
    hooks_handler = ["log"]
    type_types = {"source":{"type":"drag_drop_folder", "description":"please select the Source Folder", "optional":True}, "__Name":"Version Handler"}

    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True



    def main(self,source, cedric, ) -> bool:
        if source != None:
            curdir = os.getcwd()
            if not os.path.exists(source):
                self.logger.error(f"{source} does not exist")
                return False
            os.chdir(source)
        read_file = open("version.py", "r")
        version = read_file.read()
        version = version.split("\n")
        if cedric and bool(cedric) == True:
            version[1] = "auth = True"
        else:
            version[1] = "auth = False"
        read_file.close()

        my_file = open("version.py", "r")
        #print data in the file
        x = my_file.read()
        date = time.strftime("%d %B %Y %H:%M")
        version[0] = f"version = '{date}'"

        version_file = open("version.py", "w")

        #combine version with 
        version = "\n".join(version)
        version_file.write(version)
        version_file.close()
        self.logger.success(f"{date} written to version.py")
        if source != None:
            os.chdir(curdir)




