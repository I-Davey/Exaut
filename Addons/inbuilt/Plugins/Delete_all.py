from .__important.PluginInterface import PluginInterface
import os
import shutil

class Delete_all(PluginInterface):
    load = True
    types = {"source":0,"buttonname":11, "type_":2}

    type_types = {"folderpath":["drag_drop_folder", "Select Folder"], "__Name":"Delete all in Folder", "type_":["selection", "Select Delete Type", ["all items", "Non (.) Items"]]}
    callname = "delall", "delalldot"
    hooks_handler = ["log"]

    def load_self(self, hooks):
        self.logger = hooks["log"]
        return True

    def getTypeFunc(self, bseq, btn) -> dict:
        if "type_" in bseq:
            if bseq["type_"] == "all items":
                bseq["type"] = "delall"
            elif bseq["type_"] == "non (.) items":
                bseq["type"] = "delalldot"
        del bseq["type_"]
        return bseq, btn

    def main(self,source, bname, type_, ) -> bool:
        #if the last character is not a slash, add it
        
        if source[-1] != "/":
            source += "/"
        if os.path.exists(source)==True:
            folder = source
            #delete files but not folders in first level
            for filename in os.listdir(folder):
                #if firt item in name is a dot and type_ is delalldot, skip
                if filename[0] == "." and type_ == "delalldot":
                    continue
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    self.logger.error('Failed to delete %s. Reason: %s' % (file_path, e))
                    return False

        else:
            self.logger.error("Source path does not exist: "+source)
            return False

        return True

