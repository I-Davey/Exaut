from .__important.PluginInterface import PluginInterface
import os
from tkinter.simpledialog import askstring


class git_commit_msg(PluginInterface):
    load = True
    types = {"dir":0}
    type_types = {"folderpath":["drag_drop_folder", "please select folder"], "__Name":"Git Commit"}
    callname = "gitcmt"
    hooks_handler = ["log"]

    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True

    def main(self, dir) -> bool: 
        #check if dir exists
        if not os.path.exists(dir):
            self.logger.error(f"{dir} does not exist")
            return False
        summary = askstring("Git Commit", "Please enter a summary for your commit")
        if summary is None:
            self.logger.warning("no summary given, cancelling commit")
            return False
        command = f"git commit -am \"{summary}\""
        curdir = os.getcwd()
        os.chdir(dir)
        os.system(command)
        os.chdir(curdir)
        self.logger.success(f"{command} executed in {dir}")
        return True