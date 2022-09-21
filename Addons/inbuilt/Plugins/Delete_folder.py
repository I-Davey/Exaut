from .__important.PluginInterface import PluginInterface
import os
import shutil

class Delete_folder(PluginInterface):
    load = True
    types = {"folder":0}

    type_types = {"folderpath":["drag_drop_folder", "Select Folder"], "__Name":"Delete Folder"}
    callname = "delfldr"
    hooks_handler = ["log"]

    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True

    def main(self,folder, ) -> bool:
        
        if folder[-1] != "/":
            folder += "/"
        if os.path.exists(folder)==False:
            self.logger.error("folder path does not exist: "+folder)
            return False
        
        if os.path.isdir(folder)==False:
            self.logger.error("folder is not a folder: "+folder)
            return False
        
        try:
            shutil.rmtree(folder)
            self.logger.success("folder deleted: "+folder)
            return True
        except Exception as e:
            self.logger.error('Failed to delete %s. Reason: %s' % (folder, e))
            return False