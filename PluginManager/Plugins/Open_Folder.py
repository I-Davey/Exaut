from .__important.PluginInterface import PluginInterface
import os
import ctypes
import shutil
import win32api
import subprocess
class Open_Folder(PluginInterface):
    load = True
    #type maps directly to the readsql query results
    types = {"path":0,} 
    type_types = {"folderpath":["drag_drop_folder", "please select folder"], "__Name":"Open Folder"}
    callname = "folder"
    hooks_handler = ["log"]

    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True



    def main(self,folder) -> bool:
        #check if the given folder exists, and if so, open it, else, logger.error(f"folder {folder} does not exist")
        folder = folder 
        if os.path.exists(folder):
            #if folder starts with two forwardslashes
            if folder[0:2] in("//","\\\\"):
                self.logger.debug("network drive detected")
                folder = folder.replace("/","\\")
                os.system("explorer " + folder)
                
            else:
                current_dir = os.getcwd()
                os.chdir(folder)
                os.system(f"start .")
                os.chdir(current_dir)
               
            self.logger.success(f"opened folder {folder}")
            return True
        else:
            self.logger.error(f"folder {folder} does not exist")
            return False
        