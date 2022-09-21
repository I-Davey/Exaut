from .__important.PluginInterface import PluginInterface
import os
import shutil
class Rename_Item(PluginInterface):
    load = True
    #    types = {"folderpath":0,"filename":1,"type_":2,"source":3,"target":4,"databasepath":5,"databasename":6,"keypath":7,"keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}

    types = {"new_file_name":1,"old_file_name":3,"destination_folder":4}
    type_types = {"filename":["text", "New file name"],"source":["drag_drop_file", "Old filepath"], "target":["drag_drop_folder", "Destination folder"], "__Name":"Rename File"}

    callname = "rename"
    hooks_handler = ["log"]

    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True

    def main(self,new_file_name, old_file_path, destination_folder, ) -> bool:
        new_full = destination_folder + '/' + new_file_name
        try:
            shutil.move(old_file_path,os.path.join(destination_folder,new_file_name))
            self.logger.success(f"renamed {old_file_path} to {new_full}")
            return True
        except Exception as e:
            self.logger.error("Error renaming file")
            self.logger.error(e)
            return False
        