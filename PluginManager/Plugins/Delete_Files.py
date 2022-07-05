from .__important.PluginInterface import PluginInterface
import os
import ctypes

class Delete_Files(PluginInterface):
    load = True
    types = {"source":0,"buttonname":11}

    type_types = {"folderpath":["drag_drop_folder", "Select Folder"], "__Name":"Delete all files in Folder"}
    callname = "delfiles" 
    hooks_handler = ["log"]

    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True

    def main(self,source, bname, Popups) -> bool:
        #if the last character is not a slash, add it
        if source[-1] != "\\":
            source += "\\"
        if os.path.exists(source)==True:
            #delete files but not folders in first level
            for f in os.listdir(source):
                if os.path.isfile(source+"\\"+f)==True:
                    try:
                        os.remove(source+"\\"+f)
                        self.logger.success("file deleted: "+source+"\\"+f)
                        return True
                    except:
                        ctypes.windll.user32.MessageBoxW(0,"Problem deleting \""+source+"\\"+f+"\"?","Failed delete: "+bname,0)
                        return False

        else:
            self.logger.error("Source path does not exist: "+source)
            ctypes.windll.user32.MessageBoxW(0,"Problem removing "+source+"\\","Warning: cleardir: "+bname+"!", 0)
            return False
