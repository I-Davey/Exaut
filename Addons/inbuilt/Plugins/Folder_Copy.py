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

    def main(self, type_,source, target, ) -> bool:
        self.logger.debug(f"copying {source} to {target}")
        source = source.replace("/", "\\")
        self.type_ = type_
        #check if dir exists
        if not os.path.exists(target):
            os.makedirs(target)

        self.copylist = []
        if type_ == "foldercopynew":
            #copy all files in folder from source to target that have a more recent date stamp then the old files
            for file in os.listdir(source):
                #if file is in target, check if it is newer
                if os.path.exists(os.path.join(target,file)) and not os.path.isdir(os.path.join(source,file)):
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
            return
        else:
            self.logger.success(f"Copied all files in {source} to {target} newer than the old files")
        return True
    
    def tryCopy(self, source, file, target):
        try:
            fulldir = os.path.join(source,file)
            if os.path.isdir(fulldir):
                #makedir
                if not os.path.exists(os.path.join(target,file)):
                    os.makedirs(os.path.join(target,file))
                for file in os.listdir(fulldir):
                    self.tryCopy(fulldir, file, os.path.join(target,os.path.basename(fulldir)))
            else:
                if os.path.exists(os.path.join(target,file)):
                    if self.type_ == "foldercopynew":
                        if os.path.getmtime(os.path.join(source,file)) > os.path.getmtime(os.path.join(target,file)):
                            shutil.copy2(os.path.join(source,file), target)
                            self.copylist.append(file)  
                    elif self.type_ == "foldercopyforce":
                        shutil.copy2(os.path.join(source,file), target)
                        self.copylist.append(file)
                    elif self.type_ == "foldercopynonx":
                        if not os.path.exists(os.path.join(target,file)):
                            #replace file
                            shutil.copy2(os.path.join(source,file), target)
                            self.copylist.append(file)
                else:
                    shutil.copy2(os.path.join(source,file), target)
                    self.copylist.append(file)
        except Exception as e:
            self.logger.error(f"could not copy {file}, check if it is open")
            self.logger.error(e)
            return False     



