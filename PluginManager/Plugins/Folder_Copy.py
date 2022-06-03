from .__important.PluginInterface import PluginInterface
import os
import shutil

class Folder_Copy(PluginInterface):
    load = True
    types = {"type_":2,"source":3, "target":4}
    callname = ("foldercopynew","foldercopyforce","foldercopynonx")
    hooks_handler = ["log"]
    type_types = {"source":{"type":"drag_drop_folder", "description":"please select the Source Folder"},"target":{"type":"drag_drop_folder", "description":"please select the Destination Folder"}, "type":["selection", "select Copy type", ["foldercopynew","foldercopyforce","foldercopynonx"]], "__Name":"Copy Folder"}


    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True

   

    # "keyfile":8,"runsequence":9,"treepath":10,"buttonname":11}

    def main(self, type_,source, target) -> bool:
        self.copylist = []
        if type_ == "foldercopynew":
            #copy all files in folder from source to target that have a more recent date stamp then the old files
            for file in os.listdir(source):
                #if file is in target, check if it is newer
                if os.path.exists(os.path.join(target,file)):
                    if os.path.getmtime(os.path.join(source,file)) > os.path.getmtime(os.path.join(target,file)):
                        self.tryCopy(source, file, target)
                else:
                    self.tryCopy(source, file, target)
        elif type_ == "foldercopyforce":
            #copy all files in folder from source to target
            for file in os.listdir(source):

                self.tryCopy(source, file, target)
        elif type_ == "foldercopynonx":
            #if file doesnt exist, copy it
            for file in os.listdir(source):
                if not os.path.exists(os.path.join(target,file)):
                    self.tryCopy(source, file, target)
        else:
            self.logger.error(f"type_: {type_} is not a valid type")
            return False
        self.logger.success(f"copied the following files: {self.copylist}")
        if type_ == "foldercopyforce":
            self.logger.success(f"Copied all files in {source} to {target} replacing all files")
        elif type_ == "foldercopynonx":
            self.logger.success(f"Copied all nonexistent files in {source} to {target}")
        else:
            self.logger.success(f"Copied all files in {source} to {target} newer than the old files")
            
    def tryCopy(self, source, file, target):
        try:
            fulldir = os.path.join(source,file)
            if os.path.isdir(fulldir):
                shutil.copytree(fulldir, os.path.join(target,file))
            else:
                shutil.copy(os.path.join(source,file),os.path.join(target,file))
            self.copylist.append(file)
        except:
            self.logger.error(f"could not copy {file}, check if it is open")
            return False
        return True