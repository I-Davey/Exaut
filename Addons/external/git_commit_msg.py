from __important.PluginInterface import PluginInterface
import os


class git_commit_msg(PluginInterface):
    load = True
    types = {"dir":0}
    type_types = {"folderpath":["drag_drop_folder", "please select folder"], "__Name":"Git Commit"}
    callname = "gitcmt"
    hooks_handler = ["log"]

    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True

    def main(self, dir, Popups) -> bool: 
        #check if dir exists
        if not os.path.exists(dir):
            self.logger.error(f"{dir} does not exist")
            return False
        summary = Popups.data_entry("Please enter a summary for your commit", "Git Commit")
        if summary is None:
            self.logger.warning("no summary given, cancelling commit")
            return False
        command_0 = f"git add --all"

        command = f"git commit -am \"{summary}\""
        curdir = os.getcwd()
        os.chdir(dir)
        os.system(command_0)
        self.logger.success(f"{command_0} executed in {dir}")
        os.system(command)
        self.logger.success(f"{command} executed in {dir}")
        os.chdir(curdir)

        return True