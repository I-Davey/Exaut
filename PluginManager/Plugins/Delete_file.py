from .__important.PluginInterface import PluginInterface
import os
import ctypes
import shutil

class Delete_file(PluginInterface):
    load = True
    types = {"file":3}

    type_types = {"source":["drag_drop_file", "Select file"], "__Name":"Delete file"}
    callname = "delfile"
    hooks_handler = ["log"]

    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True

    def main(self,file, Popups) -> bool:

        if os.path.exists(file)==False:
            self.logger.error("file path does not exist: "+file)
            return False
        
        if os.path.isfile(file)==False:
            self.logger.error("file path is not a file: "+file)
            return False

        try:
            os.remove(file)
            self.logger.success("file deleted: "+file)
        except Exception as e:
            self.logger.error(f"Problem deleting {file}: {e}")
            return False
        return True

