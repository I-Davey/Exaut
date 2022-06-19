from .__important.PluginInterface import PluginInterface
import os
import ctypes
import shutil
class Run_Command(PluginInterface):
    load = True
    types = {"dir":0,"command":3}
    type_types = {"folderpath":["drag_drop_folder", "please select folder"], "source":["text", "Please Enter Command"], "__Name":"Run Command"}

    callname = "wincmd"
    hooks_handler = ["log"]

    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True

    def main(self, dir, command, Popups) -> bool: 
        #check if dir exists
        if not os.path.exists(dir):
            self.logger.error(f"{dir} does not exist")
            return False

        curdir = os.getcwd()
        os.chdir(dir)
        os.system(command)
        os.chdir(curdir)
        self.logger.success(f"{command} executed in {dir}")
        return True